"""Regression check for single-view front/side joints on tier-1 rods."""

import math

import sv_class2_transform as transform
from single_view_processor import _resolve_single_view_points


def run_tests() -> None:
    coordinates = {
        "101": [(-100.0, 0.0), (-50.0, 1000.0)],
        "103": [(100.0, 0.0), (50.0, 1000.0)],
        # The two endpoints meet opposite main rods at different heights.
        # Rotating the right endpoint creates side node 10421 inside rod 101.
        "104": [(-60.0, 800.0), (75.0, 500.0)],
    }

    members, nodes = transform.single_view0201(coordinates, front_only=False)
    left_main_endpoints = {
        str(member[key])
        for member in members
        if str(member["member_id"]).split("_", 1)[0] == "101"
        for key in ("node1_id", "node2_id")
    }

    assert {"10110", "10410", "10120"}.issubset(left_main_endpoints), members
    points = _resolve_single_view_points(nodes)
    start = points["10110"]
    end = points["10120"]
    direction = tuple(end[index] - start[index] for index in range(3))
    length_squared = sum(value * value for value in direction)
    for node_id in left_main_endpoints:
        point = points[node_id]
        parameter = sum(
            (point[index] - start[index]) * direction[index]
            for index in range(3)
        ) / length_squared
        projected = tuple(
            start[index] + parameter * direction[index]
            for index in range(3)
        )
        assert math.dist(point, projected) <= 1e-9, (node_id, point, projected)
    side_members = [
        member
        for member in members
        if str(member["member_id"]).startswith("104")
    ]
    assert any(
        left_main_endpoints.intersection(
            {str(row["node1_id"]), str(row["node2_id"])}
        )
        for row in side_members
    ), side_members

    # A point can be inside a horizontal/X member while still lying within
    # the drawing tolerance of a tier-1 rod.  Host class must win before the
    # interior-point heuristic, otherwise its type-12 references are built
    # from the front horizontal member and the rotated side node is misplaced.
    host_priority_coordinates = {
        "101": [(-300.0, 0.0), (-300.0, 1000.0)],
        "103": [(300.0, 0.0), (300.0, 1000.0)],
        "104": [(-300.0, 500.0), (300.0, 500.0)],
        "105": [(-200.0, 500.0), (0.0, 500.0)],
    }
    priority_members, _ = transform.single_view0201(
        host_priority_coordinates,
        front_only=True,
        main_rod_ids=["101", "103"],
    )
    tier3_member = next(
        member
        for member in priority_members
        if str(member["member_id"]) == "105"
    )
    assert tier3_member["node1_id"] == "10410", tier3_member

    # Front and side attachments on the same tier-1 host and within EPS must
    # share the front canonical node instead of producing two nearby nodes.
    close_attachment_coordinates = {
        "201": [(-100.0, 0.0), (-50.0, 1000.0)],
        "203": [(100.0, 0.0), (50.0, 1000.0)],
        "204": [(-75.0, 500.0), (72.5, 550.0)],
    }
    close_members, _ = transform.single_view0201(
        close_attachment_coordinates,
        front_only=False,
        main_rod_ids=["201", "203"],
    )
    front_member = next(
        member for member in close_members if str(member["member_id"]) == "204"
    )
    side_member = next(
        member for member in close_members if str(member["member_id"]) == "204_2"
    )
    assert {
        str(front_member["node1_id"]),
        str(front_member["node2_id"]),
    }.intersection(
        {str(side_member["node1_id"]), str(side_member["node2_id"])}
    ), (front_member, side_member)

    print("single-view cross-face tier-1 joint: passed")


if __name__ == "__main__":
    run_tests()
