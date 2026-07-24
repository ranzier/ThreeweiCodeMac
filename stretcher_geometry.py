import math


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
