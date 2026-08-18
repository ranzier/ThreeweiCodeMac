"""直流塔 04/06 靠塔担架正视图重建。

本模块处理正视图中的一类骨架，以及骨架两片区域内的二类节点和
二类杆件。底视图、顶视图以及普通担架仍由 ``xintrans.py`` 的原有
流程负责。
"""

import math

from get_first_ganjian_id import detect_main_rods_enhanced
from stretcher_tower_connection import get_main_rod_connection_geometry


def _dist_points(point1, point2):
    return math.hypot(point2[0] - point1[0], point2[1] - point1[1])


def _dist_point_to_line(point, line_point1, line_point2):
    x0, y0 = point
    x1, y1 = line_point1
    x2, y2 = line_point2
    denominator = math.hypot(y2 - y1, x2 - x1)
    if math.isclose(denominator, 0.0, abs_tol=1e-9):
        return _dist_points(point, line_point1)
    return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / denominator


def detect_zhiliu_near_front_class1_rods(coordinates_data, threshold=150):
    """识别靠塔担架正视图的两根一类主杆和一根一类副杆。"""
    # 04/06 的正视图比旧图纸多一根参与骨架定位的一类副杆。先沿用原算法
    # 找出两根最长主杆，再单独从其余杆件中识别副杆，避免改变旧识别函数。
    primary_ids = detect_main_rods_enhanced(coordinates_data)
    if len(primary_ids) != 2:
        raise ValueError("直流塔靠塔担架正视图未识别到两根一类主杆")

    def vertical_ratio(rod_id):
        point1, point2 = coordinates_data[rod_id]
        length = _dist_points(point1, point2)
        if math.isclose(length, 0.0, abs_tol=1e-9):
            raise ValueError(f"正视图杆件 {rod_id} 是零长度杆件")
        return abs(point2[1] - point1[1]) / length

    # 竖向变化比例较小的是水平主杆，较大的是斜主杆。
    lower_rod, diagonal_rod = sorted(primary_ids, key=vertical_ratio)
    diagonal_points = coordinates_data[diagonal_rod]
    candidates = []
    for rod_id, points in coordinates_data.items():
        if rod_id in primary_ids or vertical_ratio(rod_id) > 0.1:
            continue
        if any(
            _dist_point_to_line(point, diagonal_points[0], diagonal_points[1])
            < threshold
            for point in points
        ):
            candidates.append((_dist_points(points[0], points[1]), rod_id))

    if not candidates:
        raise ValueError("直流塔靠塔担架正视图未识别到一类副杆")

    # 一类副杆近似水平、至少一端落在斜主杆上；候选中取最长杆。
    _, secondary_rod = max(candidates, key=lambda item: item[0])
    return {
        "main_rods": (lower_rod, diagonal_rod),
        "secondary_rod": secondary_rod,
        "all_rods": (lower_rod, diagonal_rod, secondary_rod),
    }


def _endpoint_index_on_side(points, side):
    if side not in ("left", "right"):
        raise ValueError(f"未知端点方向: {side}")
    selector = min if side == "left" else max
    endpoint = selector(enumerate(points), key=lambda item: item[1][0])
    return endpoint[0]


def _projection_ratio(point, segment):
    (x1, y1), (x2, y2) = segment
    vx, vy = x2 - x1, y2 - y1
    length_squared = vx * vx + vy * vy
    if math.isclose(length_squared, 0.0, abs_tol=1e-9):
        raise ValueError("无法在零长度杆件上插值三维坐标")
    ratio = ((point[0] - x1) * vx + (point[1] - y1) * vy) / length_squared
    return max(0.0, min(1.0, ratio))


def _line_intersection(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if math.isclose(denominator, 0.0, abs_tol=1e-9):
        return None
    return (
        (
            (x1 * y2 - y1 * x2) * (x3 - x4)
            - (x1 - x2) * (x3 * y4 - y3 * x4)
        )
        / denominator,
        (
            (x1 * y2 - y1 * x2) * (y3 - y4)
            - (y1 - y2) * (x3 * y4 - y3 * x4)
        )
        / denominator,
    )


def _is_point_near_segment(point, segment, threshold):
    if _dist_point_to_line(point, segment[0], segment[1]) >= threshold:
        return False
    min_x = min(segment[0][0], segment[1][0]) - threshold
    max_x = max(segment[0][0], segment[1][0]) + threshold
    min_y = min(segment[0][1], segment[1][1]) - threshold
    max_y = max(segment[0][1], segment[1][1]) + threshold
    return min_x <= point[0] <= max_x and min_y <= point[1] <= max_y


def _interpolate_xyz(start_xyz, end_xyz, ratio):
    return tuple(
        float(start_xyz[index])
        + ratio * (float(end_xyz[index]) - float(start_xyz[index]))
        for index in range(3)
    )


def build_zhiliu_near_front_class1(
    coordinates_front_data,
    connection_group,
    jiandian_id,
    lower_remote_xyz,
    threshold=150,
):
    """生成直流塔 04/06 靠塔担架正视图的一类骨架信息。"""
    roles = detect_zhiliu_near_front_class1_rods(
        coordinates_front_data, threshold
    )
    lower_rod, diagonal_rod = roles["main_rods"]
    secondary_rod = roles["secondary_rod"]
    connection_side, _, _ = get_main_rod_connection_geometry(
        coordinates_front_data, lower_rod, diagonal_rod
    )

    if not connection_group or len(connection_group) < 2:
        raise ValueError("直流塔靠塔担架缺少塔身连接点")

    # connection_group 的固定顺序是上连接点、下连接点。04 的连接端在右侧，
    # 06 的连接端在左侧；connection_side 根据二维杆件位置自动判断。
    tower_upper_id, tower_upper_xyz = connection_group[0]
    tower_lower_id, tower_lower_xyz = connection_group[1]
    # 直流塔靠塔担架的一类节点编号约定：+20 为水平主杆外端，+30 为
    # 斜主杆外端，+40 为副杆与斜主杆的连接端，+50 为副杆外端。
    lower_remote_id = str(jiandian_id + 20)
    diagonal_joint_id = str(jiandian_id + 30)
    secondary_joint_id = str(jiandian_id + 40)
    upper_remote_id = str(jiandian_id + 50)

    lower_points = coordinates_front_data[lower_rod]
    diagonal_points = coordinates_front_data[diagonal_rod]
    secondary_points = coordinates_front_data[secondary_rod]
    tower_lower_index = _endpoint_index_on_side(lower_points, connection_side)
    tower_upper_index = _endpoint_index_on_side(diagonal_points, connection_side)
    lower_remote_index = 1 - tower_lower_index
    diagonal_joint_index = 1 - tower_upper_index

    # 水平主杆连接端直接使用塔身传入的真实坐标；外端坐标由 xintrans.py
    # 按底视图原有比例计算后通过 lower_remote_xyz 传入。
    lower_endpoint_xyz = [None, None]
    lower_endpoint_xyz[tower_lower_index] = tuple(map(float, tower_lower_xyz))
    lower_endpoint_xyz[lower_remote_index] = tuple(map(float, lower_remote_xyz))
    # 斜主杆外端在正视图中落到水平主杆上，因此使用正视图投影比例在
    # 水平主杆的两端真实 XYZ 之间插值，不再假设两根主杆收敛到尖点。
    diagonal_joint_xyz = _interpolate_xyz(
        lower_endpoint_xyz[0],
        lower_endpoint_xyz[1],
        _projection_ratio(diagonal_points[diagonal_joint_index], lower_points),
    )

    diagonal_endpoint_xyz = [None, None]
    diagonal_endpoint_xyz[tower_upper_index] = tuple(map(float, tower_upper_xyz))
    diagonal_endpoint_xyz[diagonal_joint_index] = diagonal_joint_xyz
    secondary_joint_index = min(
        range(2),
        key=lambda index: _dist_point_to_line(
            secondary_points[index], diagonal_points[0], diagonal_points[1]
        ),
    )
    if (
        _dist_point_to_line(
            secondary_points[secondary_joint_index],
            diagonal_points[0],
            diagonal_points[1],
        )
        >= threshold
    ):
        raise ValueError(
            f"直流塔一类副杆 {secondary_rod} 没有端点落在斜主杆 {diagonal_rod} 上"
        )
    # 副杆与斜主杆相接端同样按正视图比例，在斜主杆真实 XYZ 上插值。
    secondary_joint_xyz = _interpolate_xyz(
        diagonal_endpoint_xyz[0],
        diagonal_endpoint_xyz[1],
        _projection_ratio(secondary_points[secondary_joint_index], diagonal_points),
    )

    secondary_remote_index = 1 - secondary_joint_index
    # 一类副杆外端的平面位置由正视图确定：将该端点投影到水平主杆，
    # 再沿水平主杆的真实三维线段插值得到 X、Y。副杆在正视图中
    # 近似水平，因此 Z 与副杆连接端保持一致。
    secondary_remote_plan_xyz = _interpolate_xyz(
        lower_endpoint_xyz[0],
        lower_endpoint_xyz[1],
        _projection_ratio(
            secondary_points[secondary_remote_index], lower_points
        ),
    )
    upper_remote_xyz = (
        secondary_remote_plan_xyz[0],
        secondary_remote_plan_xyz[1],
        secondary_joint_xyz[2],
    )

    # endpoint_ids/endpoint_xyz 均保持与原二维端点列表相同的下标顺序，
    # 后续正视图、底视图和顶视图可以直接复用通用的端点标记流程。
    endpoint_ids = {
        lower_rod: [None, None],
        diagonal_rod: [None, None],
        secondary_rod: [None, None],
    }
    endpoint_ids[lower_rod][tower_lower_index] = str(tower_lower_id)
    endpoint_ids[lower_rod][lower_remote_index] = lower_remote_id
    endpoint_ids[diagonal_rod][tower_upper_index] = str(tower_upper_id)
    endpoint_ids[diagonal_rod][diagonal_joint_index] = diagonal_joint_id
    endpoint_ids[secondary_rod][secondary_joint_index] = secondary_joint_id
    endpoint_ids[secondary_rod][secondary_remote_index] = upper_remote_id

    endpoint_xyz = {
        lower_rod: tuple(lower_endpoint_xyz),
        diagonal_rod: tuple(diagonal_endpoint_xyz),
        secondary_rod: (None, None),
    }
    secondary_endpoint_xyz = [None, None]
    secondary_endpoint_xyz[secondary_joint_index] = secondary_joint_xyz
    secondary_endpoint_xyz[secondary_remote_index] = upper_remote_xyz
    endpoint_xyz[secondary_rod] = tuple(secondary_endpoint_xyz)

    new_nodes = [
        (diagonal_joint_id, diagonal_joint_xyz),
        (secondary_joint_id, secondary_joint_xyz),
        (upper_remote_id, upper_remote_xyz),
    ]
    return {
        "roles": roles,
        # 03/05 继续向外重建时，把靠塔担架的副杆外端作为上连接点、
        # 水平主杆外端作为下连接点，顺序与 pj[index 0/1] 约定一致。
        "outer_connection_group": [
            [upper_remote_id, list(map(float, upper_remote_xyz))],
            [lower_remote_id, list(map(float, lower_remote_xyz))],
        ],
        "endpoint_ids": {
            rod_id: tuple(node_ids) for rod_id, node_ids in endpoint_ids.items()
        },
        "endpoint_xyz": endpoint_xyz,
        # 二类节点的引用端点保持“框架内侧/连接侧 -> 外侧”的统一顺序，
        # 不受 04、06 二维坐标端点排列方向影响。
        "reference_endpoint_ids": {
            lower_rod: (str(tower_lower_id), lower_remote_id),
            diagonal_rod: (str(tower_upper_id), diagonal_joint_id),
            secondary_rod: (secondary_joint_id, upper_remote_id),
        },
        "new_nodes": [
            {
                "node_id": node_id,
                "node_type": 11,
                "symmetry_type": 2,
                "X": round(float(xyz[0]), 3),
                "Y": round(float(xyz[1]), 3),
                "Z": round(float(xyz[2]), 3),
            }
            for node_id, xyz in new_nodes
        ],
    }


def build_zhiliu_outer_front_class1(
    coordinates_front_data,
    connection_group,
    jiandian_id,
    lower_remote_xyz,
    upper_remote_xyz,
    connection_side,
):
    """生成直流塔 03/05 外层担架正视图的两根一类主杆。"""
    if not connection_group or len(connection_group) < 2:
        raise ValueError("直流塔外层担架缺少内层担架连接点")

    primary_ids = detect_main_rods_enhanced(coordinates_front_data)
    if len(primary_ids) != 2:
        raise ValueError("直流塔外层担架正视图未识别到两根一类主杆")

    def vertical_ratio(rod_id):
        point1, point2 = coordinates_front_data[rod_id]
        length = _dist_points(point1, point2)
        if math.isclose(length, 0.0, abs_tol=1e-9):
            raise ValueError(f"正视图杆件 {rod_id} 是零长度杆件")
        return abs(point2[1] - point1[1]) / length

    # 两根杆都近似水平，以正视图平均纵坐标区分上、下主杆。
    lower_rod = max(
        primary_ids,
        key=lambda rod_id: sum(point[1] for point in coordinates_front_data[rod_id]),
    )
    upper_rod = next(rod_id for rod_id in primary_ids if rod_id != lower_rod)
    if vertical_ratio(lower_rod) > 0.1 or vertical_ratio(upper_rod) > 0.1:
        raise ValueError("直流塔外层担架正视图的一类主杆不是近似水平杆")

    # 03 的连接端在右侧、05 的连接端在左侧。connection_group 来自已经
    # 完成重建的 04/06，而不是塔身的原始拼接点。
    upper_connection_id, upper_connection_xyz = connection_group[0]
    lower_connection_id, lower_connection_xyz = connection_group[1]
    lower_remote_id = str(jiandian_id + 20)
    upper_remote_id = str(jiandian_id + 30)

    endpoint_ids = {}
    endpoint_xyz = {}
    # 两根主杆的内端沿用 04/06 传来的真实 XYZ；两个外端分别使用
    # 底视图和顶视图按旧逻辑算出的真实 XYZ，从而保留四个独立端点。
    for rod_id, connection_id, connection_xyz, remote_id, remote_xyz in (
        (
            lower_rod, lower_connection_id, lower_connection_xyz,
            lower_remote_id, lower_remote_xyz,
        ),
        (
            upper_rod, upper_connection_id, upper_connection_xyz,
            upper_remote_id, upper_remote_xyz,
        ),
    ):
        connection_index = _endpoint_index_on_side(
            coordinates_front_data[rod_id], connection_side
        )
        remote_index = 1 - connection_index
        rod_endpoint_ids = [None, None]
        rod_endpoint_xyz = [None, None]
        rod_endpoint_ids[connection_index] = str(connection_id)
        rod_endpoint_ids[remote_index] = remote_id
        rod_endpoint_xyz[connection_index] = tuple(map(float, connection_xyz))
        rod_endpoint_xyz[remote_index] = tuple(map(float, remote_xyz))
        endpoint_ids[rod_id] = tuple(rod_endpoint_ids)
        endpoint_xyz[rod_id] = tuple(rod_endpoint_xyz)

    roles = {
        "main_rods": (lower_rod, upper_rod),
        "all_rods": (lower_rod, upper_rod),
    }
    return {
        "roles": roles,
        "endpoint_ids": endpoint_ids,
        "endpoint_xyz": endpoint_xyz,
        "reference_endpoint_ids": {
            lower_rod: (str(lower_connection_id), lower_remote_id),
            upper_rod: (str(upper_connection_id), upper_remote_id),
        },
        "new_nodes": [{
            "node_id": upper_remote_id,
            "node_type": 11,
            "symmetry_type": 2,
            "X": round(float(upper_remote_xyz[0]), 3),
            "Y": round(float(upper_remote_xyz[1]), 3),
            "Z": round(float(upper_remote_xyz[2]), 3),
        }],
    }


def build_zhiliu_near_front_second_class(
    coordinates_front_data,
    class1_result,
    id_prefix,
    threshold=150,
):
    """生成 04/06 正视图两片框架内的二类节点和二类杆件。

    第一片位于水平主杆与斜主杆之间，第二片位于水平主杆与一类
    副杆之间。两片框架共用的节点会复用同一编号，共用杆件按杆件
    编号去重。
    """
    roles = class1_result["roles"]
    lower_rod, diagonal_rod = roles["main_rods"]
    secondary_rod = roles["secondary_rod"]
    class1_rod_ids = set(roles["all_rods"])
    endpoint_ids = class1_result["endpoint_ids"]
    endpoint_xyz = class1_result["endpoint_xyz"]
    reference_endpoint_ids = class1_result["reference_endpoint_ids"]

    # 每根一类边界杆使用独立节点号段，避免两片框架的节点编号冲突。
    boundary_groups = {
        lower_rod: "191",
        diagonal_rod: "193",
        secondary_rod: "195",
    }
    node_counters = {rod_id: 0 for rod_id in boundary_groups}
    known_nodes = []
    for rod_id in roles["all_rods"]:
        for point, node_id in zip(
            coordinates_front_data[rod_id], endpoint_ids[rod_id]
        ):
            known_nodes.append((point, str(node_id)))

    created_nodes = []

    def resolve_boundary_node(rod_id, point):
        # 两片框架可能在水平主杆上命中同一点；先按二维距离复用节点。
        for existing_point, node_id in known_nodes:
            if _dist_points(point, existing_point) < threshold:
                return node_id

        node_counters[rod_id] += 1
        node_id = (
            f"{id_prefix}{boundary_groups[rod_id]}"
            f"{node_counters[rod_id]}0"
        )
        ratio = _projection_ratio(point, coordinates_front_data[rod_id])
        xyz = _interpolate_xyz(
            endpoint_xyz[rod_id][0], endpoint_xyz[rod_id][1], ratio
        )
        reference_start, reference_end = reference_endpoint_ids[rod_id]
        # 延续旧数据格式：X 保存插值得到的真实值，Y/Z 保存该节点所在
        # 一类杆的两个真实端点引用，由下游根据引用恢复完整三维坐标。
        created_nodes.append({
            "node_id": node_id,
            "node_type": 12,
            "symmetry_type": 2,
            "X": round(float(xyz[0]), 3),
            "Y": f"1{reference_start}",
            "Z": f"1{reference_end}",
        })
        known_nodes.append((point, node_id))
        return node_id

    members_by_id = {}
    member_to_nodes = {}
    # 分别搜索“水平主杆—斜主杆”和“水平主杆—副杆”两片框架。
    for boundary_a, boundary_b in (
        (lower_rod, diagonal_rod),
        (lower_rod, secondary_rod),
    ):
        segment_a = coordinates_front_data[boundary_a]
        segment_b = coordinates_front_data[boundary_b]
        for member_id, member_points in coordinates_front_data.items():
            if member_id in class1_rod_ids:
                continue

            point0, point1 = member_points
            connects_boundaries = (
                _is_point_near_segment(point0, segment_a, threshold)
                and _is_point_near_segment(point1, segment_b, threshold)
            ) or (
                _is_point_near_segment(point1, segment_a, threshold)
                and _is_point_near_segment(point0, segment_b, threshold)
            )
            if not connects_boundaries:
                continue

            point_a = _line_intersection(member_points, segment_a)
            point_b = _line_intersection(member_points, segment_b)
            if point_a is None or point_b is None:
                continue
            node_ids = (
                resolve_boundary_node(boundary_a, point_a),
                resolve_boundary_node(boundary_b, point_b),
            )
            member_key = str(member_id)
            # 同一杆件可能同时落入两片框架的阈值范围，按原杆件编号去重。
            if member_key in members_by_id:
                continue
            member_to_nodes[member_id] = list(node_ids)
            members_by_id[member_key] = {
                "member_id": member_key,
                "node1_id": node_ids[0],
                "node2_id": node_ids[1],
                "symmetry_type": 2,
            }

    return {
        "new_nodes": created_nodes,
        "new_members": list(members_by_id.values()),
        "member_to_nodes": member_to_nodes,
    }


def build_zhiliu_outer_front_second_class(
    coordinates_front_data,
    class1_result,
    id_prefix,
    threshold=150,
):
    """生成 03/05 正视图上下两根一类主杆之间的二类结构。"""
    lower_rod, upper_rod = class1_result["roles"]["main_rods"]
    class1_rod_ids = set(class1_result["roles"]["all_rods"])
    endpoint_ids = class1_result["endpoint_ids"]
    endpoint_xyz = class1_result["endpoint_xyz"]
    reference_endpoint_ids = class1_result["reference_endpoint_ids"]
    boundary_groups = {lower_rod: "191", upper_rod: "193"}
    node_counters = {rod_id: 0 for rod_id in boundary_groups}
    known_nodes = []
    for rod_id in (lower_rod, upper_rod):
        for point, node_id in zip(
            coordinates_front_data[rod_id], endpoint_ids[rod_id]
        ):
            known_nodes.append((point, str(node_id)))

    created_nodes = []

    def resolve_boundary_node(rod_id, point):
        for existing_point, node_id in known_nodes:
            if _dist_points(point, existing_point) < threshold:
                return node_id

        node_counters[rod_id] += 1
        node_id = (
            f"{id_prefix}{boundary_groups[rod_id]}"
            f"{node_counters[rod_id]}0"
        )
        ratio = _projection_ratio(point, coordinates_front_data[rod_id])
        xyz = _interpolate_xyz(
            endpoint_xyz[rod_id][0], endpoint_xyz[rod_id][1], ratio
        )
        reference_start, reference_end = reference_endpoint_ids[rod_id]
        created_nodes.append({
            "node_id": node_id,
            "node_type": 12,
            "symmetry_type": 2,
            "X": round(float(xyz[0]), 3),
            "Y": f"1{reference_start}",
            "Z": f"1{reference_end}",
        })
        known_nodes.append((point, node_id))
        return node_id

    members = []
    member_to_nodes = {}
    # 03/05 只有上下两根水平一类主杆，二类杆只需搜索跨接两杆的杆件。
    lower_segment = coordinates_front_data[lower_rod]
    upper_segment = coordinates_front_data[upper_rod]
    for member_id, member_points in coordinates_front_data.items():
        if member_id in class1_rod_ids:
            continue
        point0, point1 = member_points
        connects_boundaries = (
            _is_point_near_segment(point0, lower_segment, threshold)
            and _is_point_near_segment(point1, upper_segment, threshold)
        ) or (
            _is_point_near_segment(point1, lower_segment, threshold)
            and _is_point_near_segment(point0, upper_segment, threshold)
        )
        if not connects_boundaries:
            continue
        lower_point = _line_intersection(member_points, lower_segment)
        upper_point = _line_intersection(member_points, upper_segment)
        if lower_point is None or upper_point is None:
            continue
        node_ids = (
            resolve_boundary_node(lower_rod, lower_point),
            resolve_boundary_node(upper_rod, upper_point),
        )
        member_to_nodes[member_id] = list(node_ids)
        members.append({
            "member_id": str(member_id),
            "node1_id": node_ids[0],
            "node2_id": node_ids[1],
            "symmetry_type": 2,
        })

    return {
        "new_nodes": created_nodes,
        "new_members": members,
        "member_to_nodes": member_to_nodes,
        "nodes_2d": [
            {"node_id": node_id, "point_2d": point}
            for point, node_id in known_nodes
        ],
    }


def build_zhiliu_near_projected_class1_frames(class1_result):
    """返回 04/06 底视图、顶视图所投影的一类杆端点。

    底视图投影水平主杆，顶视图投影倾斜主杆。每个视图的第二根
    投影主杆使用第一根主杆端点关于对称轴生成的 ``+2`` 节点。
    """
    lower_rod, diagonal_rod = class1_result["roles"]["main_rods"]

    def frame_for(front_rod_id):
        # 第一根投影杆复用正视图一类节点；另一根杆使用节点号 +2，
        # 表示关于担架对称轴生成的对应节点，与原三视图编号规则一致。
        primary_ids = tuple(
            str(node_id)
            for node_id in class1_result["endpoint_ids"][front_rod_id]
        )
        return {
            "primary_endpoint_ids": primary_ids,
            "symmetric_endpoint_ids": tuple(
                str(int(node_id) + 2) for node_id in primary_ids
            ),
            "endpoint_xyz": class1_result["endpoint_xyz"][front_rod_id],
        }

    return {
        "bottom": frame_for(lower_rod),
        "overhead": frame_for(diagonal_rod),
    }
