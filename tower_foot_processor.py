"""Independent reconstruction for a half-front tower-foot drawing.

The special ``59_front.txt`` drawing contains only one half of one elevation.
It must not enter either the normal single-view or dual-view reconstruction
pipelines. This module completes that elevation by reflection, creates the
orthogonal elevation by a 90-degree rotation, and reuses the real interface
nodes exported by drawing 13.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from dual_view_core import load_and_parse_data

Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]
CoordDict = Dict[str, List[Point2D]]

FOOT_FILENAME = "59_front.txt"
CONNECTION_DRAWING_PREFIX = "13"
COORDINATE_DIGITS = 6


@dataclass(frozen=True)
class FootInterface:
    """Three explicit corners of the drawing-13 connection layer."""

    center_x: float
    center_y: float
    z: float
    half_x: float
    half_y: float
    corner_node_ids: Dict[Tuple[int, int], str]
    front_connection_node_ids: Tuple[str, str]
    front_connection_points: Tuple[Point3D, Point3D]
    side_connection_node_ids: Tuple[str, str]
    side_connection_points: Tuple[Point3D, Point3D]


def is_half_front_only_file(path: str) -> bool:
    """Return whether *path* is the dedicated half-front tower-foot file."""

    if os.path.basename(path).lower() != FOOT_FILENAME or not os.path.isfile(path):
        return False
    front, side = load_and_parse_data(path)
    return bool(front) and not side


def _numeric_xyz(node: dict) -> Optional[Point3D]:
    try:
        return float(node["X"]), float(node["Y"]), float(node["Z"])
    except (KeyError, TypeError, ValueError):
        return None


def _connection_node_ids(members: Iterable[dict]) -> set[str]:
    result: set[str] = set()
    for member in members:
        member_id = str(member.get("member_id", ""))
        if not member_id.startswith(CONNECTION_DRAWING_PREFIX):
            continue
        result.add(str(member.get("node1_id", "")))
        result.add(str(member.get("node2_id", "")))
    result.discard("")
    return result


def _expanded_node_points(nodes: Iterable[dict]) -> Dict[str, Point3D]:
    """Resolve real/reference nodes and their symmetry-generated companions."""

    points: Dict[str, Point3D] = {}
    pending: List[dict] = []

    def plus_suffix(node_id: str, delta: int) -> str:
        suffix = node_id[-2:]
        if not suffix.isdigit():
            return node_id
        return f"{node_id[:-2]}{int(suffix) + delta:02d}"

    def add_with_symmetry(node_id: str, point: Point3D, symmetry_type: int) -> None:
        points[node_id] = point
        deltas = {1: (1,), 2: (2,), 3: (3,), 4: (1, 2, 3)}.get(
            symmetry_type, ()
        )
        for delta in deltas:
            x, y, z = point
            symmetric = (
                -x if delta in (1, 3) else x,
                -y if delta in (2, 3) else y,
                z,
            )
            points[plus_suffix(node_id, delta)] = symmetric

    raw_nodes = list(nodes)
    for node in raw_nodes:
        node_id = str(node.get("node_id", ""))
        if not node_id:
            continue
        if int(node.get("node_type", 0) or 0) == 11:
            point = _numeric_xyz(node)
            if point is not None:
                add_with_symmetry(
                    node_id, point, int(node.get("symmetry_type", 0) or 0)
                )
        else:
            pending.append(node)

    while pending:
        unresolved: List[dict] = []
        resolved_count = 0
        for node in pending:
            references: List[str] = []
            real_axis = -1
            real_value = 0.0
            for axis_index, axis in enumerate(("X", "Y", "Z")):
                value = node.get(axis)
                if isinstance(value, str) and value.startswith("1"):
                    references.append(value[1:])
                else:
                    try:
                        real_value = float(value)
                        real_axis = axis_index
                    except (TypeError, ValueError):
                        real_axis = -1
                        break
            if (
                real_axis < 0
                or len(references) != 2
                or any(reference not in points for reference in references)
            ):
                unresolved.append(node)
                continue
            start, end = points[references[0]], points[references[1]]
            span = end[real_axis] - start[real_axis]
            if abs(span) <= 1e-9:
                unresolved.append(node)
                continue
            ratio = (real_value - start[real_axis]) / span
            coords = tuple(
                real_value
                if index == real_axis
                else start[index] + ratio * (end[index] - start[index])
                for index in range(3)
            )
            add_with_symmetry(
                str(node["node_id"]),
                coords,
                int(node.get("symmetry_type", 0) or 0),
            )
            resolved_count += 1
        if resolved_count == 0:
            break
        pending = unresolved

    return points


def find_drawing_13_interface(
    members: Iterable[dict],
    nodes: Iterable[dict],
    z_tolerance: float = 0.08,
    foot_main_slope: Optional[float] = None,
) -> FootInterface:
    """Find the wide outer layer of drawing 13 used by the tower foot.

    Single-view reconstruction explicitly exports three corners of a square
    layer; the fourth is implied by symmetry. The wider of the two terminal
    layers is the physical outer end of drawing 13 and therefore the tower-foot
    interface.
    """

    member_records = list(members)
    endpoint_ids = _connection_node_ids(member_records)
    node_points = _expanded_node_points(nodes)
    candidates = [
        (node_id, node_points[node_id])
        for node_id in endpoint_ids
        if node_id in node_points
    ]
    if not candidates:
        raise ValueError("塔脚连接失败：13号图纸没有可用的真实节点")

    z_levels = sorted({point[2] for _, point in candidates})
    terminal_levels = [z_levels[0]] if len(z_levels) == 1 else [z_levels[0], z_levels[-1]]

    def layer_at(z_value: float) -> List[Tuple[str, Point3D]]:
        return [item for item in candidates if abs(item[1][2] - z_value) <= z_tolerance]

    layers = [layer_at(z_value) for z_value in terminal_levels]
    layers = [layer for layer in layers if len(layer) >= 2]
    if not layers:
        raise ValueError("塔脚连接失败：13号图纸接口层节点不足")

    def span_score(layer: List[Tuple[str, Point3D]]) -> Tuple[float, int]:
        xs = [point[0] for _, point in layer]
        ys = [point[1] for _, point in layer]
        return (max(xs) - min(xs)) + (max(ys) - min(ys)), len(layer)

    layer = max(layers, key=span_score)
    xs = [point[0] for _, point in layer]
    ys = [point[1] for _, point in layer]
    center_x = (min(xs) + max(xs)) / 2.0
    center_y = (min(ys) + max(ys)) / 2.0
    half_x = (max(xs) - min(xs)) / 2.0
    half_y = (max(ys) - min(ys)) / 2.0
    if half_x <= 1e-9 or half_y <= 1e-9:
        raise ValueError("塔脚连接失败：13号图纸接口宽度无效")

    layer_z = sum(item[1][2] for item in layer) / len(layer)
    corner_ids: Dict[Tuple[int, int], str] = {}
    corner_distances: Dict[Tuple[int, int], float] = {}
    for node_id, point in layer:
        x_sign = 1 if point[0] >= center_x else -1
        y_sign = 1 if point[1] >= center_y else -1
        target = (
            center_x + x_sign * half_x,
            center_y + y_sign * half_y,
            layer_z,
        )
        distance = math.dist(point, target)
        key = (x_sign, y_sign)
        if key not in corner_ids or distance < corner_distances[key]:
            corner_ids[key] = node_id
            corner_distances[key] = distance

    front_face = [
        item for item in layer if abs(item[1][1] - min(ys)) <= z_tolerance
    ]
    side_face = [
        item for item in layer if abs(item[1][0] - min(xs)) <= z_tolerance
    ]
    if len(front_face) < 2 or len(side_face) < 2:
        raise ValueError("塔脚连接失败：13号图纸缺少正面或侧面连接点")
    front_middle = min(
        front_face, key=lambda item: (abs(item[1][0] - center_x), item[0])
    )
    side_middle = min(
        side_face, key=lambda item: (abs(item[1][1] - center_y), item[0])
    )

    # Match drawing 59's 5921 slope against the drawing-13 class-1 rods.  The
    # positive-slope match is the original right front leg; the opposite leg
    # supplies the rotated side seed before Y symmetry completes the model.
    main_leg_candidates: List[Tuple[float, str, Point3D]] = []
    for member in member_records:
        member_id = str(member.get("member_id", "")).split("_")[0]
        if not member_id.startswith(CONNECTION_DRAWING_PREFIX) or not member_id.endswith(
            ("01", "02", "03")
        ):
            continue
        node1_id = str(member.get("node1_id", ""))
        node2_id = str(member.get("node2_id", ""))
        if node1_id not in node_points or node2_id not in node_points:
            continue
        point1, point2 = node_points[node1_id], node_points[node2_id]
        lower, upper = sorted((point1, point2), key=lambda point: point[2])
        z_span = upper[2] - lower[2]
        if z_span <= 1e-9 or abs(upper[2] - layer_z) > z_tolerance:
            continue
        upper_id = node1_id if point1 == upper else node2_id
        main_leg_candidates.append(
            ((upper[0] - lower[0]) / z_span, upper_id, upper)
        )
    if len(main_leg_candidates) < 2:
        raise ValueError("塔脚连接失败：13号图纸一类杆件不足")

    if foot_main_slope is None:
        front_main = max(main_leg_candidates, key=lambda item: item[0])
    else:
        front_main = min(
            main_leg_candidates,
            key=lambda item: abs(math.atan(item[0]) - math.atan(foot_main_slope)),
        )
    side_main = min(
        (item for item in main_leg_candidates if item != front_main),
        key=lambda item: item[0],
    )

    return FootInterface(
        center_x=center_x,
        center_y=center_y,
        z=layer_z,
        half_x=half_x,
        half_y=half_y,
        corner_node_ids=corner_ids,
        front_connection_node_ids=(front_middle[0], front_main[1]),
        front_connection_points=(front_middle[1], front_main[2]),
        side_connection_node_ids=(side_middle[0], side_main[1]),
        side_connection_points=(side_middle[1], side_main[2]),
    )


def _find_foot_connection_points(front: CoordDict) -> Tuple[Point2D, Point2D]:
    """Return the two upper ends of the tower-foot main rods.

    In drawing 59 these are the two lowest CAD-Y endpoints, ``(882, 690)`` and
    ``(2370, 649)``. They are the blue-circled points in the reference image;
    the high fan vertex is not a connection point.
    """

    def segment(member_id: str) -> List[Point2D]:
        for raw_id, raw_segment in front.items():
            if str(raw_id).split("_")[0] == member_id:
                return [
                    (float(point[0]), float(point[1])) for point in raw_segment
                ]
        raise ValueError(f"塔脚图纸缺少一类杆件 {member_id}")

    center_connection = min(segment("5907"), key=lambda point: point[1])
    right_connection = min(segment("5921"), key=lambda point: point[1])
    return center_connection, right_connection


def _right_foot_main_slope(front: CoordDict) -> float:
    """Return 5921's signed dx/dy slope for matching the right tower leg."""

    for raw_id, raw_segment in front.items():
        if str(raw_id).split("_")[0] != "5921" or len(raw_segment) != 2:
            continue
        lower, upper = sorted(raw_segment, key=lambda point: float(point[1]))
        dy = float(upper[1]) - float(lower[1])
        if abs(dy) <= 1e-9:
            break
        return (float(upper[0]) - float(lower[0])) / dy
    raise ValueError("塔脚图纸无法计算5921杆件斜率")


def build_half_front_foot(
    path: str,
    interface: FootInterface,
) -> Tuple[List[dict], List[dict]]:
    """Complete the front/side tower-foot geometry and attach it to drawing 13."""

    front, side = load_and_parse_data(path)
    if not front or side:
        raise ValueError(f"{os.path.basename(path)} 不是仅含半幅正视图的塔脚文件")

    source_a, source_b = _find_foot_connection_points(front)
    source_dx = source_b[0] - source_a[0]
    source_dy = source_b[1] - source_a[1]
    source_length = math.hypot(source_dx, source_dy)
    if source_length <= 1e-9:
        raise ValueError("塔脚图纸的一类杆件连接端点重合")

    front_target_a, front_target_b = interface.front_connection_points
    side_target_a, side_target_b = interface.side_connection_points
    front_scale = math.dist(front_target_a, front_target_b) / source_length
    side_scale = math.dist(side_target_a, side_target_b) / source_length
    scale_z = (front_scale + side_scale) / 2.0

    nodes: List[dict] = []
    members: List[dict] = []
    node_cache: Dict[Tuple[str, Point3D], str] = {}
    existing_connections = {
        tuple(round(value, COORDINATE_DIGITS) for value in point): node_id
        for node_ids, points in (
            (interface.front_connection_node_ids, interface.front_connection_points),
            (interface.side_connection_node_ids, interface.side_connection_points),
        )
        for node_id, point in zip(node_ids, points)
    }

    def node_id(point: Point3D, face: str, symmetry_type: int) -> str:
        key = tuple(round(float(value), COORDINATE_DIGITS) for value in point)
        if key in existing_connections:
            return existing_connections[key]
        cache_key = face, key
        if cache_key not in node_cache:
            new_id = f"TF{face.upper()}{len(node_cache) + 1:04d}0"
            node_cache[cache_key] = new_id
            nodes.append(
                {
                    "node_id": new_id,
                    "node_type": 11,
                    "symmetry_type": symmetry_type,
                    "X": key[0],
                    "Y": key[1],
                    "Z": key[2],
                }
            )
        return node_cache[cache_key]

    def source_coordinates(point: Point2D) -> Tuple[float, float]:
        offset_x = float(point[0]) - source_a[0]
        offset_y = float(point[1]) - source_a[1]
        parameter = (offset_x * source_dx + offset_y * source_dy) / (
            source_length * source_length
        )
        height = (source_dx * offset_y - source_dy * offset_x) / source_length
        return parameter, height

    def map_to_face(
        point: Point2D,
        target_a: Point3D,
        target_b: Point3D,
    ) -> Point3D:
        parameter, height = source_coordinates(point)
        return (
            target_a[0] + parameter * (target_b[0] - target_a[0]),
            target_a[1] + parameter * (target_b[1] - target_a[1]),
            interface.z + height * scale_z,
        )

    outer_main_segment = next(
        (
            segment
            for raw_member_id, segment in front.items()
            if str(raw_member_id).split("_")[0] == "5921" and len(segment) == 2
        ),
        None,
    )
    if outer_main_segment is None:
        raise ValueError("塔脚图纸缺少控制外倾角的5921杆件")

    front_outer_line = [
        map_to_face(point, front_target_a, front_target_b)
        for point in outer_main_segment
    ]
    side_outer_line = [
        map_to_face(point, side_target_a, side_target_b)
        for point in outer_main_segment
    ]

    def axis_value_at_z(line: List[Point3D], axis_index: int, z_value: float) -> float:
        """Interpolate one projected main-leg coordinate at a given height."""

        point_a, point_b = line
        z_span = point_b[2] - point_a[2]
        if abs(z_span) <= 1e-9:
            raise ValueError("塔脚5921杆件高度跨度无效")
        ratio = (z_value - point_a[2]) / z_span
        return point_a[axis_index] + ratio * (
            point_b[axis_index] - point_a[axis_index]
        )

    front_outer_at_interface = axis_value_at_z(front_outer_line, 0, interface.z)
    side_outer_at_interface = axis_value_at_z(side_outer_line, 1, interface.z)

    def outward_face_coordinate(
        interface_coordinate: float,
        outer_coordinate: float,
        outer_at_interface: float,
    ) -> float:
        """Move a face outward by the main-leg widening at this height."""

        growth = abs(outer_coordinate) - abs(outer_at_interface)
        direction = -1.0 if interface_coordinate < 0.0 else 1.0
        return interface_coordinate + direction * growth

    def transform_front(point: Point2D) -> Point3D:
        x_value, _, z_value = map_to_face(point, front_target_a, front_target_b)
        side_outer = axis_value_at_z(side_outer_line, 1, z_value)
        y_value = outward_face_coordinate(
            front_target_b[1], side_outer, side_outer_at_interface
        )
        return x_value, y_value, z_value

    def transform_side(point: Point2D) -> Point3D:
        _, y_value, z_value = map_to_face(point, side_target_a, side_target_b)
        front_outer = axis_value_at_z(front_outer_line, 0, z_value)
        x_value = outward_face_coordinate(
            side_target_b[0], front_outer, front_outer_at_interface
        )
        return x_value, y_value, z_value

    seen_members: set[Tuple[str, str, str]] = set()
    for raw_member_id, segment in front.items():
        if len(segment) != 2:
            continue
        for face, transform, symmetry_type in (
            # Each seed contains only half of one elevation.  Four-quadrant
            # symmetry first completes that elevation and then copies it to
            # the opposite face: front -> front/back, side -> left/right.
            ("front", transform_front, 4),
            ("side", transform_side, 4),
        ):
            start_id = node_id(transform(segment[0]), face, symmetry_type)
            end_id = node_id(transform(segment[1]), face, symmetry_type)
            if start_id == end_id:
                continue
            endpoint_key = tuple(sorted((start_id, end_id)))
            unique_key = (str(raw_member_id), endpoint_key[0], endpoint_key[1])
            if unique_key in seen_members:
                continue
            seen_members.add(unique_key)
            members.append(
                {
                    "member_id": str(raw_member_id),
                    "node1_id": start_id,
                    "node2_id": end_id,
                    "symmetry_type": symmetry_type,
                }
            )

    return members, nodes


def attach_half_front_foot(
    path: str,
    tower_members: List[dict],
    tower_nodes: List[dict],
) -> Tuple[List[dict], List[dict]]:
    """Return tower data with the independently reconstructed foot appended."""

    front, _ = load_and_parse_data(path)
    interface = find_drawing_13_interface(
        tower_members,
        tower_nodes,
        foot_main_slope=_right_foot_main_slope(front),
    )
    foot_members, foot_nodes = build_half_front_foot(path, interface)
    return tower_members + foot_members, tower_nodes + foot_nodes
