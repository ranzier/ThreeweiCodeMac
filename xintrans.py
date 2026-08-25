import math
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

# 本模块负责“担架”部分的二维三视图转三维。主调用链为：
# tran2dto3d.tran2dto3d() -> work() -> trans()。
#
# 输入由两部分组成：
# 1. 每张担架图纸中的 coordinatesFront_data、coordinatesBottom_data、
#    coordinatesOverhead_data，记录杆件编号及其两个二维端点；
# 2. 塔身重建提供的连接点 data，每个连接点为 [节点编号, [X, Y, Z]]。
#
# 输出为节点字典列表和杆件字典列表。二类、三类节点的 Y/Z 字段可能不是
# 数值，而是形如 "1{节点编号}" 的引用编码；下游会依据该引用和对称类型
# 恢复完整坐标。因此这些字符串不能当作普通数字转换或重新格式化。
#
# 代码中“左/右”通常指二维图像 X 方向；三维空间中的担架侧别则由 pj 中
# 连接点 X 的正负决定。二维图像的 Y 轴向下，与三维 Z 轴方向并不相同。
from get_first_ganjian_id import detect_main_rods_enhanced
from stretcher_tower_connection import get_main_rod_connection_geometry
from zhiliu_near_front_reconstruction import (
    build_zhiliu_near_front_class1,
    build_zhiliu_near_front_second_class,
    build_zhiliu_near_projected_class1_frames,
    build_zhiliu_outer_front_class1,
    build_zhiliu_outer_front_second_class,
)


# 这些数值参与节点编号、吸附和对称性输出，提取为常量但不改变原值。
# 几何吸附阈值使用图纸像素单位。端点、交点和杆件匹配都依赖这个固定值；
# 即使不同图纸比例不同，也必须保持与历史输出一致。
INTERSECTION_THRESHOLD = 150

# 塔身连接点的扁平输入每四个为一个物理连接层，通常依次包含两侧的
# 上、下连接点。拆分后再按三维 X 正负形成两个 ConnectionGroup。
CONNECTION_GROUP_SIZE = 4

# 三类节点的第一编号段最多容纳 9 个节点，第 10 个起切换到溢出编号段。
THIRD_CLASS_PRIMARY_CAPACITY = 9

# 投影视图中成对节点的历史编号相差 2，例如尖点 10020/10022。
MIRRORED_NODE_ID_OFFSET = 2

# 输出协议中的节点分类：11 为一类真实坐标节点，12 为二/三类引用节点。
NODE_TYPE_CLASS_1 = 11
NODE_TYPE_CLASS_2 = 12

# 对称性编码由下游消费：0=无对称，1=左右，2=前后，4=四角对称。
SYMMETRY_NONE = 0
SYMMETRY_LEFT_RIGHT = 1
SYMMETRY_FRONT_BACK = 2
SYMMETRY_FOUR_CORNERS = 4

# 直流塔 03/05 的内端连接点来自 04/06 的外端，必须先处理靠塔内层，
# 再处理外层；该顺序不同于自然图号顺序。
ZHILIU_EXECUTION_ORDER = (1, 2, 4, 3, 6, 5)

# 下列类型别名仅描述运行时字典的预期结构，不改变原始输入和输出类型。
Point2D = Tuple[float, float]
CoordinateMap = Dict[Any, List[Point2D]]
NodeRecord = Dict[str, Any]
MemberRecord = Dict[str, Any]
ConnectionGroup = List[Any]


@dataclass(frozen=True)
class DrawingViews:
    """一个担架文件中原样读取的三视图二维杆件。"""

    # front=正视图，bottom=底视图，overhead=顶视图。不同主分支会交换
    # bottom/overhead 在 101~104 一类杆件编号体系中的角色。
    front: CoordinateMap
    bottom: CoordinateMap
    overhead: CoordinateMap


@dataclass
class ConversionState:
    """一次 ``work`` 调用内累计的节点和杆件。"""

    # 显式运行状态替代旧版模块级全局列表。列表顺序属于输出契约，所有
    # 生成函数均按图纸执行顺序 append，不在这里排序或去重。
    nodes: List[NodeRecord] = field(default_factory=list)
    members: List[MemberRecord] = field(default_factory=list)


@dataclass(frozen=True)
class StateCursor:
    """记录单张图开始处理时的运行状态位置。"""

    # ShangZi 02 只修改本张图新增记录的对称性，因此需要保存切片起点；
    # 其他部分塔型仍按旧规则修改整个运行级累计列表。
    node_start: int
    member_start: int


def load_drawing_views(file_path: str) -> DrawingViews:
    """按旧实现的 ``exec`` 语义读取三视图，不改变输入和异常行为。"""
    # 图纸 txt 本身是 Python 赋值文本，而不是 JSON。这里有意保留 exec：
    # 更换解析器可能改变可接受语法、异常类型或字典键的运行时类型。
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    namespace: Dict[str, Any] = {}
    exec(content, namespace)
    return DrawingViews(
        front=namespace.get('coordinatesFront_data', {}),
        bottom=namespace.get('coordinatesBottom_data', {}),
        overhead=namespace.get('coordinatesOverhead_data', {}),
    )


def count_txt_files(folder_path):
    """
    统计文件夹内 .txt 文件数量（不递归）
    """
    try:
        entries = os.listdir(folder_path)
    except FileNotFoundError:
        # 与旧流程一致：目录不存在等价于没有图纸，而不是向上抛错。
        return 0

    return sum(1 for name in entries if name.lower().endswith(".txt"))


def list_stretcher_drawings(folder_path):
    """Return ``(drawing_id, path)`` pairs for the actual drawing files.

    Drawing IDs come from numeric file stems (for example ``01.txt`` -> 1).
    They are sorted numerically, so missing IDs do not cause nonexistent files to
    be opened.  Ambiguous duplicate IDs such as ``01.txt`` and ``1.txt`` are
    rejected instead of being processed twice.
    """
    try:
        entries = os.listdir(folder_path)
    except FileNotFoundError:
        return []

    drawings = []
    paths_by_id = {}
    for name in entries:
        if not name.lower().endswith(".txt"):
            continue

        stem = os.path.splitext(name)[0]
        # drawing_id 同时参与 pj 定位和节点编号，因此只接受正整数文件名。
        if not stem.isdigit():
            raise ValueError(f"担架图纸文件名必须是数字编号: {name}")

        drawing_id = int(stem)
        if drawing_id <= 0:
            raise ValueError(f"担架图纸编号必须大于 0: {name}")
        if drawing_id in paths_by_id:
            # 01.txt 与 1.txt 会映射为同一 ID，必须拒绝以免重复生成。
            raise ValueError(
                f"担架图纸编号重复: {paths_by_id[drawing_id]} 和 {name}"
            )

        full_path = os.path.join(folder_path, name)
        paths_by_id[drawing_id] = name
        drawings.append((drawing_id, full_path))

    # 文件系统枚举顺序不稳定；自然图号顺序保证节点/杆件追加顺序稳定。
    return sorted(drawings, key=lambda item: item[0])


def align_connection_groups(pj, drawing_id, connection_index):
    """Expose the current ordered connection group at its drawing-ID slot.

    Most of the legacy conversion code addresses a connection group with
    ``drawing_id - 1``.  For sparse file IDs, ``connection_index`` identifies
    the corresponding group in the compact tower connection list.  A copy is
    returned so other groups and callers' data are never mutated.
    """
    if connection_index is None or connection_index == drawing_id - 1:
        return pj
    if connection_index < 0 or connection_index >= len(pj):
        raise IndexError(
            f"图纸 {drawing_id:02d} 缺少对应的塔身拼接点: "
            f"处理序号 {connection_index + 1}, 拼接点组数 {len(pj)}"
        )

    # 仅复制最外层列表：连接组内容仍保持原对象和原节点顺序。
    aligned = list(pj)
    target_index = drawing_id - 1
    if target_index >= len(aligned):
        # 稀疏图号（例如缺少 03）需要补空槽，使旧代码仍可用 drawing_id-1。
        aligned.extend([None] * (target_index + 1 - len(aligned)))
    aligned[target_index] = pj[connection_index]
    return aligned


def split_connection_groups(data1: Sequence[Any]) -> List[ConnectionGroup]:
    """按旧顺序将塔身连接点每四个一组，再按 X 正负拆成两侧。"""
    data = transform_data(data1)
    connection_groups: List[ConnectionGroup] = []
    for array in data:
        positive_group: ConnectionGroup = []
        negative_group: ConnectionGroup = []
        for point in array:
            # point[0] 是塔身节点编号，point[1] 是真实三维坐标。这里只按
            # 真实 X 划分塔身两侧，组内原始顺序保持不变。
            x_coord = point[1][0]
            if x_coord >= 0:
                positive_group.append(point)
            else:
                negative_group.append(point)
        # 每个物理层固定先放 X>=0 侧，再放 X<0 侧；下面的塔型映射依赖
        # 这一顺序按索引选择对应连接组。
        connection_groups.append(positive_group)
        connection_groups.append(negative_group)
    return connection_groups


def prepare_connection_groups(
    data1: Sequence[Any],
    file_path: str,
    drawing_id: int,
    drawing_type: str,
    connection_index: Optional[int],
    zhiliu_pj_overrides: Optional[Mapping[int, ConnectionGroup]],
) -> List[ConnectionGroup]:
    """构造并按图纸类型重排 ``pj``，保持旧索引和异常信息。"""
    # pj 的目标形状为 pj[图纸ID-1][上/下连接点][节点编号/XYZ]。具体塔型
    # 对连接层和左右侧的取法不同，因此先统一拆组，再执行固定索引映射。
    pj = split_connection_groups(data1)

    # 04/06 完成后会把各自外端连接点写回原始 pj 槽位，使随后执行的
    # 03/05 把这些点当作内端连接点；其他图纸类型不进入此分支。
    if drawing_type == "ZhiLiu" and zhiliu_pj_overrides:
        pj = list(pj)
        for pj_index, connection_group in zhiliu_pj_overrides.items():
            if pj_index < 0 or pj_index >= len(pj):
                raise IndexError(
                    f"直流塔复合担架连接点槽位不存在: pj[{pj_index}]"
                )
            pj[pj_index] = connection_group

    # ===== 担架索引修正 =====
    if drawing_type == "ShangZi":
        # 两张图分别取第一、第二物理层的正 X 侧。
        pj = [pj[i] for i in (0, 2)]
    elif drawing_type == "GanZi":
        # 7837/01 位于塔身左侧，7837/02 位于塔身右侧。
        pj = [pj[i] for i in (1, 2)]
    # J1,Z1
    elif drawing_type == "GuLou" and count_txt_files(os.path.dirname(file_path)) == 4:
        # 四担架鼓楼型每层只取正 X 侧，后续通过四角对称展开。
        pj = [pj[i] for i in (0, 2, 4, 6)]
    # J3,J4
    elif drawing_type == "GuLou" and count_txt_files(os.path.dirname(file_path)) == 8:
        if is_first_stretcher_apex_on_left(file_path, drawing_type):
            pj = [pj[i] for i in (1, 0, 3, 2, 5, 4, 7, 6)]
    elif drawing_type == "YangJiao":
        # 羊角形共有 01、02、04、06 四张担架图：01/02 共用第一组，
        # 04 使用第二组，06 使用第三组。四张图的连接端都位于左侧，
        # 而每个物理组在 pj 中按右侧、左侧依次存放。
        pj = [pj[i] for i in (0, 0, 2, 4)]
    elif drawing_type == "ZhiLiu":
        # 直流塔按 01、02、04、03、06、05 执行。
        # 03/05 不直接连接塔身，分别复用 04/06 所在侧的连接点组。
        # 此处数组仍按实际图号 01..06 排列，所以 03/04 共用 pj[3]，
        # 05/06 共用 pj[2]；外层担架执行前对应槽位会被上方覆盖。
        pj = [pj[i] for i in (1, 0, 3, 3, 2, 2)]

    # 最后再处理稀疏图号；前面的塔型映射仍使用其历史紧凑索引。
    return align_connection_groups(pj, drawing_id, connection_index)


def append_two_node_members(
    state: ConversionState,
    member_to_nodes: Mapping[Any, Sequence[Any]],
    symmetry_type: int,
) -> None:
    """按原遍历顺序追加恰好拥有两个端点的杆件。"""
    for member_id, node_list in member_to_nodes.items():
        # 少于两个节点表示杆件端点识别不完整，多于两个表示匹配有歧义；
        # 两者均沿用旧行为跳过，不尝试选最近节点或自动修复。
        if len(node_list) == 2:
            state.members.append({
                "member_id": str(member_id),
                "node1_id": node_list[0],
                "node2_id": node_list[1],
                "symmetry_type": symmetry_type,
            })


def build_intersection_nodes(
    state: ConversionState,
    real_points: Sequence[Mapping[str, Any]],
    node_id_factory: Callable[[int], str],
    node_record_factory: Optional[
        Callable[[str, Mapping[str, Any]], NodeRecord]
    ] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """复用已有端点，并按旧规则只为真正新建的节点递增序号。

    ``node_record_factory`` 为 ``None`` 时仍生成参与杆件匹配的二维节点，
    但不向最终节点表追加记录，对应各投影视图的对称引用节点。
    """
    nodes_2d: List[Dict[str, Any]] = []
    new_node_count = 0
    for item in real_points:
        # mark_endpoint_for_real_points 已把落在主杆端点附近的交点标为
        # 已有三维节点。复用它可避免连接点或尖点被重复写入节点表。
        endpoint_3d_id = item.get("endpoint_3d_id", -1)
        if endpoint_3d_id != -1:
            nodes_2d.append({
                "node_id": endpoint_3d_id,
                "point_2d": item["point_2d"],
            })
            continue

        # 编号序号只统计真正新增的节点；复用端点不会造成编号空洞。
        new_node_count += 1
        node_id = node_id_factory(new_node_count)
        nodes_2d.append({
            "node_id": node_id,
            "point_2d": item["point_2d"],
        })
        if node_record_factory is not None:
            # nodes_2d 用于二维端点匹配；最终 state.nodes 则保存三维输出。
            # 某些对称投影只需要前者，所以 factory 允许为空。
            state.nodes.append(node_record_factory(node_id, item))

    return nodes_2d, new_node_count


def remove_members_by_id(
    state: ConversionState, member_ids: Sequence[Any]
) -> None:
    """原地删除指定编号杆件，保留其余杆件的已有顺序。"""
    # 二/三类搜索可能把一类杆件也临时识别出来。最终需要先从运行级结果
    # 全量移除这些编号，再用已确定的真实端点重新添加正确的一类杆件。
    remove_ids = {str(member_id) for member_id in member_ids}
    state.members[:] = [
        member
        for member in state.members
        if member.get("member_id") not in remove_ids
    ]


def apply_symmetry_postprocessing(
    state: ConversionState,
    drawing_type: str,
    drawing_id: int,
    file_path: str,
    cursor: StateCursor,
) -> None:
    """应用旧版图纸类型后处理，并保留全量/本图切片的作用域。"""
    # 四担架鼓楼型只保存一个象限的数据，因此把累计结果中的前后对称提升
    # 为四角对称、无对称提升为左右对称。这里有意处理整个累计状态。
    if drawing_type == "GuLou" and count_txt_files(os.path.dirname(file_path)) == 4:
        for member in state.members:
            if member.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                member["symmetry_type"] = SYMMETRY_FOUR_CORNERS
            elif member.get("symmetry_type") == SYMMETRY_NONE:
                member["symmetry_type"] = SYMMETRY_LEFT_RIGHT
        for node in state.nodes:
            if node.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                node["symmetry_type"] = SYMMETRY_FOUR_CORNERS

    # 上字型只有 02 图需要扩大对称性，且不能回写 01 图已生成的记录。
    if drawing_type == "ShangZi" and drawing_id == 2:
        for member in state.members[cursor.member_start:]:
            if member.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                member["symmetry_type"] = SYMMETRY_FOUR_CORNERS
            elif member.get("symmetry_type") == SYMMETRY_NONE:
                member["symmetry_type"] = SYMMETRY_LEFT_RIGHT
        for node in state.nodes[cursor.node_start:]:
            if node.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                node["symmetry_type"] = SYMMETRY_FOUR_CORNERS

    # 干字型、羊角型沿用旧规则：每张图处理后都作用于累计结果。
    if drawing_type == "GanZi" or drawing_type == "YangJiao":
        for member in state.members:
            if member.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                member["symmetry_type"] = SYMMETRY_FOUR_CORNERS
            elif member.get("symmetry_type") == SYMMETRY_NONE:
                member["symmetry_type"] = SYMMETRY_LEFT_RIGHT
        for node in state.nodes:
            if node.get("symmetry_type") == SYMMETRY_FRONT_BACK:
                node["symmetry_type"] = SYMMETRY_FOUR_CORNERS

def dist_points(p1, p2):
    """计算点之间距离"""
    # 本函数用于二维像素坐标；三维真实坐标距离由 dist_z 单独计算。
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angle_between_lines(line1_pt1, line1_pt2, line2_pt1, line2_pt2):
    """
    计算两条直线的锐角夹角（0-90度）的简化版本

    参数:
        line1_pt1: 第一条直线的第一个端点 (x1, y1)
        line1_pt2: 第一条直线的第二个端点 (x2, y2)
        line2_pt1: 第二条直线的第一个端点 (x3, y3)
        line2_pt2: 第二条直线的第二个端点 (x4, y4)

    返回:
        两条直线的锐角夹角（单位：度，范围0-90度）
    """
    # 计算方向向量
    # 两条输入线均按“端点2-端点1”构造方向向量。方向正反不影响最终
    # 返回的锐角，因为最后会把钝角折算到 0~90 度。
    v1 = (line1_pt2[0] - line1_pt1[0], line1_pt2[1] - line1_pt1[1])
    v2 = (line2_pt2[0] - line2_pt1[0], line2_pt2[1] - line2_pt1[1])

    # 计算点积和模
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    # 检查零向量
    # 零长度杆件没有有效方向；历史行为是返回 0，而不是抛出异常。
    if mag1 == 0 or mag2 == 0:
        return 0

    # 计算夹角
    # 浮点误差可能让余弦略超出 [-1, 1]，先截断再调用 acos。
    cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    angle_deg = math.degrees(math.acos(cos_angle))

    # 返回锐角
    return min(angle_deg, 180 - angle_deg)

def dist_point_to_line(point, line_point1, line_point2):
    """
    计算点到直线的垂直距离（垂线段长度）

    参数:
        point: 点的坐标 (x, y)
        line_point1: 直线上的第一个点 (x1, y1)
        line_point2: 直线上的第二个点 (x2, y2)

    返回:
        点到直线的垂直距离
    """
    x, y = point
    x1, y1 = line_point1
    x2, y2 = line_point2

    # 这里计算的是到“无限延伸直线”的距离，不检查垂足是否在线段内。
    # 三类节点识别需要线段范围时，会在调用侧额外检查包围盒。
    # 如果直线是垂直的
    if x1 == x2:
        return abs(x - x1)

    # 如果直线是水平的
    if y1 == y2:
        return abs(y - y1)

    # 计算直线的一般式方程 Ax + By + C = 0
    # 一般位置使用直线标准式 Ax + By + C = 0。
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2

    # 计算点到直线的距离
    distance = abs(A * x + B * y + C) / math.sqrt(A ** 2 + B ** 2)

    return distance

def line_intersection(line1, line2):
    """
    计算两条直线的交点，返回交点坐标（x,y）

    参数:
        line1: 第一条直线，格式为 [(x1, y1), (x2, y2)]
        line2: 第二条直线，格式为 [(x3, y3), (x4, y4)]

    返回:
        交点坐标 (x, y)，如果直线平行则返回 None
    """
    # 提取坐标
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    # 计算分母
    # 按无限直线求交，不限制交点是否落在两条输入线段内部；调用方通过
    # 端点吸附、阈值和聚类筛选业务上有效的交点。
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # 如果分母为0，则直线平行或重合
    # 保留精确等于 0 的历史判断；不要在等价维护中改成容差判断。
    if denominator == 0:
        return None

    # 计算交点坐标
    x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
    y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

    return (x, y)

def dist_z(p1, p2):
    """
    计算三维点之间的欧氏距离
    """
    # 名称沿用历史代码，实际返回完整 XYZ 欧氏距离而非单独 Z 差值。
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

def transform_data(input_data):
    """
    将输入的节点数据按每4个一组进行分组

    示例:
        输入: [1, 2, 3, 4, 5, 6, 7, 8]
        输出: [[1, 2, 3, 4], [5, 6, 7, 8]]
    """
    # 将数据分成4组，每组4个节点
    # 最后一组不足四个时仍原样保留；后续按实际内容拆分，不在此补点。
    groups = []
    for i in range(0, len(input_data), CONNECTION_GROUP_SIZE):
        group = input_data[i:i + CONNECTION_GROUP_SIZE]
        groups.append(group)

    return groups

def cluster_points(points, threshold):
    """
    对点进行聚类，如果当前点与前一个点距离小于阈值，则合并到前一个聚类

    示例:
        输入: points=[(0, 0), (1, 1), (10, 10)], threshold=3
        输出: [(0.5, 0.5), (10, 10)]
    """
    # 这是顺序相关的相邻聚类，而不是全局最近邻聚类。调用方必须先按担架
    # 朝向排序，同一主杆上的交点才能沿杆件方向稳定合并。
    clusters = []

    for point in points:
        if not clusters:
            # 第一个点，直接作为第一个聚类
            clusters.append({
                "points": [point],
                "centroid": point
            })
        else:
            # 计算与最后一个聚类中心的距离
            # 只比较最后一个聚类中心，不回查更早的聚类。
            last_centroid = clusters[-1]["centroid"]
            distance = dist_points(point, last_centroid)

            if distance < threshold:
                # 合并到最后一个聚类
                clusters[-1]["points"].append(point)
                # 更新聚类中心为所有点的平均值
                # 聚类中心随新点更新为该簇全部点的算术平均值。
                all_points = clusters[-1]["points"]
                avg_x = sum(p[0] for p in all_points) / len(all_points)
                avg_y = sum(p[1] for p in all_points) / len(all_points)
                clusters[-1]["centroid"] = (avg_x, avg_y)
            else:
                # 创建新聚类
                clusters.append({
                    "points": [point],
                    "centroid": point
                })

    # 返回聚类中心点
    return [cluster["centroid"] for cluster in clusters]

def mark_endpoint_for_real_points(real_points,coordinates_data,rod_id,left_endpoint_3d_id,right_endpoint_3d_id,threshold):
    """
    判断交点是否为杆件端点之一，若是则用端点的三维节点编号标记
    """

    # 杆件的两个二维端点
    # left/right 是历史参数名；实际分别对应 coordinates_data[rod_id] 中
    # 第 0、1 个端点，并不保证几何上一定是左端和右端。调用方负责根据
    # 当前担架方向传入与这两个二维端点对应的三维节点编号。
    rod_p1, rod_p2 = coordinates_data[rod_id]

    for item in real_points:
        px, py = item["point_2d"]

        d1 = dist_points((px, py), rod_p1)
        d2 = dist_points((px, py), rod_p2)

        # 同时靠近两个端点时优先复用第 0 个端点，这是原有判定顺序。
        if d1 < threshold:
            item["endpoint_3d_id"] = left_endpoint_3d_id
        elif d2 < threshold:
            item["endpoint_3d_id"] = right_endpoint_3d_id
        else:
            # -1 是“需要新建节点”的哨兵值，由 build_intersection_nodes 识别。
            item["endpoint_3d_id"] = -1

    return real_points

def find_ganjian_by_nodes(node_list, coordinates_data, threshold):
    """
    根据节点列表，通过节点的二维坐标查找对应的杆件编号
    """
    # 返回方向为 node_id -> [member_id, ...]；generate_ganjian 随后会翻转
    # 为 member_id -> [node_id, ...]，以判断某根杆是否找齐两个端点。
    node_to_members = {}

    for node in node_list:
        node_id = node["node_id"]
        x0, y0 = node["point_2d"]

        matched_members = []

        # 按输入字典顺序扫描，匹配结果顺序会继续影响最终杆件输出顺序。
        for member_id, endpoints in coordinates_data.items():
            for (x, y) in endpoints:
                dist = math.hypot(x - x0, y - y0)
                if dist < threshold:
                    matched_members.append(member_id)
                    # 同一杆件只记录一次；任一端点命中即可。
                    break  # 一个端点命中即可

        node_to_members[node_id] = matched_members

    return node_to_members

def calc_jiandian_xyz(coordinates_data, drawing_id, pj,pj_view_index, rod_a_id, rod_b_id):
    """
    pj_view_index：0代表担架的上端点，1代表担架的下端点
    rod_a_id, rod_b_id：当前视图中两根一类杆件的实际编号
    生成尖点的真实XYZ的值
    输出：10020：（x,y,z）
    """
    # 两根一类杆件在二维视图中围成一个由基座向尖端收拢的梯形/三角形。
    # 两侧端点中点的距离 h 表示担架沿 X 方向的像素长度，a1/a2 表示
    # 两端的像素半宽；塔身连接点真实半宽 shiji 用于标定像素比例。
    start_01x = coordinates_data[rod_a_id][0][0]
    start_01y = coordinates_data[rod_a_id][0][1]
    start_02x = coordinates_data[rod_b_id][0][0]
    start_02y = coordinates_data[rod_b_id][0][1]
    end_01x = coordinates_data[rod_a_id][1][0]
    end_01y = coordinates_data[rod_a_id][1][1]
    end_02x = coordinates_data[rod_b_id][1][0]
    end_02y = coordinates_data[rod_b_id][1][1]
    midr = ((end_01x + end_02x) / 2, (end_01y + end_02y) / 2)  # 计算301和302两个右端点的中点
    midl = ((start_01x + start_02x) / 2, (start_01y + start_02y) / 2)  # 计算301和302两个左端点的中点
    h = dist_points(midl, midr)  # 计算左中点到右中点的距离
    p_01l = (start_01x, start_01y)
    a1 = dist_points(p_01l, midl)  # 起点侧一类杆件到起点中点的距离（起点侧像素半宽）
    p_01r = (end_01x, end_01y)
    a2 = dist_points(p_01r, midr)  # 终点侧一类杆件到终点中点的距离（终点侧像素半宽）
    # pj_view_index 的 0/1 分别选择当前担架的上/下连接组；[1][1]
    # 最终取得连接点真实 Y，历史变量名和注释称其为横向半宽。取绝对值
    # 是为了比例只表达长度，左右方向由后面的真实 X 正负单独处理。
    shiji = abs(pj[drawing_id - 1][pj_view_index][1][1])  # 计算担架3与塔身相交的下端点的三维x坐标的值，也就是实际值
    # 常规图纸：基座在起点侧，用起点侧半宽 a1 做像素→真实比例、终点侧半宽 a2 算 newy。
    # 特例（如 7837/01）：两根一类杆件在起点处收拢，a1==0 会除零；此时基座实为终点侧，
    # 回退用 a2 做比例、a1 算 newy。只有 a1==0 时才切换，其余图纸行为完全不变。
    if a1 != 0:
        base_half, apex_half = a1, a2
    else:
        base_half, apex_half = a2, a1
    # 此比例统一换算当前视图的像素长度和真实坐标长度。
    bili = shiji / base_half  # 计算实际值/像素值的比例
    # 生成尖点
    # 连接点位于塔身正 X 侧时尖点继续向 +X 延伸；负 X 侧则向 -X 延伸。
    if (pj[drawing_id - 1][pj_view_index][1][0] >= 0):  # if里面生成右边担架的尖点
        newx = pj[drawing_id - 1][pj_view_index][1][0] + h * bili
        newy = -apex_half * bili
        newz = pj[drawing_id - 1][pj_view_index][1][2]
    else:  # else生成左边担架的尖点
        newx = pj[drawing_id - 1][pj_view_index][1][0] - h * bili
        newy = -apex_half * bili
        newz = pj[drawing_id - 1][pj_view_index][1][2]
    return newx, newy, newz

def get_jiaodian_on_ganjian(coordinates_data, drawing_id, pj, rod_101_id, rod_103_id, yuzhi):
    """
    找二类杆件与一类杆件在一类杆件上的交点坐标

    输入：
    rod_101_id：101杆件的编号
    rod_103_id：103杆件的编号

    输出：
    node_101: [(10,20),(50,70),(90,100)] 表示101一类杆件上有三个交点（二类节点）
    node_103同理
    """
    # rod_101_id/rod_103_id 是当前视图中的两根一类参考杆，名称只是历史
    # 编号角色；在不同分支、不同视图里实际杆件 ID 会由调用方传入。
    rod_101_points = coordinates_data[rod_101_id]
    rod_103_points = coordinates_data[rod_103_id]
    intersections_101 = []
    intersections_103 = []

    # 遍历所有杆件
    # rod_id：杆件编号（如 301、302、303 …），points：该杆件的两个端点（二维）
    for rod_id, points in coordinates_data.items():
        if rod_id in [rod_101_id, rod_103_id]:  # 如果是301、303杆件就跳过
            continue
        # 只有一根候选杆的两个端点都靠近两根参考主杆中的任意一根，才把
        # 它视为跨接主杆的二类杆件，避免单端悬接杆过早进入本阶段。
        flag1 = 0  # flag1 用来统计该杆件有多少端点靠近参考杆件
        for i, point in enumerate(points):
            distance_to_101 = dist_point_to_line(point, rod_101_points[0], rod_101_points[1])
            distance_to_103 = dist_point_to_line(point, rod_103_points[0], rod_103_points[1])
            if (distance_to_103 < yuzhi or distance_to_101 < yuzhi):  # 如果端点只要靠近任意一根参考杆，flag1就加1
                flag1 += 1
        if flag1 == 2:  # 该杆件的两个端点都靠近参考杆件
            intersection_101 = line_intersection(points, rod_101_points)
            if intersection_101 is not None:
                intersections_101.append(intersection_101)  # 求杆件与 301 的交点坐标

            # 计算目标杆件与303杆件的交点坐标
            intersection_103 = line_intersection(points, rod_103_points)
            if intersection_103 is not None:
                intersections_103.append(intersection_103)

    # 对在301杆件上的交点这个数组的元素进行排序，按照二维坐标的x轴从小到大进行排序
    # 排序方向跟随担架所在塔身侧，使列表始终从连接端向尖端（或旧流程
    # 约定的对应方向）排列；cluster_points 依赖这个顺序消除近邻重复点。
    if (pj[drawing_id - 1][1][1][0] > 0):
        intersections_101.sort(key=lambda point: point[0])
    else:
        intersections_101.sort(key=lambda point: point[0], reverse=True)
    node_101 = cluster_points(intersections_101, threshold=yuzhi)  # 对杆件上的交点进行聚类得到node_101[]这个聚类后的交点数组
    if (pj[drawing_id - 1][1][1][0] > 0):
        intersections_103.sort(key=lambda point: point[0])
    else:
        intersections_103.sort(key=lambda point: point[0], reverse=True)
    node_103 = cluster_points(intersections_103, threshold=yuzhi)

    return node_101,node_103

def get_jiaodian_on_ganjian_by_missing_members(
    coordinates_data,
    missing_members,
    existing_member_ids,
    drawing_id,
    rod_101_id, 
    rod_103_id,
    pj,
    yuzhi,
):
    """
    找三类杆件与一类杆件、二类杆件上的交点坐标

    """

    # 结果按“已存在的宿主杆件 ID”分组。每个点来自尚未生成的三类杆件
    # 端点，表示需要在该宿主杆上补一个三类连接节点。
    intersections_existing = defaultdict(list)

    def is_point_on_segment(point, seg_p1, seg_p2, threshold):
        # 先判断到无限直线的垂距，再用扩展 threshold 的包围盒限制在线段
        # 范围附近；两项同时成立才认为端点吸附在宿主杆件上。
        if dist_point_to_line(point, seg_p1, seg_p2) >= threshold:
            return False
        min_x = min(seg_p1[0], seg_p2[0]) - threshold
        max_x = max(seg_p1[0], seg_p2[0]) + threshold
        min_y = min(seg_p1[1], seg_p2[1]) - threshold
        max_y = max(seg_p1[1], seg_p2[1]) + threshold
        return min_x <= point[0] <= max_x and min_y <= point[1] <= max_y

    # 预先整理二类杆件编号，并建立字符串->原始键的映射，避免类型不一致
    # existing_member_ids 是当前视图已经生成的二类杆；两根一类主杆也可
    # 作为三类节点宿主，因此一并加入候选集合。
    second_class_ids = {
        str(m_id)
        for m_id in (existing_member_ids or [])
    }
    second_class_ids.update({str(rod_101_id), str(rod_103_id)})
    # 输出杆件编号统一为字符串，但二维输入键可能是 int 或 str。映射回
    # 原始键后再索引 coordinates_data，避免静默漏匹配。
    second_class_key_map = {str(m_id): m_id for m_id in (coordinates_data or {}).keys()}

    # 遍历三类杆件的二维端点，若端点落在二类杆件上则记录
    for rod_id, points in (missing_members or {}).items():
        for point in points:
            for second_id in second_class_ids:
                key = second_class_key_map.get(second_id)
                if key is None:
                    continue
                second_points = coordinates_data.get(key)
                if not second_points:
                    continue
                if is_point_on_segment(point, second_points[0], second_points[1], yuzhi):
                    intersections_existing[str(second_id)].append(point)


    node_existing = {}
    # 对每个二类杆件的交点排序+聚类
    for second_id, points in intersections_existing.items():
        # 保持排序方向与当前担架方向一致
        if pj[drawing_id - 1][1][1][0] > 0:
            points.sort(key=lambda point: point[0])
        else:
            points.sort(key=lambda point: point[0], reverse=True)
        # 聚类以去除近邻重复交点
        node_existing[second_id] = cluster_points(points, threshold=yuzhi)

    # 去除与二类杆件端点距离过近的交点
    # 与已有宿主杆端点重合的点应直接复用既有二类/一类节点，不在三类
    # 阶段重复创建；因此聚类后统一剔除靠近任何宿主端点的点。
    endpoint_points = []
    endpoint_ids = set(second_class_ids)
    for member_id in endpoint_ids:
        key = second_class_key_map.get(member_id)
        if key is None:
            continue
        endpoints = coordinates_data.get(key)
        if not endpoints:
            continue
        endpoint_points.append(endpoints[0])
        endpoint_points.append(endpoints[1])

    def is_near_any_endpoint(point, endpoints, threshold):
        return any(dist_points(point, endpoint) < threshold for endpoint in endpoints)

    for member_id, points in list(node_existing.items()):
        node_existing[member_id] = [
            point for point in points
            if not is_near_any_endpoint(point, endpoint_points, yuzhi)
        ]

    return node_existing


def get_real_x_of_jiaodian(coordinates_data, drawing_id, filtered, newx, pj, rod_id, judge_pj_index,value_pj_index):
    """
    计算一类杆件上交点的真实x坐标
    输出：[{"point_2d": (10,20), "x_3d": 123.456}, {...}, ...] 表示每个交点的二维坐标和对应的真实x坐标
    """

    # 得到301杆件的两个端点的二维X坐标
    # 沿二维主杆 X 坐标做线性插值。该历史算法假设主杆两端二维 X 不同；
    # 零跨度时自然产生原有除零异常，不在此修正。
    min_2d_x = coordinates_data[rod_id][0][0]
    max_2d_x = coordinates_data[rod_id][1][0]

    # 得到301 杆件在三维中的两端的 X 坐标
    # judge_pj_index 只判断担架位于塔身哪一侧；value_pj_index 决定本杆
    # 使用上连接点还是真实下连接点作为插值端点。二者不能合并。
    if (pj[drawing_id - 1][judge_pj_index][1][0] >= 0):
        min_3d_x = pj[drawing_id - 1][value_pj_index][1][0]  # 这个是301杆件与塔身相交的端点的三维X坐标
        max_3d_x = newx  # 这个是301杆件尖点的三维X坐标
    else:
        min_3d_x = newx
        max_3d_x = pj[drawing_id - 1][value_pj_index][1][0]

    real = []  # 计算比例并转换为真实x坐标

    for point in filtered:
        # 计算点在二维杆件上的x坐标比例
        x_ratio = (point[0] - min_2d_x) / (max_2d_x - min_2d_x)
        # 根据比例计算真实x坐标
        real_x = min_3d_x + x_ratio * (max_3d_x - min_3d_x)
        real.append({
            "point_2d": point,  # (x2d, y2d)
            "x_3d": real_x  # 对应的真实x
        })

    return real


def get_real_x_between_xyz_endpoints(
    coordinates_data, filtered, rod_id, endpoint_xyz
):
    """按投影主杆两端的真实 XYZ，为杆上二维交点插值真实 X。"""
    # 直流塔专用骨架已能提供主杆两端完整真实 XYZ，因此用二维向量投影
    # 比例插值，比只使用二维 X 更适合倾斜主杆。函数仍只输出真实 X，
    # Y/Z 继续由节点引用编码表达。
    point1, point2 = coordinates_data[rod_id]
    vx = point2[0] - point1[0]
    vy = point2[1] - point1[1]
    length_squared = vx * vx + vy * vy
    if math.isclose(length_squared, 0.0, abs_tol=1e-9):
        raise ValueError(f"投影主杆 {rod_id} 是零长度杆件")

    start_x = float(endpoint_xyz[0][0])
    end_x = float(endpoint_xyz[1][0])
    real = []
    for point in filtered:
        ratio = (
            (point[0] - point1[0]) * vx
            + (point[1] - point1[1]) * vy
        ) / length_squared
        # 将因识别阈值落到端点外侧的投影截断到真实杆件范围。
        ratio = max(0.0, min(1.0, ratio))
        real.append({
            "point_2d": point,
            "x_3d": start_x + ratio * (end_x - start_x),
        })
    return real

def get_real_x_of_missing_nodes(
    coordinates_data,
    drawing_id,
    node_existing,
    newx,
    pj,
    rod_id,
    judge_pj_index,
    value_pj_index,
):
    """
    计算三类节点的真实x坐标
    输出：{member_id: [{"point_2d": (x,y), "x_3d": v}, ...], ...}
    """

    def calc_real_points(points):
        # 所有三类交点都借用 rod_id 这根一类参考杆的二维/三维端点范围，
        # 即使字典键是二类宿主杆件 ID，也不切换插值基准。
        # 统一使用 rod_id 对应的二维端点范围
        if rod_id not in coordinates_data:
            return []

        min_2d_x = coordinates_data[rod_id][0][0]
        max_2d_x = coordinates_data[rod_id][1][0]

        # 根据担架方向确定对应的三维 x 取值范围
        if pj[drawing_id - 1][judge_pj_index][1][0] > 0:
            min_3d_x = pj[drawing_id - 1][value_pj_index][1][0]
            max_3d_x = newx
        else:
            min_3d_x = newx
            max_3d_x = pj[drawing_id - 1][value_pj_index][1][0]

        real_points = []
        for point in points:
            # 按二维 x 比例映射到三维 x
            x_ratio = (point[0] - min_2d_x) / (max_2d_x - min_2d_x)
            real_x = min_3d_x + x_ratio * (max_3d_x - min_3d_x)
            real_points.append({
                "point_2d": point,
                "x_3d": real_x,
            })
        return real_points

    # 输入为 dict 时，统一按 rod_id 的范围计算
    # node_existing 通常为 宿主member_id -> [二维交点]；同时保留接受单个
    # 点列表的旧接口，两种形态最终都返回带 point_2d/x_3d 的记录。
    if isinstance(node_existing, dict):
        real_existing = {}
        for member_id, points in node_existing.items():
            real_existing[member_id] = calc_real_points(points)
        return real_existing

    # 否则按单杆件的点列表计算
    return calc_real_points(node_existing)

def generate_ganjian(coordinates_data, node_101_nodes, node_103_nodes,yuzhi):
    """
    根据节点从二维坐标信息中找到杆件编号
    """
    # 先分别计算两根参考主杆上的节点能命中哪些二维杆件，再合并并翻转
    # 映射。正常跨接杆最终应获得来自两侧主杆的两个节点。
    ganjian_nodes_table_101 = find_ganjian_by_nodes(node_101_nodes, coordinates_data,yuzhi)
    ganjian_nodes_table_103 = find_ganjian_by_nodes(node_103_nodes, coordinates_data,yuzhi)
    all_node_member_map = {}
    all_node_member_map.update(ganjian_nodes_table_101)
    # node_id 若在两组中重复，后一次 update 沿用历史覆盖行为。
    all_node_member_map.update(ganjian_nodes_table_103)
    member_to_nodes = defaultdict(list)
    for node_id, member_list in all_node_member_map.items():
        for member_id in member_list:
            member_to_nodes[member_id].append(node_id)
    return member_to_nodes


def find_missing_members(ganjian, coordinates_data, main_rod_ids):
    """
    找出还未生成的三类杆件的杆件编号ID与其对应的二维坐标数据
    通过对比 ganjian 和 当前视图的坐标数据，找出 ganjian 中缺失的 member_id 及其二维坐标

    参数:
        ganjian: 已生成的杆件列表，每个字典包含 'member_id'
        coordinates_data: 当前视图的坐标数据，键为 member_id，值为两端点的二维坐标数据
        main_rod_ids: 一类杆件的 ID 列表（可选），如包含则从缺失结果中剔除

    返回:
        missing_members: 字典格式，键为缺失的 member_id，值为其对应的二维坐标点列表
        existing_member_ids: 已生成且存在于 coordinates_data 的 member_id 列表（字符串）
    """
    # 收集 ganjian 中已有的 member_id（统一转换为字符串以方便比对）
    # 只比较编号，不比较端点。统一转字符串以兼容二维输入的整数键和输出
    # 杆件的字符串 member_id。
    existing_members = {str(item.get("member_id")) for item in ganjian if "member_id" in item}
    coordinates_member_ids = {str(m_id) for m_id in (coordinates_data or {}).keys()}
    # 排序使后续宿主集合构造保持历史确定性；这是字典字符串顺序。
    existing_member_ids = sorted(existing_members & coordinates_member_ids)

    # 对比查找并收集缺失的 member_id 及其二维坐标
    main_rod_id_set = {str(m_id) for m_id in (main_rod_ids or [])}
    missing_members = {}
    if coordinates_data:
        for m_id, points in coordinates_data.items():
            m_id_str = str(m_id)
            if m_id_str not in existing_members and m_id_str not in main_rod_id_set:
                missing_members[m_id_str] = points

    return missing_members, existing_member_ids


def generate_third_class_nodes_and_members(
    state: ConversionState,
    coordinates_data,
    drawing_id,
    newx,
    pj,
    view_member_to_nodes,
    rod_a_id,
    rod_b_id,
    judge_pj_index,
    value_pj_index,
    main_rod_endpoints,
    id_prefix,
    node_id_groups,
    symmetry_type,
    yuzhi,
    extra_main_rod_ids=None,
    seed_nodes_2d=None,
    real_x_endpoint_xyz=None,
):
    """为单个视图生成尚未覆盖的三类节点和三类杆件。

    保持原底视图三类处理算法不变；视图间不同的一类杆件、拼接点映射和
    节点编号段由调用方传入。
    """
    # state 是一次 work() 的运行级结果；这里用短变量名只是兼容原业务
    # 代码的表述，二者仍指向同一列表，不会创建局部结果副本。
    jiedian = state.nodes
    ganjian = state.members
    # 仅使用当前视图刚生成的二类杆件。累计状态会包含其他视图和
    # 其他担架的数据，直接参与比对会让相同杆件编号互相干扰。
    # view_member_to_nodes 来自本视图二类杆件识别，形如
    # {member_id: [node1_id, node2_id]}。只把端点完整的杆件作为已生成项，
    # 其余杆件仍会进入 missing_members，交由三类阶段尝试补齐。
    view_members = [
        {
            "member_id": str(member_id),
            "node1_id": node_list[0],
            "node2_id": node_list[1],
        }
        for member_id, node_list in view_member_to_nodes.items()
        if len(node_list) == 2
    ]
    # 一类主杆由 main_rod_ids 显式排除；直流塔三主杆骨架可通过
    # extra_main_rod_ids 再排除专用副主杆，避免把骨架误判为三类杆。
    missing_members, existing_member_ids = find_missing_members(
        view_members,
        coordinates_data,
        [rod_a_id, rod_b_id, *(extra_main_rod_ids or [])],
    )

    # 找出每根缺失杆件的二维端点落在哪些已经存在的一/二类宿主杆上。
    # 返回键是宿主杆件 ID，值是需要在该宿主杆上新增的二维连接点。
    node_existing = get_jiaodian_on_ganjian_by_missing_members(
        coordinates_data,
        missing_members,
        existing_member_ids,
        drawing_id,
        rod_a_id,
        rod_b_id,
        pj,
        yuzhi,
    )

    # 普通图纸以 pj 连接点和尖点 newx 标定真实 X；直流塔专用投影框架
    # 已知一类主杆两端完整 XYZ，则改用二维向量投影比例插值真实 X。
    if real_x_endpoint_xyz is not None:
        real_node_existing = {
            member_id: get_real_x_between_xyz_endpoints(
                coordinates_data, points, rod_a_id, real_x_endpoint_xyz
            )
            for member_id, points in node_existing.items()
        }
    else:
        real_node_existing = get_real_x_of_missing_nodes(
            coordinates_data,
            drawing_id,
            node_existing,
            newx,
            pj,
            rod_a_id,
            judge_pj_index,
            value_pj_index,
        )

    # 建立“宿主杆件 -> 已有三维端点节点”映射。新三类节点的 Y/Z 字段
    # 将分别引用这两个端点，使下游能够沿宿主杆恢复其余坐标分量。
    member_endpoints = {}
    for member in view_members:
        member_id = str(member.get("member_id"))
        # 同一 member_id 若重复出现，保留最先生成的端点关系。
        if member_id not in member_endpoints:
            member_endpoints[member_id] = (
                member.get("node1_id"),
                member.get("node2_id"),
            )
    # 一类主杆端点由调用方提供，并覆盖同编号的二类临时映射。
    member_endpoints.update({
        str(member_id): endpoints
        for member_id, endpoints in main_rod_endpoints.items()
    })

    # node_id_groups 由视图决定，例如正视图使用 (691, 791)。前 9 个节点
    # 使用 first_group，第 10 个起重新从 1 编入 overflow_group。
    first_group, overflow_group = node_id_groups
    new_node_cnt = 0
    real_node_existing_2d_nodes = []
    for member_id, points in (real_node_existing or {}).items():
        endpoints = member_endpoints.get(str(member_id))
        # 没有可靠宿主端点时无法生成引用坐标，沿用旧行为直接跳过。
        if not endpoints:
            continue
        node1_id, node2_id = endpoints
        for item in points:
            new_node_cnt += 1
            if new_node_cnt > THIRD_CLASS_PRIMARY_CAPACITY:
                node_seq = new_node_cnt - THIRD_CLASS_PRIMARY_CAPACITY
                node_id = f"{id_prefix}{overflow_group}{node_seq}0"
            else:
                node_id = f"{id_prefix}{first_group}{new_node_cnt}0"
            # X 是本节点唯一直接计算的真实坐标；Y/Z 以 "1+节点编号"
            # 分别引用宿主杆的两个端点，这是输出协议而不是十进制数字。
            jiedian.append({
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": symmetry_type,
                "X": item["x_3d"],
                "Y": f"1{node1_id}",
                "Z": f"1{node2_id}",
            })
            real_node_existing_2d_nodes.append({
                "node_id": node_id,
                "point_2d": item.get("point_2d"),
            })

    # 04/06 底视图的末端斜杆会同时连接“本轮新生成的三类节点”和
    # “前面已经生成的二类节点”。可选种子让两类节点共同参与杆件组装；
    # 旧图纸不传该参数，行为保持不变。
    nodes_for_member_matching = list(real_node_existing_2d_nodes)
    nodes_for_member_matching.extend(seed_nodes_2d or [])
    # 用新三类节点（以及可选的已有种子节点）重新匹配二维杆件端点，
    # 从 node->members 再翻转为 member->nodes。
    node_to_members = find_ganjian_by_nodes(
        nodes_for_member_matching, coordinates_data, yuzhi
    )
    member_to_nodes = defaultdict(list)
    for node_id, member_list in node_to_members.items():
        for member_id in member_list:
            member_to_nodes[member_id].append(node_id)

    # 一个二维节点可能因阈值重复命中同一杆件，先按出现顺序去重；只为
    # 本轮确属 missing 的杆件且恰好找齐两个唯一端点时输出三类杆件。
    missing_member_ids = {str(member_id) for member_id in missing_members}
    for member_id, node_list in member_to_nodes.items():
        unique_node_list = list(dict.fromkeys(node_list))
        if str(member_id) in missing_member_ids and len(unique_node_list) == 2:
            ganjian.append({
                "member_id": str(member_id),
                "node1_id": unique_node_list[0],
                "node2_id": unique_node_list[1],
                "symmetry_type": symmetry_type,
            })


def detect_main_rods_by_type(coordinates_data, drawing_type):
    """统一使用通用规则识别一类杆件；保留 drawing_type 参数以兼容现有调用。"""
    # drawing_type 目前不参与算法，但保留在封装层，避免调用方接口变化，
    # 也为未来确有图型差异时提供单一扩展点。
    return detect_main_rods_enhanced(coordinates_data)


def is_diagonal_rod_above_horizontal_rod(coordinates_data, rod_a_id, rod_b_id):
    """根据正视图两根一类杆件的上下关系判断担架转换分支。"""
    # 本判断决定 trans() 的两个大分支：它不仅影响正视图上下杆顺序，
    # 还决定底视图和顶视图谁承担 101/102、103/104 的角色。
    rods = []
    for rod_id in (rod_a_id, rod_b_id):
        points = coordinates_data.get(rod_id)
        if not points or len(points) != 2:
            raise ValueError(f"正视图一类杆件 {rod_id} 缺少两个有效端点")

        p1, p2 = points
        length = dist_points(p1, p2)
        if length == 0:
            raise ValueError(f"正视图一类杆件 {rod_id} 是零长度杆件")

        # 相对杆长的竖向变化越小，越接近水平杆。
        # 用竖向变化/杆长归一化，避免仅因两根杆像素长度不同而误分类。
        # 比值较小者视为水平杆，较大者视为斜杆。
        vertical_ratio = abs(p2[1] - p1[1]) / length
        rods.append((vertical_ratio, rod_id, points))

    rods.sort(key=lambda item: item[0])
    if math.isclose(rods[0][0], rods[1][0], abs_tol=1e-9):
        raise ValueError(
            f"正视图一类杆件 {rod_a_id}、{rod_b_id} 无法区分水平杆和斜杆"
        )

    _, horizontal_id, horizontal_points = rods[0]
    _, diagonal_id, diagonal_points = rods[1]
    # 只在两根杆共同覆盖的二维 X 区间比较高度，避免外推到杆件范围之外。
    overlap_left = max(
        min(point[0] for point in horizontal_points),
        min(point[0] for point in diagonal_points),
    )
    overlap_right = min(
        max(point[0] for point in horizontal_points),
        max(point[0] for point in diagonal_points),
    )
    if overlap_left >= overlap_right:
        raise ValueError(
            f"正视图水平杆 {horizontal_id} 与斜杆 {diagonal_id} 没有有效的公共 X 区间"
        )

    # 取公共区间中点，避开端点附近的吸附噪声。
    compare_x = (overlap_left + overlap_right) / 2

    def y_at_x(points, x):
        (x1, y1), (x2, y2) = points
        if x1 == x2:
            raise ValueError("正视图一类杆件为竖直杆，无法按 X 坐标比较上下位置")
        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

    # 图像坐标的 Y 轴向下，斜杆 Y 更小表示它位于水平杆上方。
    horizontal_y = y_at_x(horizontal_points, compare_x)
    diagonal_y = y_at_x(diagonal_points, compare_x)
    return diagonal_y < horizontal_y


def calc_yangjiao_01_apex_z(
    coordinates_front_data,
    connection_group,
    rod_a_id,
    rod_b_id,
):
    """根据正视图倾角计算羊角形 01 号担架尖点的真实 Z。

    connection_group 按通用流程约定为 [上连接点, 下连接点]。先用两个
    连接端在正视图中的像素 Y 与对应三维 Z 标定比例，再把两根主杆
    对侧端点的平均 Y 外推为尖点 Z。
    """
    # 通用尖点算法主要从平面投影视图恢复 X/Y，羊角 01 的尖点还具有
    # 正视图可见的倾角，因此需用上下塔身连接点额外标定真实 Z。
    if not connection_group or len(connection_group) < 2:
        raise ValueError("羊角形 01 号担架缺少上下连接点，无法计算尖点 Z")

    try:
        upper_xyz = connection_group[0][1]
        lower_xyz = connection_group[1][1]
        upper_z = float(upper_xyz[2])
        lower_z = float(lower_xyz[2])
    except (IndexError, TypeError, ValueError) as exc:
        raise ValueError("羊角形 01 号担架上下连接点坐标无效") from exc

    # 同时识别两根主杆连接塔身的一侧及其上下角色，避免依赖输入杆件顺序。
    connection_side, upper_rod_id, lower_rod_id = get_main_rod_connection_geometry(
        coordinates_front_data,
        rod_a_id,
        rod_b_id,
    )

    def endpoint_on_side(rod_id, side):
        points = coordinates_front_data.get(rod_id)
        if not points or len(points) != 2:
            raise ValueError(f"羊角形 01 号正视图一类杆件 {rod_id} 端点无效")
        # 二维 X 最小/最大端点分别代表图像左/右侧。
        selector = min if side == "left" else max
        return selector(points, key=lambda point: point[0])

    # 尖点位于塔身连接端的对侧；两根主杆对侧端点平均 Y 作为尖点像素高度。
    apex_side = "right" if connection_side == "left" else "left"
    upper_connection_2d = endpoint_on_side(upper_rod_id, connection_side)
    lower_connection_2d = endpoint_on_side(lower_rod_id, connection_side)
    upper_apex_2d = endpoint_on_side(upper_rod_id, apex_side)
    lower_apex_2d = endpoint_on_side(lower_rod_id, apex_side)

    connection_y_span = lower_connection_2d[1] - upper_connection_2d[1]
    if math.isclose(connection_y_span, 0.0, abs_tol=1e-9):
        raise ValueError("羊角形 01 号正视图上下连接端高度相同，无法标定尖点 Z")

    apex_y = (upper_apex_2d[1] + lower_apex_2d[1]) / 2.0
    # 用连接端二维 Y 差与真实 Z 差建立线性比例，再外推至尖点 Y。
    z_per_pixel = (lower_z - upper_z) / connection_y_span
    return upper_z + (apex_y - upper_connection_2d[1]) * z_per_pixel


def is_first_stretcher_apex_on_left(file_path, drawing_type):
    """判断 01 号担架的尖点是否位于两根一类杆件左端。从而区分J1和J3J4"""
    # 八担架鼓楼型的 pj 排列取决于整套图纸的朝向；统一读取 01 图作为
    # 基准，而不是使用当前可能为 02~08 的 file_path。
    first_file_path = os.path.join(os.path.dirname(file_path), "01.txt")
    with open(first_file_path, 'r', encoding='utf-8') as f:
        first_content = f.read()
    first_namespace = {}
    exec(first_content, first_namespace)
    first_front = first_namespace.get('coordinatesFront_data', {})
    first_front_a, first_front_b = detect_main_rods_by_type(first_front, drawing_type)
    # 两根主杆在左侧收拢到同一点（像素距离 <=1）表示尖点在左侧。
    first_left_a = min(first_front[first_front_a], key=lambda point: point[0])
    first_left_b = min(first_front[first_front_b], key=lambda point: point[0])
    return dist_points(first_left_a, first_left_b) <= 1





def trans(
    file_path,
    drawing_id,
    data1,
    drawing_type,
    id_offset=False,
    connection_index=None,
    zhiliu_pj_overrides=None,
    state=None,
):
    """
    参数:
        file_path: 包含三视图坐标数据的文件路径
        drawing_id: 从文件名取得的实际图纸编号，用于生成节点/杆件编号
        connection_index: 当前图纸在排序后文件列表中的位置（从 0 开始），
            用于读取按处理顺序排列的塔身拼接点；省略时保持旧的连续编号行为
        zhiliu_pj_overrides: 直流塔复合担架生成的原始 pj 槽位覆盖值；
            04 写入槽位 3 供 03 使用，06 写入槽位 2 供 05 使用
        state: ``work`` 创建的一次转换运行状态
    """
    # trans() 处理单张担架，但所有结果追加到 work() 提供的运行级 state。
    # 允许 state=None 仅用于兼容直接调用；这种情况下结果存在新建状态中，
    # 本函数仍按原接口只返回直流塔外端连接组。生产入口应始终调用 work()。
    if state is None:
        state = ConversionState()
    jiedian = state.nodes
    ganjian = state.members
    # 记录本次担架处理前状态列表的长度，用于只对本担架新增的节点/杆件做后处理
    # 游标必须在任何特殊补点之前记录，确保 ShangZi 02 的后处理切片覆盖
    # 本图产生的全部节点和杆件，同时不影响此前图纸。
    jiedian_start = len(jiedian)
    ganjian_start = len(ganjian)
    # 输入文件只负责二维几何；塔身连接点由 data1 经 prepare_connection_groups
    # 转成 pj。两类输入在后续插值和节点引用阶段合流。
    views = load_drawing_views(file_path)
    coordinatesFront_data = views.front
    coordinatesBottom_data = views.bottom
    coordinatesOverhead_data = views.overhead

    # 所有视图共享同一历史吸附阈值，保证交点、端点和杆件匹配口径一致。
    yuzhi = INTERSECTION_THRESHOLD   #阈值
    pj = prepare_connection_groups(
        data1, file_path, drawing_id, drawing_type, connection_index,
        zhiliu_pj_overrides,
    )


    # 担架编号偏移：担架和塔身合并的图纸（如 T7833/7837，塔身目录下存在 01.txt）担架从 3 号起，
    # 需 +2（1→3, 2→4），保证担架和塔身的节点编号生成不会重复。是否偏移由调用方 work() 传入。
    # 节点编号以处理后的担架编号为前缀。jiandian_id 对应形如 10010 的
    # 基址，常用 +20 为真实尖点、+22 为其镜像/对称尖点；191/291/391
    # 分别用于正视图、第一投影视图、第二投影视图的二类节点编号段。
    id_prefix = drawing_id + 2 if id_offset else drawing_id
    jiandian_id = (id_prefix * 100 + 1) * 100

    # 羊角形 01 号担架从塔身取得的 index 0 是下连接点；上连接点位于
    # 塔身中心线，与下连接点组成 45 度等腰直角三角形。后续通用逻辑
    # 约定 index 0/1 分别为上/下连接点，因此补点后需调整二者顺序。
    if drawing_type == "YangJiao" and drawing_id == 1:
        connection_group = pj[drawing_id - 1]
        if not connection_group or len(connection_group) < 2:
            raise ValueError("羊角形 01 号担架缺少塔身下连接点")

        lower_connection = connection_group[0]
        lower_xyz = lower_connection[1]
        if not lower_xyz or len(lower_xyz) != 3:
            raise ValueError("羊角形 01 号担架的塔身下连接点坐标无效")

        # 由下连接点构造塔身中心线上的上连接点：X 固定为 0，Y 不变，
        # Z 向上移动 |lower_x|，对应 45 度等腰直角几何关系。
        lower_x, lower_y, lower_z = map(float, lower_xyz)
        upper_node_id = str(jiandian_id + 10)
        upper_xyz = [0.0, lower_y, lower_z - abs(lower_x)]
        connection_group[1] = lower_connection
        connection_group[0] = [upper_node_id, upper_xyz]
        jiedian.append({
            "node_id": upper_node_id,
            "node_type": NODE_TYPE_CLASS_1,
            "symmetry_type": SYMMETRY_FRONT_BACK,
            "X": upper_xyz[0],
            "Y": upper_xyz[1],
            "Z": upper_xyz[2],
        })


    # 7837 干字型图纸最终生成的担架和塔身的节点编号有重复的，导致冲突，此处代码仅为了避免编号冲突
    # 干字型使用同一 id_prefix 时会与塔身既有编号段重叠，因此尖点基址
    # 固定再偏移 70。该偏移是输出编号协议，不能由节点数量动态推导。
    if drawing_type == "GanZi":
        jiandian_id = (id_prefix * 100 + 1) * 100 + 70

    # 先只用正视图确定两根主杆的上下关系和主分支；底/顶视图的主杆角色
    # 要等分支确定后再映射为 101~104。
    rod_front_a, rod_front_b = detect_main_rods_by_type(coordinatesFront_data, drawing_type)
    _, upper_front_rod, lower_front_rod = get_main_rod_connection_geometry(
        coordinatesFront_data,
        rod_front_a,
        rod_front_b,
    )
    diagonal_rod_is_above = is_diagonal_rod_above_horizontal_rod(
        coordinatesFront_data,
        rod_front_a,
        rod_front_b,
    )
    # 这两个变量只在直流塔 03~06 专用流程中赋值。普通图纸保持 None，
    # 继续走双主杆通用算法。
    zhiliu_front_class1 = None
    zhiliu_projected_frames = None

    # 正视图斜杆在水平杆上方时走 if 分支，在水平杆下方时走 else 分支。
    # 两个大分支执行相同的五阶段业务，但视图角色和 pj 上下端索引不同：
    # - 斜杆在上：底视图=101/102，顶视图=103/104，尖点由底视图计算；
    # - 斜杆在下：顶视图=101/102，底视图=103/104，尖点由顶视图计算。
    # 保留分支内各自的索引参数，避免把图纸方向差异错误统一。
    if diagonal_rod_is_above:

        rod_bottom_a, rod_bottom_b = detect_main_rods_by_type(coordinatesBottom_data, drawing_type)
        rod_overhead_a, rod_overhead_b = detect_main_rods_by_type(coordinatesOverhead_data, drawing_type)

        # 本分支约定 a 对应下连接点(index1)，b 对应上连接点(index0)。
        # 正视图参数重新排列为 a=水平/下杆、b=斜/上杆。后续真实 X 插值
        # 分别使用 pj index1 和 index0，与主杆塔身连接端一一对应。
        rod_front_a, rod_front_b = lower_front_rod, upper_front_rod

        rod_101_id, rod_102_id = rod_bottom_a, rod_bottom_b
        rod_103_id, rod_104_id = rod_overhead_a, rod_overhead_b
        # 汇总全部视图的一类杆编号，供后续移除自动误生成的一类杆件。
        main_rod_ids = [rod_101_id, rod_102_id, rod_103_id, rod_104_id, rod_front_a, rod_front_b]


        ############################################################################################################
        # 1. 计算尖点的三维信息
        ############################################################################################################

        # 本分支从底视图两根主杆和下连接组 pj index1 恢复真实尖点。
        newx, newy, newz = calc_jiandian_xyz(coordinatesBottom_data, drawing_id, pj,1, rod_101_id, rod_102_id)
        new_node = {
            "node_id": f"{jiandian_id + 20}",
            "node_type": NODE_TYPE_CLASS_1,  # 根据实际情况设置节点类型
            "symmetry_type": SYMMETRY_FRONT_BACK,  # 根据实际情况设置对称类型
            "X": round(newx,3),
            "Y": round(newy,3),
            "Z": round(newz,3),
        }
        jiedian.append(new_node)
        # 04/06 是直接靠塔的内层担架：保留底视图算出的水平主杆外端，
        # 再由专用模块根据正视图建立两根主杆、一根副杆及其真实端点。
        # 直流 04/06 是直接连接塔身的内层担架：通用底视图先给出水平
        # 主杆外端，再由专用正视图模块重建三根一类骨架及真实端点。
        if drawing_type == "ZhiLiu" and drawing_id in (4, 6):
            zhiliu_front_class1 = build_zhiliu_near_front_class1(
                coordinatesFront_data,
                pj[drawing_id - 1],
                jiandian_id,
                (newx, newy, newz),
                yuzhi,
            )
            zhiliu_projected_frames = (
                build_zhiliu_near_projected_class1_frames(
                    zhiliu_front_class1
                )
            )
            jiedian.extend(zhiliu_front_class1["new_nodes"])
            main_rod_ids.append(
                zhiliu_front_class1["roles"]["secondary_rod"]
            )
        # 03/05 是复合担架的外层：内端使用 04/06 回传的连接点，
        # 上、下外端仍分别由顶视图、底视图的原有尖点算法提供。
        # 直流 03/05 是外层担架：其内端由已完成的 04/06 通过 pj override
        # 传入，上、下外端仍分别按原顶/底视图尖点算法计算。
        elif drawing_type == "ZhiLiu" and drawing_id in (3, 5):
            upper_remote_xyz = calc_jiandian_xyz(
                coordinatesOverhead_data,
                drawing_id,
                pj,
                0,
                rod_103_id,
                rod_104_id,
            )
            zhiliu_front_class1 = build_zhiliu_outer_front_class1(
                coordinatesFront_data,
                pj[drawing_id - 1],
                jiandian_id,
                (newx, newy, newz),
                upper_remote_xyz,
                "right" if drawing_id == 3 else "left",
            )
            zhiliu_projected_frames = (
                build_zhiliu_near_projected_class1_frames(
                    zhiliu_front_class1
                )
            )
            jiedian.extend(zhiliu_front_class1["new_nodes"])


        ############################################################################################################
        # 2. 正视图
        ############################################################################################################

        # 专用直流骨架存在时，正视图二类杆跨越三根一类杆形成的两个
        # 框架，不能使用普通双主杆算法，因此委托专用模块统一生成。
        zhiliu_front_second_class = None
        # 只要专用一类骨架存在，正视图的二类结构也交给直流塔模块；
        # 普通图纸继续进入下面完全不变的双主杆通用流程。
        if zhiliu_front_class1 is not None:
            if drawing_id in (3, 5):
                zhiliu_front_second_class = (
                    build_zhiliu_outer_front_second_class(
                        coordinatesFront_data,
                        zhiliu_front_class1,
                        id_prefix,
                        yuzhi,
                    )
                )
            else:
                zhiliu_front_second_class = build_zhiliu_near_front_second_class(
                    coordinatesFront_data,
                    zhiliu_front_class1,
                    id_prefix,
                    yuzhi,
                )
            jiedian.extend(zhiliu_front_second_class["new_nodes"])
            ganjian.extend(zhiliu_front_second_class["new_members"])
            # 04/06 的正视图由三根一类杆形成两片框架，新模块统一处理
            # 两片框架，并负责复用公共节点和去除公共杆件。
            jiaodian_101, jiaodian_103 = [], []
        else:
            # 得到两个一类杆件上的交点
            jiaodian_101,jiaodian_103 = get_jiaodian_on_ganjian(coordinatesFront_data,drawing_id, pj, rod_front_a,rod_front_b, yuzhi)

        # 得到这些交点的真实x的值
        # 普通正视图的每个二类节点：X 沿对应一类杆插值，Y/Z 通过
        # 连接点和尖点节点引用表达；主杆端点附近的交点直接复用已有节点。
        real_101 = get_real_x_of_jiaodian(coordinatesFront_data, drawing_id, jiaodian_101, newx, pj, rod_front_a, 1, 1)
        real_103 = get_real_x_of_jiaodian(coordinatesFront_data, drawing_id, jiaodian_103, newx, pj, rod_front_b, 0, 0)

        if zhiliu_front_class1 is not None:
            left_3d_id, right_3d_id = zhiliu_front_class1["endpoint_ids"][
                rod_front_a
            ]
        elif (pj[drawing_id - 1][1][1][0] > 0): # 第 drawing_id 号担架下连接点的 x 坐标
            left_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点的节点编号
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点

        # 标记交点中的端点
        real_101 = mark_endpoint_for_real_points(real_101,coordinatesFront_data,rod_front_a,left_3d_id,right_3d_id,yuzhi)

        if zhiliu_front_class1 is not None:
            left_3d_id, right_3d_id = zhiliu_front_class1["endpoint_ids"][
                rod_front_b
            ]
        elif (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][0][0]  # 303 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点
        real_103 = mark_endpoint_for_real_points(real_103, coordinatesFront_data, rod_front_b, left_3d_id, right_3d_id,yuzhi)

        # ----------------生成节点---------------------------------------------------------------------------------------#
        # 191/193 两段分别对应正视图两根主杆上的新增二类节点。
        node_101_nodes, _ = build_intersection_nodes(
            state,
            real_101,
            lambda sequence: f"{id_prefix}191{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{pj[drawing_id - 1][1][0]}",
                "Z": f"1{jiandian_id + 20}",
            },
        )
        node_103_nodes, _ = build_intersection_nodes(
            state,
            real_103,
            lambda sequence: f"{id_prefix}193{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{pj[drawing_id - 1][0][0]}",
                "Z": f"1{jiandian_id + 20}",
            },
        )

        # # ---------------生成杆件-----------------------------------------------------------------------------------#

        if zhiliu_front_second_class is not None:
            member_to_nodes = zhiliu_front_second_class["member_to_nodes"]
        else:
            member_to_nodes = generate_ganjian(coordinatesFront_data, node_101_nodes, node_103_nodes,yuzhi)

            append_two_node_members(state, member_to_nodes, SYMMETRY_FRONT_BACK)

        # 正视图三类节点使用 691，超过 9 个后转入 791。
        generate_third_class_nodes_and_members(
            state,
            coordinatesFront_data, drawing_id, newx, pj, member_to_nodes,
            rod_front_a, rod_front_b, 1, 1,
            (
                zhiliu_front_class1["endpoint_ids"]
                if zhiliu_front_class1 is not None
                else {
                    rod_front_a: (pj[drawing_id - 1][1][0], f"{jiandian_id + 20}"),
                    rod_front_b: (pj[drawing_id - 1][0][0], f"{jiandian_id + 20}"),
                }
            ),
            id_prefix, ("691", "791"), 2, yuzhi,
            extra_main_rod_ids=(
                [zhiliu_front_class1["roles"]["secondary_rod"]]
                if (
                    zhiliu_front_class1 is not None
                    and "secondary_rod" in zhiliu_front_class1["roles"]
                )
                else None
            ),
            seed_nodes_2d=(
                zhiliu_front_second_class.get("nodes_2d")
                if (
                    zhiliu_front_second_class is not None
                    and drawing_id in (3, 5)
                )
                else None
            ),
            real_x_endpoint_xyz=(
                zhiliu_front_class1["endpoint_xyz"][rod_front_a]
                if (
                    zhiliu_front_class1 is not None
                    and drawing_id in (3, 5)
                )
                else None
            ),
        )

        ############################################################################################################
        # 3. 底视图
        ############################################################################################################

        jiaodian_101,jiaodian_102 = get_jiaodian_on_ganjian(coordinatesBottom_data,drawing_id, pj, rod_101_id,rod_102_id, yuzhi)

        # 直流塔底视图仍复用原节点/杆件生成流程，仅把几何基准替换为
        # 正视图水平主杆的真实端点及其 +2 对称端点。
        if zhiliu_projected_frames is not None:
            bottom_frame = zhiliu_projected_frames["bottom"]
            real_101 = get_real_x_between_xyz_endpoints(
                coordinatesBottom_data, jiaodian_101, rod_101_id,
                bottom_frame["endpoint_xyz"],
            )
            real_102 = get_real_x_between_xyz_endpoints(
                coordinatesBottom_data, jiaodian_102, rod_102_id,
                bottom_frame["endpoint_xyz"],
            )
            left_3d_id, right_3d_id = bottom_frame[
                "primary_endpoint_ids"
            ]
        else:
            real_101 = get_real_x_of_jiaodian(coordinatesBottom_data, drawing_id, jiaodian_101, newx, pj, rod_101_id,1,1)
            real_102 = get_real_x_of_jiaodian(coordinatesBottom_data, drawing_id, jiaodian_102, newx, pj, rod_102_id, 0,0)

        if zhiliu_projected_frames is not None:
            pass
        elif (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点
        real_101 = mark_endpoint_for_real_points(real_101,coordinatesBottom_data,rod_101_id,left_3d_id,right_3d_id,yuzhi)


        if zhiliu_projected_frames is not None:
            left_3d_id, right_3d_id = bottom_frame[
                "symmetric_endpoint_ids"
            ]
        elif (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET)
            right_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
        else:
            left_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
            right_3d_id = str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET)
        real_102 = mark_endpoint_for_real_points(real_102, coordinatesBottom_data, rod_102_id, left_3d_id, right_3d_id,yuzhi)

        # ----------------生成节点---------------------------------------------------------------------------------------#
        # 底视图的两根一类杆互为前后镜像：291...0 节点保存真实 X 和
        # 对称端点引用，291...2 仅作为同一二维位置体系下的镜像节点编号。
        # build_intersection_nodes 会优先复用已标记的塔身端点/尖点，因此
        # sequence 只对真正新建的交点递增，不会因复用端点产生编号空洞。
        if zhiliu_projected_frames is not None:
            reference_start, reference_end = bottom_frame[
                "symmetric_endpoint_ids"
            ]
        else:
            reference_start = str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET)
            reference_end = str(jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET)
        node_101_ids, _ = build_intersection_nodes(
            state,
            real_102,
            lambda sequence: f"{id_prefix}291{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{reference_start}",
                "Z": f"1{reference_end}",
            },
        )
        node_102_ids, _ = build_intersection_nodes(
            state,
            real_101,
            lambda sequence: f"{id_prefix}291{sequence}2",
        )

        # ----------------生成杆件---------------------------------------------------------------------------------------#

        member_to_nodes = generate_ganjian(coordinatesBottom_data, node_101_ids, node_102_ids,yuzhi)

        append_two_node_members(state, member_to_nodes, SYMMETRY_NONE)

        generate_third_class_nodes_and_members(
            state,
            coordinatesBottom_data, drawing_id, newx, pj, member_to_nodes,
            rod_101_id, rod_102_id, 1, 1,
            (
                {
                    rod_101_id: bottom_frame["primary_endpoint_ids"],
                    rod_102_id: bottom_frame["symmetric_endpoint_ids"],
                }
                if zhiliu_projected_frames is not None
                else {
                    rod_101_id: (pj[drawing_id - 1][1][0], f"{jiandian_id + 20}"),
                    rod_102_id: (
                        str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET),
                        f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}",
                    ),
                }
            ),
            id_prefix, ("491", "591"), 0, yuzhi,
            # 直流专用投影的端点不是由通用 pj+尖点组合得到，因此把已识别的
            # 二类二维点作为种子，并显式传入正视图骨架的真实 XYZ 插值基准。
            seed_nodes_2d=(
                node_101_ids + node_102_ids
                if zhiliu_projected_frames is not None
                else None
            ),
            real_x_endpoint_xyz=(
                bottom_frame["endpoint_xyz"]
                if zhiliu_projected_frames is not None
                else None
            ),
        )
        ############################################################################################################
        # 4. 顶视图
        ############################################################################################################

        jiaodian_103,jiaodian_104 = get_jiaodian_on_ganjian(coordinatesOverhead_data,drawing_id, pj, rod_103_id,rod_104_id, yuzhi)

        # 直流塔顶视图与底视图处理方式相同，但几何基准取正视图斜主杆。
        if zhiliu_projected_frames is not None:
            overhead_frame = zhiliu_projected_frames["overhead"]
            real_103 = get_real_x_between_xyz_endpoints(
                coordinatesOverhead_data, jiaodian_103, rod_103_id,
                overhead_frame["endpoint_xyz"],
            )
            real_104 = get_real_x_between_xyz_endpoints(
                coordinatesOverhead_data, jiaodian_104, rod_104_id,
                overhead_frame["endpoint_xyz"],
            )
            left_3d_id, right_3d_id = overhead_frame[
                "primary_endpoint_ids"
            ]
        else:
            real_103 = get_real_x_of_jiaodian(coordinatesOverhead_data, drawing_id, jiaodian_103, newx, pj, rod_103_id,1,0)
            real_104 = get_real_x_of_jiaodian(coordinatesOverhead_data, drawing_id, jiaodian_104, newx, pj, rod_104_id, 1,0)

        if zhiliu_projected_frames is not None:
            pass
        elif (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点

        real_103 = mark_endpoint_for_real_points(real_103, coordinatesOverhead_data, rod_103_id, left_3d_id, right_3d_id,yuzhi)

        if zhiliu_projected_frames is not None:
            left_3d_id, right_3d_id = overhead_frame[
                "symmetric_endpoint_ids"
            ]
        elif (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET)
            right_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
            right_3d_id = str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET)

        real_104 = mark_endpoint_for_real_points(real_104, coordinatesOverhead_data, rod_104_id, left_3d_id, right_3d_id,yuzhi)

        # ----------------生成节点---------------------------------------------------------------------------------------#
        # 顶视图使用独立的 391 编号段，避免与底视图 291 节点冲突。
        # 此处 ...0 对应主杆真实端点，...2 对应 +2 镜像端点；节点坐标中的
        # Y/Z 字符串仍是三维端点引用，不是二维图纸坐标。
        if zhiliu_projected_frames is not None:
            reference_start, reference_end = overhead_frame[
                "primary_endpoint_ids"
            ]
        else:
            reference_start = str(pj[drawing_id - 1][0][0])
            reference_end = str(jiandian_id + 20)
        node_103_ids, _ = build_intersection_nodes(
            state,
            real_103,
            lambda sequence: f"{id_prefix}391{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{reference_start}",
                "Z": f"1{reference_end}",
            },
        )
        node_104_ids, _ = build_intersection_nodes(
            state,
            real_104,
            lambda sequence: f"{id_prefix}391{sequence}2",
        )

        # ----------------生成杆件---------------------------------------------------------------------------------------#
        member_to_nodes = generate_ganjian(coordinatesOverhead_data, node_103_ids, node_104_ids,yuzhi)

        append_two_node_members(state, member_to_nodes, SYMMETRY_NONE)

        generate_third_class_nodes_and_members(
            state,
            coordinatesOverhead_data, drawing_id, newx, pj, member_to_nodes,
            rod_103_id, rod_104_id, 1, 0,
            (
                {
                    rod_103_id: overhead_frame["primary_endpoint_ids"],
                    rod_104_id: overhead_frame["symmetric_endpoint_ids"],
                }
                if zhiliu_projected_frames is not None
                else {
                    rod_103_id: (pj[drawing_id - 1][0][0], f"{jiandian_id + 20}"),
                    rod_104_id: (
                        str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET),
                        f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}",
                    ),
                }
            ),
            id_prefix, ("891", "991"), 0, yuzhi,
            # 直流顶视图投影来自正视图斜主杆，所以三类节点的 X 插值必须
            # 沿 overhead_frame 的真实端点进行，不能改用通用 pj 端点。
            seed_nodes_2d=(
                node_103_ids + node_104_ids
                if zhiliu_projected_frames is not None
                else None
            ),
            real_x_endpoint_xyz=(
                overhead_frame["endpoint_xyz"]
                if zhiliu_projected_frames is not None
                else None
            ),
        )
        ############################################################################################################
        # 5. 添加一类杆件
        ############################################################################################################

        # 删除已经生成的一类杆件信息
        remove_ids = {
            str(rod_101_id),
            str(rod_102_id),
            str(rod_103_id),
            str(rod_104_id),
            str(rod_front_a),
            str(rod_front_b),
        }
        # 专用流程可能已在二类/三类搜索中匹配到一类杆；先统一移除，
        # 再按已经确定的真实端点重建，防止错误端点或重复杆件残留。
        if zhiliu_front_class1 is not None:
            secondary_rod = zhiliu_front_class1["roles"].get(
                "secondary_rod"
            )
            if secondary_rod is not None:
                remove_ids.add(str(secondary_rod))

        remove_members_by_id(state, remove_ids)

        if zhiliu_front_class1 is not None:
            for rod_id in zhiliu_front_class1["roles"]["all_rods"]:
                node1_id, node2_id = zhiliu_front_class1["endpoint_ids"][
                    rod_id
                ]
                ganjian.append({
                    "member_id": str(rod_id),
                    "node1_id": node1_id,
                    "node2_id": node2_id,
                    "symmetry_type": SYMMETRY_FRONT_BACK,
                })

            # 底视图投影水平主杆，顶视图投影倾斜主杆。两组中的
            # 第二根杆连接对应的 +2 对称节点。
            for rod_id, endpoint_key, frame_name in (
                (rod_101_id, "primary_endpoint_ids", "bottom"),
                (rod_102_id, "symmetric_endpoint_ids", "bottom"),
                (rod_103_id, "primary_endpoint_ids", "overhead"),
                (rod_104_id, "symmetric_endpoint_ids", "overhead"),
            ):
                node1_id, node2_id = zhiliu_projected_frames[frame_name][
                    endpoint_key
                ]
                ganjian.append({
                    "member_id": str(rod_id),
                    "node1_id": node1_id,
                    "node2_id": node2_id,
                    "symmetry_type": SYMMETRY_NONE,
                })
        else:
            # 普通图纸的正视图只需重建两根真实一类杆。底/顶视图中的
            # 101~104 是这两根空间杆的不同投影，不在此处重复写入杆件表。
            new_ganjian = {
                "member_id": f"{rod_front_a}",
                "node1_id": pj[drawing_id - 1][1][0],
                "node2_id": f"{jiandian_id + 20}",
                "symmetry_type": SYMMETRY_FRONT_BACK
            }
            ganjian.append(new_ganjian)

            new_ganjian = {
                "member_id": f"{rod_front_b}",
                "node1_id": pj[drawing_id - 1][0][0],
                "node2_id": f"{jiandian_id + 20}",
                "symmetry_type": SYMMETRY_FRONT_BACK
            }
            ganjian.append(new_ganjian)


    else:
        # 斜主杆位于水平主杆下方时，101/102 来自顶视图，103/104 来自
        # 底视图。这个映射与上一分支相反，后续 pj 索引和编号尾码也随之
        # 调换；这里保留完整分支以维持既有图纸方向语义。

        rod_bottom_a, rod_bottom_b = detect_main_rods_by_type(coordinatesBottom_data, drawing_type)
        rod_overhead_a, rod_overhead_b = detect_main_rods_by_type(coordinatesOverhead_data, drawing_type)

        # 本分支约定 a 对应上连接点(index0)，b 对应下连接点(index1)。
        rod_front_a, rod_front_b = upper_front_rod, lower_front_rod

        rod_101_id, rod_102_id = rod_overhead_a, rod_overhead_b
        rod_103_id, rod_104_id = rod_bottom_a, rod_bottom_b
        main_rod_ids = [rod_101_id, rod_102_id, rod_103_id, rod_104_id, rod_front_a, rod_front_b]


        ############################################################################################################
        # 1. 计算尖点的三维信息
        ############################################################################################################

        # 本方向从顶视图的 101/102 恢复尖点；羊角形 01 的正视图具有额外
        # 塔身中心线上连接点，其尖点 Z 必须沿用既有专用几何计算结果。
        newx, newy, newz = calc_jiandian_xyz(coordinatesOverhead_data, drawing_id, pj, 0, rod_101_id, rod_102_id)
        if drawing_type == "YangJiao" and drawing_id == 1:
            newz = calc_yangjiao_01_apex_z(
                coordinatesFront_data,
                pj[drawing_id - 1],
                rod_front_a,
                rod_front_b,
            )
        new_node = {
            "node_id": f"{jiandian_id + 20}",
            "node_type": NODE_TYPE_CLASS_1,  # 根据实际情况设置节点类型
            "symmetry_type": SYMMETRY_FRONT_BACK,  # 根据实际情况设置对称类型
            "X": round(newx,3),
            "Y": round(newy,3),
            "Z": round(newz,3),
        }
        jiedian.append(new_node)

        ############################################################################################################
        # 2. 正视图
        ############################################################################################################


        # 正视图仍负责两根空间主杆上的二类交点：191 属于连接 pj[0] 的
        # 主杆，193 属于连接 pj[1] 的主杆；两组都以真实尖点为另一端。
        jiaodian_101,jiaodian_103 = get_jiaodian_on_ganjian(coordinatesFront_data,drawing_id, pj, rod_front_a,rod_front_b, yuzhi)

        real_101 = get_real_x_of_jiaodian(coordinatesFront_data, drawing_id, jiaodian_101, newx, pj, rod_front_a, 1, 0)
        real_103 = get_real_x_of_jiaodian(coordinatesFront_data, drawing_id, jiaodian_103, newx, pj, rod_front_b, 0, 1)

        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点

        real_101 = mark_endpoint_for_real_points(real_101, coordinatesFront_data, rod_front_a, left_3d_id, right_3d_id,yuzhi)

        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点

        real_103 = mark_endpoint_for_real_points(real_103, coordinatesFront_data, rod_front_b, left_3d_id, right_3d_id,yuzhi)

        # ---------------生成节点-----------------------------------------------------------------------------------#
        node_101_nodes, _ = build_intersection_nodes(
            state,
            real_101,
            lambda sequence: f"{id_prefix}191{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{pj[drawing_id - 1][0][0]}",
                "Z": f"1{jiandian_id + 20}",
            },
        )
        node_103_nodes, _ = build_intersection_nodes(
            state,
            real_103,
            lambda sequence: f"{id_prefix}193{sequence}0",
            lambda node_id, item: {
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{pj[drawing_id - 1][1][0]}",
                "Z": f"1{jiandian_id + 20}",
            },
        )

        # ---------------生成杆件-----------------------------------------------------------------------------------#

        member_to_nodes = generate_ganjian(coordinatesFront_data, node_101_nodes, node_103_nodes,yuzhi)

        append_two_node_members(state, member_to_nodes, SYMMETRY_FRONT_BACK)

        generate_third_class_nodes_and_members(
            state,
            coordinatesFront_data, drawing_id, newx, pj, member_to_nodes,
            rod_front_a, rod_front_b, 1, 0,
            {
                rod_front_a: (pj[drawing_id - 1][0][0], f"{jiandian_id + 20}"),
                rod_front_b: (pj[drawing_id - 1][1][0], f"{jiandian_id + 20}"),
            },
            id_prefix, ("691", "791"), 2, yuzhi,
        )

        ############################################################################################################
        # 3. 顶视图
        ############################################################################################################

        # 顶视图中 102 是 101 的 +2 镜像投影。先给两组交点标记已有三维
        # 端点，再把其余交点放入 291 编号段，供二维杆件端点匹配使用。
        jiaodian_101,jiaodian_102 = get_jiaodian_on_ganjian(coordinatesOverhead_data,drawing_id, pj, rod_101_id,rod_102_id, yuzhi)

        real_101 = get_real_x_of_jiaodian(coordinatesOverhead_data, drawing_id, jiaodian_101, newx, pj, rod_101_id,1,1)
        real_102 = get_real_x_of_jiaodian(coordinatesOverhead_data, drawing_id, jiaodian_102, newx, pj, rod_102_id, 1,0)


        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][0][0]  # 301 与塔身相交端点

        real_101 = mark_endpoint_for_real_points(real_101, coordinatesOverhead_data, rod_101_id, left_3d_id, right_3d_id,yuzhi)

        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET)
            right_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
            right_3d_id = str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET)

        real_102 = mark_endpoint_for_real_points(real_102, coordinatesOverhead_data, rod_102_id, left_3d_id, right_3d_id,yuzhi)

        # ----------------生成节点---------------------------------------------------------------------------------------#
        # real_102 的新交点以 291...0 写入最终节点表，并引用 +2 镜像端点；
        # real_101 的 291...2 只加入二维匹配列表，不再写一份节点记录。
        # 这是既有对称性表达方式：输出中的一个基础节点配合 symmetry_type
        # 表示对应镜像，不能把缺少 append 误判为漏生成节点。
        node_101_ids = []
        node_102_ids = []

        new_node_cnt = 0  # 只统计“真正新建的节点”
        for i, item in enumerate(real_102):
            if item.get("endpoint_3d_id", -1) != -1:
                # 复用已有端点节点
                node_102_ids.append({
                    "node_id": item["endpoint_3d_id"],
                    "point_2d": item["point_2d"]
                })
                continue

            new_node_cnt += 1
            node_id = f"{id_prefix}291{new_node_cnt}0"
            node_info = {
                "node_id": node_id,
                "point_2d": item["point_2d"]
            }
            node_102_ids.append(node_info)
            duichenzuo = int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET
            jiedian.append({
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{duichenzuo}",
                "Z": f"1{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
            })

        new_node_cnt = 0  # 只统计“真正新建的节点”
        for i, item in enumerate(real_101):
            if item.get("endpoint_3d_id", -1) != -1:
                # 复用已有端点节点
                node_101_ids.append({
                    "node_id": item["endpoint_3d_id"],
                    "point_2d": item["point_2d"]
                })
                continue

            new_node_cnt += 1
            node_id = f"{id_prefix}291{new_node_cnt}2"
            node_info = {
                "node_id": node_id,
                "point_2d": item["point_2d"]
            }
            node_101_ids.append(node_info)

        # ----------------生成杆件---------------------------------------------------------------------------------------#

        member_to_nodes = generate_ganjian(coordinatesOverhead_data, node_101_ids, node_102_ids,yuzhi)

        append_two_node_members(state, member_to_nodes, SYMMETRY_NONE)

        generate_third_class_nodes_and_members(
            state,
            coordinatesOverhead_data, drawing_id, newx, pj, member_to_nodes,
            rod_101_id, rod_102_id, 1, 1,
            {
                rod_101_id: (pj[drawing_id - 1][0][0], f"{jiandian_id + 20}"),
                rod_102_id: (
                    str(int(pj[drawing_id - 1][0][0]) + MIRRORED_NODE_ID_OFFSET),
                    f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}",
                ),
            },
            id_prefix, ("891", "991"), 0, yuzhi,
        )

        ############################################################################################################
        # 4. 底视图
        ############################################################################################################

        # 底视图处理 103/104，其中 103 使用真实连接端，104 使用统一 +2
        # 镜像端。其二类节点进入独立的 391 编号段，三类节点使用 491/591。
        jiaodian_103,jiaodian_104 = get_jiaodian_on_ganjian(coordinatesBottom_data,drawing_id, pj, rod_103_id,rod_104_id, yuzhi)

        real_103 = get_real_x_of_jiaodian(coordinatesBottom_data, drawing_id, jiaodian_103, newx, pj, rod_103_id,1,0)
        real_104 = get_real_x_of_jiaodian(coordinatesBottom_data, drawing_id, jiaodian_104, newx, pj, rod_104_id, 1,0)

        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点
            right_3d_id = f"{jiandian_id + 20}"  # 尖点
        else:
            left_3d_id = f"{jiandian_id + 20}"
            right_3d_id = pj[drawing_id - 1][1][0]  # 301 与塔身相交端点
        real_103 = mark_endpoint_for_real_points(real_103,coordinatesBottom_data,rod_103_id,left_3d_id,right_3d_id,yuzhi)

        if (pj[drawing_id - 1][1][1][0] > 0):
            left_3d_id = str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET)
            right_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
        else:
            left_3d_id = f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}"
            right_3d_id = str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET)
        real_104 = mark_endpoint_for_real_points(real_104, coordinatesBottom_data, rod_104_id, left_3d_id, right_3d_id,yuzhi)


        # ----------------生成节点---------------------------------------------------------------------------------------#
        # 与顶视图相反，这里 391...0（real_103）写入基础节点记录，
        # 391...2（real_104）通常仅承担二维匹配中的镜像节点 ID。
        node_103_ids = []
        node_104_ids = []

        new_node_cnt = 0  # 只统计“真正新建的节点”
        for i, item in enumerate(real_103):
            if item.get("endpoint_3d_id", -1) != -1:
                # 复用已有端点节点
                node_103_ids.append({
                    "node_id": item["endpoint_3d_id"],
                    "point_2d": item["point_2d"]
                })
                continue

            new_node_cnt += 1
            node_id = f"{id_prefix}391{new_node_cnt}0"
            node_info = {
                "node_id": node_id,
                "point_2d": item["point_2d"]
            }
            node_103_ids.append(node_info)
            duichenzuo = int(pj[drawing_id - 1][1][0])
            jiedian.append({
                "node_id": node_id,
                "node_type": NODE_TYPE_CLASS_2,
                "symmetry_type": SYMMETRY_FRONT_BACK,
                "X": item["x_3d"],
                "Y": f"1{duichenzuo}",
                "Z": f"1{jiandian_id + 20}"
            })

        base_node_count = new_node_cnt
        new_node_cnt = 0  # 只统计“真正新建的节点”
        for i, item in enumerate(real_104):
            if item.get("endpoint_3d_id", -1) != -1:
                # 复用已有端点节点
                node_104_ids.append({
                    "node_id": item["endpoint_3d_id"],
                    "point_2d": item["point_2d"]
                })
                continue

            new_node_cnt += 1
            node_id = f"{id_prefix}391{new_node_cnt}2"
            node_info = {
                "node_id": node_id,
                "point_2d": item["point_2d"]
            }
            node_104_ids.append(node_info)

            # 羊角形 01 的两根底视图主杆交点数不一致时，补齐额外
            # 对称节点对应的基础节点，避免产生悬空的节点引用。
            if (
                drawing_type == "YangJiao"
                and drawing_id == 1
                and new_node_cnt > base_node_count
            ):
                base_node_id = f"{id_prefix}391{new_node_cnt}0"
                duichenzuo = int(pj[drawing_id - 1][1][0])
                jiedian.append({
                    "node_id": base_node_id,
                    "node_type": NODE_TYPE_CLASS_2,
                    "symmetry_type": SYMMETRY_FRONT_BACK,
                    "X": item["x_3d"],
                    "Y": f"1{duichenzuo}",
                    "Z": f"1{jiandian_id + 20}"
                })
        # ----------------生成杆件---------------------------------------------------------------------------------------#

        member_to_nodes = generate_ganjian(coordinatesBottom_data, node_103_ids, node_104_ids,yuzhi)

        append_two_node_members(state, member_to_nodes, SYMMETRY_NONE)

        generate_third_class_nodes_and_members(
            state,
            coordinatesBottom_data, drawing_id, newx, pj, member_to_nodes,
            rod_103_id, rod_104_id, 1, 0,
            {
                rod_103_id: (pj[drawing_id - 1][1][0], f"{jiandian_id + 20}"),
                rod_104_id: (
                    str(int(pj[drawing_id - 1][1][0]) + MIRRORED_NODE_ID_OFFSET),
                    f"{jiandian_id + 20 + MIRRORED_NODE_ID_OFFSET}",
                ),
            },
            id_prefix, ("491", "591"), 0, yuzhi,
        )

        ############################################################################################################
        # 5. 添加一类杆件
        ############################################################################################################

        # 二类/三类杆件搜索会把投影中的一类主杆也识别出来。这里必须先按
        # 六个视图杆号统一删除，再以确定的塔身连接点和尖点重建正视图的
        # 两根空间一类杆，从而保持最终端点和追加顺序与原协议一致。
        remove_ids = {
            str(rod_101_id),
            str(rod_102_id),
            str(rod_103_id),
            str(rod_104_id),
            str(rod_front_a),
            str(rod_front_b),
        }

        remove_members_by_id(state, remove_ids)

        new_ganjian = {
            "member_id": f"{rod_front_a}",
            "node1_id": pj[drawing_id - 1][0][0],
            "node2_id": f"{jiandian_id + 20}",
            "symmetry_type": SYMMETRY_FRONT_BACK
        }
        ganjian.append(new_ganjian)

        new_ganjian = {
            "member_id": f"{rod_front_b}",
            "node1_id": pj[drawing_id - 1][1][0],
            "node2_id": f"{jiandian_id + 20}",
            "symmetry_type": SYMMETRY_FRONT_BACK
        }
        ganjian.append(new_ganjian)




    # ShangZi 等图型的对称性修正必须等本图三视图、三类杆件及一类杆件
    # 全部生成后执行。起始游标把处理范围限制在本次 trans() 新增的切片，
    # 避免累计 state 中先前图纸的节点和杆件被再次改写。
    apply_symmetry_postprocessing(
        state,
        drawing_type,
        drawing_id,
        file_path,
        StateCursor(jiedian_start, ganjian_start),
    )

    # 仅直流塔 03/04/05/06 专用骨架会返回连接组。work() 只使用
    # 04/06 的返回值继续向外传递，普通担架仍返回 None。
    if zhiliu_front_class1 is not None:
        return zhiliu_front_class1.get("outer_connection_group")
    return None

def work(file_path, data, drawing_type, tashen_dir=None):
    """转换目录内全部担架图纸并返回本次调用独立的节点、杆件。"""
    # 每次入口调用都创建新的运行状态，节点和杆件只在本次转换内累计，
    # 不再依赖模块级可变列表，因此连续调用 work() 不会串入上次结果。
    state = ConversionState()
    # 担架和塔身合并的图纸（塔身目录下存在 01.txt，如 T7833/7837）担架编号需偏移 +2，
    # 避免担架与塔身的节点编号生成重复。
    id_offset = bool(tashen_dir) and os.path.exists(os.path.join(tashen_dir, "01.txt"))

    drawings = list_stretcher_drawings(file_path)
    # 普通图型保持 list_stretcher_drawings() 的自然数字顺序；只有直流
    # 复合担架需要按固定依赖顺序执行，以便内层先计算外端连接组。
    if drawing_type == "ZhiLiu":
        # 复合担架必须先重建靠塔部分再重建外层部分，才能传递真实连接点。
        execution_order = {
            drawing_id: order
            for order, drawing_id in enumerate(ZHILIU_EXECUTION_ORDER)
        }
        drawings.sort(
            key=lambda item: execution_order.get(
                item[0], len(execution_order) + item[0]
            )
        )

    zhiliu_pj_overrides = {}
    for connection_index, (drawing_id, drawing_path) in enumerate(drawings):
        # 普通图纸的 data 连接组按实际执行位置连续消费；直流图纸虽然
        # 改变了执行顺序，却仍必须用 drawing_id-1 读取与文件号对应的组。
        if drawing_type == "ZhiLiu":
            # 直流塔在 trans() 中已经按实际图号建立 01..06 的 pj 映射；
            # 执行顺序只负责让内段先于外段，不能再用执行序号改写图号索引。
            connection_index = drawing_id - 1
        outer_connection_group = trans(
            drawing_path,
            drawing_id,
            data,
            drawing_type,
            id_offset,
            connection_index,
            zhiliu_pj_overrides,
            state,
        )
        if drawing_type == "ZhiLiu" and outer_connection_group is not None:
            # 04 的外端覆盖 03 使用的原始 pj[3]，06 的外端覆盖 05 使用
            # 的原始 pj[2]；下一次 trans() 会在 pj 重排前应用该覆盖。
            if drawing_id == 4:
                zhiliu_pj_overrides[3] = outer_connection_group
            elif drawing_id == 6:
                zhiliu_pj_overrides[2] = outer_connection_group


    # state 内列表保持各图纸实际执行时的追加顺序；这里不再排序或复制，
    # 以维持调用方依赖的节点、杆件输出次序。
    return state.nodes, state.members
