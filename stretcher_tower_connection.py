"""
「上/干字型」担架拼接点识别（T7833、781、7837）。

拼接点这样识别：
1. 根据正视图两根一类杆件的展开/收拢关系确定塔身连接侧，再按连接端Y确定上下杆；
2. 到塔身正视图的**横杆**里找相同二维坐标的端点，拿到该横杆的塔身 member_id；
3. 取该横杆 ganjian 行的 -x 左侧节点（node1）和 +x 右侧节点（node2）作为两侧拼接点，
   三维坐标优先从塔身 jiedian 取；任意一侧缺少数值坐标时，由另一侧镜像补齐。

只依赖塔身返回的 jiedian + ganjian，不需要塔身重建内部的 final_coords_map。

产出的 pinjie 直接喂给 xintrans.trans 消费：每 4 个一组对应一个担架，
组内顺序 [右上, 右下, 左上, 左下]，左右两组均携带各自真实的塔身节点编号。
"""

import os
import glob
import math

from get_first_ganjian_id import detect_main_rods_enhanced


def _endpoint_on_side(segment, side):
    """返回线段在指定左右侧的端点。"""
    if not segment or len(segment) != 2:
        raise ValueError("一类杆件必须包含两个二维端点")
    selector = min if side == "left" else max
    return selector(segment, key=lambda point: point[0])


def get_main_rod_connection_geometry(coordinates_data, rod_a_id, rod_b_id):
    """
    根据正视图两根一类杆件确定塔身连接侧及上下杆。

    两杆在展开侧的端点间距大，在收拢尖点侧的端点间距小，因此展开侧
    就是连接塔身的一侧。图像坐标 Y 轴向下，连接端 Y 较小者为上杆。
    """
    try:
        rod_a = coordinates_data[rod_a_id]
        rod_b = coordinates_data[rod_b_id]
    except KeyError as exc:
        raise ValueError(f"正视图缺少一类杆件 {exc.args[0]}") from exc

    endpoints = {
        side: (
            _endpoint_on_side(rod_a, side),
            _endpoint_on_side(rod_b, side),
        )
        for side in ("left", "right")
    }
    gaps = {
        side: math.dist(points[0], points[1])
        for side, points in endpoints.items()
    }
    if math.isclose(gaps["left"], gaps["right"], rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            f"正视图一类杆件 {rod_a_id}、{rod_b_id} 无法区分连接侧和收拢侧"
        )

    connection_side = max(gaps, key=gaps.get)
    upper_rod_id, lower_rod_id = sorted(
        (rod_a_id, rod_b_id),
        key=lambda rod_id: _endpoint_on_side(
            coordinates_data[rod_id], connection_side
        )[1],
    )
    return connection_side, upper_rod_id, lower_rod_id


def _read_front(txt_path):
    """
    读取一个坐标 txt，返回其正视图杆件字典 {member_id_str: [(x1,y1),(x2,y2)]}。

    复用塔身重建的正则解析器 _parse_block_dict，而非 exec：
    txt 里形如 119_1 的 key 若用 exec 会被 Python 当成数字分隔符解析成整数 1191，
    与塔身 final_coords_map 保留的字符串 key（F_119_1）对不上。正则解析保持字符串 key 一致。
    """
    # 延迟导入，避免只使用几何辅助函数的 xintrans 提前依赖 numpy 等塔身解析依赖。
    from dual_view_core import _parse_block_dict

    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return _parse_block_dict(text, "front")


def _left_end(front, mid):
    """取杆件 mid 的左端点（x 较小者），返回 (二维点, 端点index)。"""
    p1, p2 = front[mid]  # [(x1,y1),(x2,y2)]
    return (p1, 0) if p1[0] <= p2[0] else (p2, 1)


def _right_end(front, mid):
    """取杆件 mid 的右端点（x 较大者），返回 (二维点, 端点index)。与 _left_end 对称。"""
    p1, p2 = front[mid]  # [(x1,y1),(x2,y2)]
    return (p1, 0) if p1[0] >= p2[0] else (p2, 1)


def _pick_end(front, mid, side):
    """按 side（"left"/"right"）取杆件 mid 的连接端点。"""
    return _right_end(front, mid) if side == "right" else _left_end(front, mid)


def _base_id(k):
    """去掉 F_/R_ 前缀与 _1/_2 拼接后缀，得到基础 member_id。例：F_119_1 -> 119。"""
    k = str(k).replace("F_", "").replace("R_", "")
    return k.split("_", 1)[0]


def _is_horizontal(seg, tol_y=20.0):
    """判断塔身杆件是否为横杆（两端 y 近似相等）。担架连接点落在横杆上。"""
    return abs(seg[0][1] - seg[1][1]) <= tol_y


def _match_tashen_horizontal(pt2d, tashen_fronts, tol):
    """
    在塔身正视图的**横杆**里找与 pt2d 重合的端点。
    只匹配横杆，避免斜杆（如 113）在同一二维点上的深度歧义与悬空节点。
    tashen_fronts: [(member_id, [(x1,y1),(x2,y2)]), ...]
    返回 (塔身member_id, 重合端点index)。
    """
    best = None
    for mid, seg in tashen_fronts:
        if not _is_horizontal(seg):
            continue
        for idx, (x, y) in enumerate(seg):
            d = ((x - pt2d[0]) ** 2 + (y - pt2d[1]) ** 2) ** 0.5
            if d <= tol and (best is None or d < best[0]):
                best = (d, mid, idx)
    if best is None:
        raise KeyError(f"塔身正视图横杆中未匹配到担架拼接点二维坐标 {pt2d}")
    return best[1], best[2]


def _right_nodes_of_member(mid, ganjian_rows_by_base):
    """
    取横杆 mid 的 (-x 左节点, +x 右节点) 编号。
    横杆 ganjian 行约定 node1↔idx0(-x)、node2↔idx1(+x)；
    多行时优先 symmetry_type==2 的正视图行（拼接/对称拆分会产生 sym1 的镜像行）。
    """
    rows = ganjian_rows_by_base.get(_base_id(mid), [])
    if not rows:
        return None, None
    sym2 = [r for r in rows if int(r.get("symmetry_type", 0)) == 2]
    chosen = sym2[0] if sym2 else rows[0]
    return str(chosen.get("node1_id")), str(chosen.get("node2_id"))


def _node_xyz_from_jiedian(node_id, node_xyz):
    """从 jiedian 坐标表取节点三维坐标；仅接受数值型（node_type 11）坐标。"""
    v = node_xyz.get(str(node_id))
    if v is None:
        return None
    try:
        return [float(v[0]), float(v[1]), float(v[2])]
    except (TypeError, ValueError):
        return None  # node_type 12 的引用式坐标（非数值）不可用


def build_stretcher_tower_pinjie(danjia_dir, tashen_dir, jiedian_tashen, ganjian_tashen, tol=1.0,
                                 longest_main_rods=False):
    """
    为构建 xintrans 消费格式的 pinjie（长度 = 担架数 × 4）。
    每个元素形如 [node_id_str, [x, y, z]]。

    识别规则：
      两根一类杆件展开较宽的一侧为塔身连接侧；连接端Y较小者为上杆、较大者为下杆。
      两个连接端点 -> 塔身正视图**横杆**上的重合端点 -> 分别取该横杆 -x 左侧节点(node1)
      和 +x 右侧节点(node2)。
      三维坐标优先直接查 jiedian；任意一侧查不到时，用另一侧坐标关于 X=0 镜像补齐。

    参数:
        danjia_dir: 担架坐标目录（含 0{i}.txt）
        tashen_dir: 塔身坐标目录（含正视图 txt）
        jiedian_tashen: 塔身节点列表，用于取连接点三维坐标
        ganjian_tashen: 塔身杆件列表，用于把横杆映射回 +x 连接节点编号
        tol: 二维坐标匹配容差（原始坐标为整数，默认 1.0 兜底）
        longest_main_rods: 已弃用的兼容参数；一类杆件始终使用通用规则识别。
    """
    # 汇总塔身所有正视图杆件的二维坐标
    tashen_fronts = []
    for fp in sorted(glob.glob(os.path.join(tashen_dir, "*.txt"))):
        for mid, seg in _read_front(fp).items():
            tashen_fronts.append((str(mid), seg))

    # member_id(base) -> [ganjian 行, ...]（同一 base 可能有对称/拼接多行）
    ganjian_rows_by_base = {}
    for g in ganjian_tashen:
        ganjian_rows_by_base.setdefault(_base_id(g.get("member_id")), []).append(g)

    # node_id -> (X,Y,Z)
    node_xyz = {str(n.get("node_id")): (n.get("X"), n.get("Y"), n.get("Z")) for n in jiedian_tashen}

    def endpoint(pt2d):
        """担架某连接端二维坐标 -> 左、右两侧各自的塔身节点编号与三维坐标。"""
        mid, _idx = _match_tashen_horizontal(pt2d, tashen_fronts, tol)
        left_node, right_node = _right_nodes_of_member(mid, ganjian_rows_by_base)
        if left_node is None or right_node is None:
            raise KeyError(f"塔身横杆 {mid} 在 ganjian 中缺少左右端节点")

        left_xyz = _node_xyz_from_jiedian(left_node, node_xyz)
        right_xyz = _node_xyz_from_jiedian(right_node, node_xyz)
        if left_xyz is None and right_xyz is None:
            raise KeyError(f"横杆 {mid} 的节点 {left_node}/{right_node} 均无数值坐标")
        if left_xyz is None:
            left_xyz = [-abs(right_xyz[0]), right_xyz[1], right_xyz[2]]
        if right_xyz is None:
            right_xyz = [abs(left_xyz[0]), left_xyz[1], left_xyz[2]]

        left_xyz = [-abs(left_xyz[0]), left_xyz[1], left_xyz[2]]
        right_xyz = [abs(right_xyz[0]), right_xyz[1], right_xyz[2]]
        return left_node, left_xyz, right_node, right_xyz

    danjia_txts = sorted(glob.glob(os.path.join(danjia_dir, "*.txt")))
    pinjie = []
    for txt in danjia_txts:
        front = _read_front(txt)
        ids = detect_main_rods_enhanced(front)
        if len(ids) < 2:
            raise ValueError(f"担架 {os.path.basename(txt)} 正视图未识别到两个一类杆件")
        side, up_id, down_id = get_main_rod_connection_geometry(
            front, ids[0], ids[1]
        )
        up2d, _ = _pick_end(front, up_id, side)
        down2d, _ = _pick_end(front, down_id, side)

        lu_node, lx_u, ru_node, rx_u = endpoint(up2d)
        ld_node, lx_d, rd_node, rx_d = endpoint(down2d)

        # 组内顺序：右上, 右下, 左上, 左下
        pinjie += [
            [ru_node, rx_u],
            [rd_node, rx_d],
            [lu_node, lx_u],
            [ld_node, lx_d],
        ]

    return pinjie
