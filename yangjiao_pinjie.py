"""YangJiao stretcher-to-tower splice-point construction.

The YangJiao family uses the first six front-view tower horizontals, counted
from the smallest tower drawing number. Consecutive horizontals form three
physical upper/lower connection pairs. The first pair is shared by the first
two YangJiao component drawings; subsequent pairs are consumed once each.
"""

import glob
import math
import os
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, TypeAlias

from dual_view_core import _parse_block_dict
from get_first_ganjian_id import detect_main_rods_enhanced
from stretcher_tower_connection import get_main_rod_connection_geometry


Point2D: TypeAlias = Tuple[float, float]
Point3D: TypeAlias = Tuple[float, float, float]
NodeMap: TypeAlias = Dict[str, Point3D]

_AXES = ("X", "Y", "Z")
_AXIS_INDEX = {"X": 0, "Y": 1, "Z": 2}


def _natural_key(value: str) -> Tuple[Tuple[int, object], ...]:
    """Return a stable numeric-aware sort key for drawing/member names."""
    stem = os.path.splitext(os.path.basename(str(value)))[0]
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.lower())
        for part in re.split(r"(\d+)", stem)
        if part
    )


def _base_member_id(value: object) -> str:
    text = str(value).replace("F_", "").replace("R_", "")
    return text.split("_", 1)[0]


def _plus_suffix(node_id: str, delta: int) -> str:
    suffix = node_id[-2:] if len(node_id) >= 2 else node_id
    if not suffix.isdigit():
        return node_id
    return f"{node_id[:-2]}{int(suffix) + delta:02d}"


def _symmetry_deltas(symmetry_type: int) -> List[int]:
    if symmetry_type == 1:
        return [1]
    if symmetry_type == 2:
        return [2]
    if symmetry_type == 3:
        return [3]
    if symmetry_type == 4:
        return [1, 2, 3]
    return []


def _symmetry_point(point: Point3D, symmetry_type: int) -> Point3D:
    x, y, z = point
    if symmetry_type == 1:
        return -x, y, z
    if symmetry_type == 2:
        return x, -y, z
    if symmetry_type == 3:
        return -x, -y, z
    return point


def _add_node_with_symmetry(
    nodes: NodeMap,
    node_id: str,
    point: Point3D,
    symmetry_type: int,
) -> None:
    nodes[node_id] = point
    for delta in _symmetry_deltas(symmetry_type):
        nodes[_plus_suffix(node_id, delta)] = _symmetry_point(point, delta)


def _decode_reference(value: object) -> Optional[str]:
    if not isinstance(value, str) or not value.startswith("1"):
        return None
    candidate = value[1:]
    if not candidate or "." in candidate:
        return None
    return candidate


def _resolve_reference_node(row: dict, nodes: NodeMap) -> Optional[Point3D]:
    references: List[str] = []
    real_axis = ""
    real_value = 0.0
    for axis in _AXES:
        reference_id = _decode_reference(row.get(axis))
        if reference_id is None:
            real_axis = axis
            try:
                real_value = float(row[axis])
            except (KeyError, TypeError, ValueError):
                return None
        else:
            references.append(reference_id)

    if len(references) != 2 or not real_axis:
        return None
    if references[0] not in nodes or references[1] not in nodes:
        return None

    start = nodes[references[0]]
    end = nodes[references[1]]
    axis_index = _AXIS_INDEX[real_axis]
    span = end[axis_index] - start[axis_index]
    if math.isclose(span, 0.0, abs_tol=1e-9):
        return None
    ratio = (real_value - start[axis_index]) / span
    coords = [start[i] + ratio * (end[i] - start[i]) for i in range(3)]
    coords[axis_index] = real_value
    return float(coords[0]), float(coords[1]), float(coords[2])


def _build_expanded_nodes(raw_nodes: Iterable[dict]) -> NodeMap:
    """Resolve real/reference nodes and their symmetry families."""
    nodes: NodeMap = {}
    pending: List[dict] = []
    for row in raw_nodes:
        node_id = str(row.get("node_id", ""))
        if not node_id:
            continue
        if int(row.get("node_type", 0)) == 11:
            point = (float(row["X"]), float(row["Y"]), float(row["Z"]))
            _add_node_with_symmetry(
                nodes, node_id, point, int(row.get("symmetry_type", 0))
            )
        else:
            pending.append(row)

    unresolved = pending
    while unresolved:
        next_unresolved: List[dict] = []
        resolved_count = 0
        for row in unresolved:
            point = _resolve_reference_node(row, nodes)
            if point is None:
                next_unresolved.append(row)
                continue
            _add_node_with_symmetry(
                nodes,
                str(row["node_id"]),
                point,
                int(row.get("symmetry_type", 0)),
            )
            resolved_count += 1
        if resolved_count == 0:
            break
        unresolved = next_unresolved
    return nodes


def _read_front(txt_path: str) -> Dict[str, List[Point2D]]:
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as handle:
        return _parse_block_dict(handle.read(), "front")


def _collect_first_horizontals(
    tashen_dir: str,
    count: int = 6,
    horizontal_tolerance: float = 20.0,
) -> List[Tuple[str, str, List[Point2D]]]:
    """Collect front horizontals by drawing number, then top-to-bottom in CAD."""
    selected: List[Tuple[str, str, List[Point2D]]] = []
    paths = sorted(
        glob.glob(os.path.join(tashen_dir, "*.txt")),
        key=_natural_key,
    )
    for path in paths:
        front = _read_front(path)
        horizontals = []
        for member_id, segment in front.items():
            if len(segment) != 2:
                continue
            if abs(segment[0][1] - segment[1][1]) > horizontal_tolerance:
                continue
            average_y = (segment[0][1] + segment[1][1]) / 2.0
            horizontals.append((average_y, str(member_id), segment))
        horizontals.sort(key=lambda item: (item[0], _natural_key(item[1])))
        drawing_name = os.path.splitext(os.path.basename(path))[0]
        selected.extend(
            (drawing_name, member_id, segment)
            for _, member_id, segment in horizontals
        )
        if len(selected) >= count:
            return selected[:count]

    raise ValueError(
        f"YangJiao: tower drawings contain only {len(selected)} front horizontals; "
        f"{count} are required"
    )


def _pick_front_member_row(member_id: str, members: Sequence[dict]) -> dict:
    exact = [row for row in members if str(row.get("member_id")) == member_id]
    candidates = exact or [
        row
        for row in members
        if _base_member_id(row.get("member_id")) == _base_member_id(member_id)
    ]
    if not candidates:
        raise KeyError(f"YangJiao: final model has no member row for horizontal {member_id}")
    return max(
        candidates,
        key=lambda row: (
            int(row.get("symmetry_type", 0)) == 2,
            str(row.get("member_id")) == member_id,
        ),
    )


def _horizontal_endpoints(
    member_id: str,
    members: Sequence[dict],
    nodes: NodeMap,
) -> Tuple[Tuple[str, Point3D], Tuple[str, Point3D]]:
    row = _pick_front_member_row(member_id, members)
    endpoints = []
    for key in ("node1_id", "node2_id"):
        node_id = str(row.get(key, ""))
        point = nodes.get(node_id)
        if not node_id or point is None:
            raise KeyError(
                f"YangJiao: horizontal {member_id} endpoint {node_id!r} has no 3D node"
            )
        endpoints.append((node_id, point))
    endpoints.sort(key=lambda item: item[1][0])
    return endpoints[0], endpoints[1]


def build_yangjiao_stretcher_pinjie(
    danjia_dir: str,
    tashen_dir: str,
    jiedian_tashen: Sequence[dict],
    ganjian_tashen: Sequence[dict],
) -> List[list]:
    """Build three YangJiao physical splice pairs from the first six horizontals."""
    selected = _collect_first_horizontals(tashen_dir, count=6)
    nodes = _build_expanded_nodes(jiedian_tashen)
    pinjie: List[list] = []

    labels = [f"{drawing}:{member}" for drawing, member, _ in selected]
    print(f"[YangJiao pinjie] first six tower horizontals: {' -> '.join(labels)}")

    for pair_index in range(0, 6, 2):
        _, upper_id, _ = selected[pair_index]
        _, lower_id, _ = selected[pair_index + 1]
        left_upper, right_upper = _horizontal_endpoints(
            upper_id, ganjian_tashen, nodes
        )
        left_lower, right_lower = _horizontal_endpoints(
            lower_id, ganjian_tashen, nodes
        )
        pinjie.extend(
            [
                [right_upper[0], list(right_upper[1])],
                [right_lower[0], list(right_lower[1])],
                [left_upper[0], list(left_upper[1])],
                [left_lower[0], list(left_lower[1])],
            ]
        )

    expected_files = len(glob.glob(os.path.join(danjia_dir, "*.txt")))
    if expected_files != 4:
        print(
            f"[YangJiao pinjie] warning: expected 4 component drawings, "
            f"found {expected_files}"
        )
    return pinjie


def build_yangjiao_pj_indices(danjia_dir: str, pair_count: int) -> List[int]:
    """Map YangJiao component drawings to physical pair and left/right side."""
    paths = sorted(
        glob.glob(os.path.join(danjia_dir, "*.txt")),
        key=_natural_key,
    )
    if not paths:
        return []
    if pair_count <= 0 or len(paths) < pair_count:
        raise ValueError(
            f"YangJiao: {len(paths)} component drawings cannot use {pair_count} pairs"
        )

    # Four drawings and three physical pairs become [A, A, B, C]. More
    # generally, any surplus drawings share the first (horn-top) pair.
    repeated_first = len(paths) - pair_count + 1
    pair_assignments = [0] * repeated_first + list(range(1, pair_count))
    if len(pair_assignments) != len(paths):
        raise ValueError("YangJiao: failed to construct component/pair mapping")

    indices: List[int] = []
    descriptions: List[str] = []
    for path, pair_index in zip(paths, pair_assignments):
        front = _read_front(path)
        main_ids = detect_main_rods_enhanced(front)
        if len(main_ids) < 2:
            raise ValueError(
                f"YangJiao: {os.path.basename(path)} has fewer than two main rods"
            )
        side, _, _ = get_main_rod_connection_geometry(
            front, main_ids[0], main_ids[1]
        )
        side_offset = 0 if side == "right" else 1
        indices.append(pair_index * 2 + side_offset)
        descriptions.append(
            f"{os.path.basename(path)}=pair{pair_index + 1}/{side}"
        )

    print(f"[YangJiao pinjie] component mapping: {', '.join(descriptions)}")
    return indices
