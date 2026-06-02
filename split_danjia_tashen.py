"""
区分担架杆件和塔身杆件。

逻辑：
1. 担架的一类杆件：在所有杆件中，倾角 < 45°（即 |dy| < |dx|）的杆件里取最长的两根。
2. 担架的二类杆件：两个端点分别落在两根一类杆件上（允许在同一根上）。
3. 其余杆件归为塔身。
"""

import math


YUZHI = 150  # 判断点是否在杆件上的像素阈值，与项目其他模块保持一致


def segment_length(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def is_horizontal_like(p1, p2):
    """倾角 < 45° 视为横向杆件（水平倾斜不超过 45°）。"""
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    return dx > dy


def point_on_segment(pt, seg_p1, seg_p2, tol=YUZHI):
    """判断点 pt 是否在线段 seg_p1-seg_p2 上（允许 tol 像素垂直误差）。"""
    x, y = pt
    x1, y1 = seg_p1
    x2, y2 = seg_p2

    # 端点重合直接命中
    if math.hypot(x - x1, y - y1) <= tol or math.hypot(x - x2, y - y2) <= tol:
        return True

    dx, dy = x2 - x1, y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(x - x1, y - y1) <= tol

    # 投影参数 t：0 表示 p1，1 表示 p2
    t = ((x - x1) * dx + (y - y1) * dy) / seg_len_sq
    if t < 0 or t > 1:
        return False

    # 投影点到原点距离 = 垂直距离
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(x - proj_x, y - proj_y) <= tol


def detect_danjia_main_rods(coordinates_data):
    """从所有杆件中挑选担架的两根一类杆件：横向（倾角<45°）中最长的两根。"""
    horizontals = []
    for rod_id, (p1, p2) in coordinates_data.items():
        if is_horizontal_like(p1, p2):
            horizontals.append((rod_id, segment_length(p1, p2)))

    if len(horizontals) < 2:
        return []

    horizontals.sort(key=lambda x: x[1], reverse=True)
    return [horizontals[0][0], horizontals[1][0]]


def split_danjia_tashen(coordinates_data):
    """
    返回 (danjia_dict, tashen_dict)。
    danjia 包含两根一类杆件以及两端都落在一类杆件上的二类杆件。
    """
    main_ids = detect_danjia_main_rods(coordinates_data)
    if len(main_ids) < 2:
        # 找不到一类杆件时，全部视为塔身，避免误判
        return {}, dict(coordinates_data)

    main_segs = [coordinates_data[rid] for rid in main_ids]

    danjia = {rid: coordinates_data[rid] for rid in main_ids}
    tashen = {}

    for rod_id, (p1, p2) in coordinates_data.items():
        if rod_id in danjia:
            continue
        p1_on_main = any(point_on_segment(p1, s[0], s[1]) for s in main_segs)
        p2_on_main = any(point_on_segment(p2, s[0], s[1]) for s in main_segs)
        if p1_on_main and p2_on_main:
            danjia[rod_id] = (p1, p2)
        else:
            tashen[rod_id] = (p1, p2)

    return danjia, tashen


if __name__ == "__main__":
    coordinatesFront_data = {
        101: [(289, 2850), (528, 150)],
        103: [(885, 150), (1125, 2850)],
        105: [(939, 750), (3710, 1350)],
        107: [(992, 1350), (3710, 1350)],
        109: [(707, 2442), (707, 2850)],
        111: [(355, 2100), (1125, 2850)],
        112: [(289, 2850), (1059, 2100)],
        113: [(355, 2100), (992, 1350)],
        114: [(422, 1350), (1059, 2100)],
        115: [(422, 1350), (992, 1350)],
        119_1: [(422, 1350), (939, 750)],
        119_2: [(475, 750), (992, 1350)],
        120: [(475, 750), (939, 750)],
        124: [(992, 1350), (1853, 947)],
        125: [(1853, 947), (1899, 1350)],
        126: [(1899, 1350), (2780, 1148)],
        127: [(2780, 1148), (2804, 1350)],
        130: [(475, 750), (885, 150)],
        131: [(528, 150), (885, 150)],
    }

    danjia_coordinatesFront_data, tashen_coordinatesFront_data = split_danjia_tashen(
        coordinatesFront_data
    )

    print("担架一类杆件:", detect_danjia_main_rods(coordinatesFront_data))

    print("\ndanjia_coordinatesFront_data = {")
    for k, v in danjia_coordinatesFront_data.items():
        print(f"    {k!r}: [{tuple(v[0])}, {tuple(v[1])}],")
    print("}")

    print("\ntashen_coordinatesFront_data = {")
    for k, v in tashen_coordinatesFront_data.items():
        print(f"    {k!r}: [{tuple(v[0])}, {tuple(v[1])}],")
    print("}")
