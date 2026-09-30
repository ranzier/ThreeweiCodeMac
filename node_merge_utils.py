"""Utilities for merging coincident transmission-tower nodes."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple, TypeAlias


Point3D: TypeAlias = Tuple[float, float, float]
NodeMap: TypeAlias = Dict[str, Point3D]

AXES = ("X", "Y", "Z")
AXIS_INDEX = {"X": 0, "Y": 1, "Z": 2}
SYMMETRY_TAIL_MAP = {
    1: {"0": "1", "1": "0", "2": "3", "3": "2"},
    2: {"0": "2", "2": "0", "1": "3", "3": "1"},
    3: {"0": "3", "3": "0", "1": "2", "2": "1"},
}


def _symmetry_deltas(symmetry_type: int) -> List[int]:
    if symmetry_type in (1, 2, 3):
        return [symmetry_type]
    if symmetry_type == 4:
        return [1, 2, 3]
    return []


def _plus_suffix(node_id: str, delta: int) -> str:
    suffix = node_id[-2:] if len(node_id) >= 2 else node_id
    if not suffix.isdigit():
        return node_id
    return f"{node_id[:-2]}{int(suffix) + delta:02d}"


def _symmetry_point(point: Point3D, delta: int) -> Point3D:
    x, y, z = point
    if delta == 1:
        return -x, y, z
    if delta == 2:
        return x, -y, z
    if delta == 3:
        return -x, -y, z
    return point


def _map_node_id(node_id: str, delta: int) -> Optional[str]:
    mapping = SYMMETRY_TAIL_MAP.get(delta)
    if not mapping or not node_id:
        return None
    tail = node_id[-1]
    if tail not in mapping:
        return None
    return f"{node_id[:-1]}{mapping[tail]}"


def _add_node_with_symmetry(
    nodes: NodeMap,
    node_id: str,
    point: Point3D,
    symmetry_type: int,
) -> None:
    nodes[node_id] = point
    for delta in _symmetry_deltas(symmetry_type):
        nodes[_plus_suffix(node_id, delta)] = _symmetry_point(point, delta)


def _decode_node_reference(value: object) -> Optional[str]:
    """Decode the leading-1 reference format while retaining numeric strings."""
    if not isinstance(value, str) or not value.startswith("1"):
        return None
    candidate = value[1:]
    if not candidate or "." in candidate:
        return None
    return candidate


def _read_real_node(row: dict) -> Optional[Point3D]:
    try:
        return tuple(float(row[axis]) for axis in AXES)  # type: ignore[return-value]
    except (KeyError, TypeError, ValueError):
        return None


def _compute_reference_node(row: dict, nodes: NodeMap) -> Optional[Point3D]:
    references: List[str] = []
    real_axes: List[str] = []
    real_value = 0.0
    for axis in AXES:
        reference_id = _decode_node_reference(row.get(axis))
        if reference_id is None:
            real_axes.append(axis)
            try:
                real_value = float(row[axis])
            except (KeyError, TypeError, ValueError):
                return None
        else:
            references.append(reference_id)

    if len(references) != 2 or len(real_axes) != 1:
        return None
    if references[0] not in nodes or references[1] not in nodes:
        return None

    start = nodes[references[0]]
    end = nodes[references[1]]
    axis_index = AXIS_INDEX[real_axes[0]]
    span = end[axis_index] - start[axis_index]
    if math.isclose(span, 0.0, abs_tol=1e-12):
        return None
    ratio = (real_value - start[axis_index]) / span
    result = [start[i] + ratio * (end[i] - start[i]) for i in range(3)]
    result[axis_index] = real_value
    return float(result[0]), float(result[1]), float(result[2])


def expand_nodes(raw_nodes: Iterable[dict]) -> Tuple[NodeMap, List[dict], List[dict]]:
    """Expand real/reference nodes and return nodes, unresolved rows, duplicates."""
    nodes: NodeMap = {}
    pending: List[dict] = []
    duplicates: List[dict] = []
    seen_raw: Dict[str, dict] = {}

    for row in raw_nodes:
        node_id = str(row.get("node_id", ""))
        if not node_id:
            continue
        if node_id in seen_raw:
            duplicates.append({"node_id": node_id, "definitions": 2})
        seen_raw[node_id] = row
        if int(row.get("node_type", 0) or 0) == 11:
            point = _read_real_node(row)
            if point is None:
                pending.append(row)
                continue
            _add_node_with_symmetry(
                nodes, node_id, point, int(row.get("symmetry_type", 0) or 0)
            )
        else:
            pending.append(row)

    unresolved = pending[:]
    while unresolved:
        next_unresolved: List[dict] = []
        resolved_count = 0
        for row in unresolved:
            point = _compute_reference_node(row, nodes)
            if point is None:
                next_unresolved.append(row)
                continue
            _add_node_with_symmetry(
                nodes,
                str(row["node_id"]),
                point,
                int(row.get("symmetry_type", 0) or 0),
            )
            resolved_count += 1
        if resolved_count == 0:
            break
        unresolved = next_unresolved
    return nodes, unresolved, duplicates


def expand_members(raw_members: Iterable[dict]) -> List[dict]:
    """Expand symmetric members and retain a stable source-member label."""
    members: List[dict] = []
    seen = set()
    for source_index, row in enumerate(raw_members):
        member_id = str(row.get("member_id", ""))
        node1_id = str(row.get("node1_id", ""))
        node2_id = str(row.get("node2_id", ""))
        symmetry_type = int(row.get("symmetry_type", 0) or 0)
        candidates = [(node1_id, node2_id, 0)]
        for delta in _symmetry_deltas(symmetry_type):
            mapped1 = _map_node_id(node1_id, delta)
            mapped2 = _map_node_id(node2_id, delta)
            if mapped1 and mapped2:
                candidates.append((mapped1, mapped2, delta))
        for start_id, end_id, copy_index in candidates:
            key = tuple(sorted((start_id, end_id)))
            if key in seen:
                continue
            seen.add(key)
            members.append(
                {
                    "member_id": member_id,
                    "node1_id": start_id,
                    "node2_id": end_id,
                    "symmetry_copy": copy_index,
                    "source_index": source_index,
                }
            )
    return members


def _distance(a: Point3D, b: Point3D) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def merge_coincident_nodes(
    raw_nodes: List[dict],
    raw_members: List[dict],
    pinjie: Optional[List[list]] = None,
    tolerance: float = 0.01,
    only_cross_drawing: bool = False,
) -> dict:
    """Merge every exported node family that occupies the same 3-D point.

    This is primarily a seam repair: adjacent drawings often export several
    IDs for the same physical joint.  The function resolves type-12 nodes and
    symmetry copies first, maps every coincident ID to one explicit canonical
    node, then rewrites member endpoints, type-12 references, and splice IDs.
    It intentionally does not create intersections inside a member; that is a
    separate rod-splitting operation.
    """
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    expanded_nodes, _, _ = expand_nodes(raw_nodes)
    if not expanded_nodes:
        return {
            "merged_node_ids": 0,
            "removed_node_rows": 0,
            "coincident_groups": 0,
            "id_mapping": {},
        }

    raw_by_id = {str(row.get("node_id", "")): row for row in raw_nodes}
    family_ids: Dict[str, List[str]] = {}
    expanded_to_family: Dict[str, str] = {}
    for row in raw_nodes:
        raw_id = str(row.get("node_id", ""))
        if not raw_id or raw_id not in expanded_nodes:
            continue
        symmetry_type = int(row.get("symmetry_type", 0) or 0)
        ids = [raw_id]
        ids.extend(_plus_suffix(raw_id, delta) for delta in _symmetry_deltas(symmetry_type))
        ids = list(dict.fromkeys(node_id for node_id in ids if node_id in expanded_nodes))
        family_ids[raw_id] = ids
        for expanded_id in ids:
            expanded_to_family[expanded_id] = raw_id

    family_names = sorted(family_ids)
    parent = {family_id: family_id for family_id in family_names}
    expanded_node_drawings: Dict[str, set[int]] = defaultdict(set)
    for member in expand_members(raw_members):
        drawing_match = re.search(r"\d+", str(member.get("member_id", "")))
        if drawing_match is None:
            continue
        numeric_id = int(drawing_match.group())
        drawing_id = numeric_id // 100 if numeric_id >= 100 else numeric_id
        for key in ("node1_id", "node2_id"):
            expanded_node_drawings[str(member.get(key, ""))].add(drawing_id)
    family_drawings: Dict[str, set[int]] = {
        family_id: set().union(
            *(expanded_node_drawings[node_id] for node_id in expanded_ids)
        )
        for family_id, expanded_ids in family_ids.items()
    }

    def may_merge_families(first: str, second: str) -> bool:
        if not only_cross_drawing:
            return True
        first_drawings = family_drawings.get(first, set())
        second_drawings = family_drawings.get(second, set())
        return bool(
            first_drawings
            and second_drawings
            and len(first_drawings | second_drawings) > 1
            and first_drawings != second_drawings
        )
    family_references: Dict[str, set[str]] = defaultdict(set)
    for family_id in family_names:
        row = raw_by_id[family_id]
        for axis in AXES:
            reference_id = _decode_node_reference(row.get(axis))
            reference_family = expanded_to_family.get(reference_id or "")
            if reference_family:
                family_references[family_id].add(reference_family)

    forced_id_mapping: Dict[str, str] = {}
    for source_family, reference_families in family_references.items():
        for reference_family in reference_families:
            if not may_merge_families(source_family, reference_family):
                continue
            for source_id in family_ids[source_family]:
                source_point = expanded_nodes[source_id]
                matches = [
                    target_id
                    for target_id in family_ids[reference_family]
                    if _distance(source_point, expanded_nodes[target_id]) <= tolerance
                ]
                if matches:
                    forced_id_mapping[source_id] = min(matches)

    family_depth: Dict[str, int] = {}
    pending_depth = set(family_names)
    for family_id in list(pending_depth):
        row = raw_by_id[family_id]
        if int(row.get("node_type", 0) or 0) == 11:
            family_depth[family_id] = 0
            pending_depth.remove(family_id)
    while pending_depth:
        resolved_this_round = []
        for family_id in pending_depth:
            row = raw_by_id[family_id]
            reference_families = []
            resolvable = True
            for axis in AXES:
                reference_id = _decode_node_reference(row.get(axis))
                if reference_id is None:
                    continue
                reference_family = expanded_to_family.get(reference_id)
                if reference_family is None or reference_family not in family_depth:
                    resolvable = False
                    break
                reference_families.append(reference_family)
            if resolvable:
                family_depth[family_id] = 1 + max(
                    (family_depth[item] for item in reference_families),
                    default=0,
                )
                resolved_this_round.append(family_id)
        if not resolved_this_round:
            break
        pending_depth.difference_update(resolved_this_round)
    for family_id in pending_depth:
        family_depth[family_id] = 10**9

    def find(family_id: str) -> str:
        while parent[family_id] != family_id:
            parent[family_id] = parent[parent[family_id]]
            family_id = parent[family_id]
        return family_id

    def union(first: str, second: str) -> None:
        root_first = find(first)
        root_second = find(second)
        if root_first != root_second:
            parent[root_second] = root_first

    # Search the current cell and its 26 neighbors so points on a rounding
    # boundary are still compared with the requested Euclidean tolerance.
    buckets: Dict[Tuple[int, int, int], List[str]] = defaultdict(list)
    for node_id in sorted(expanded_to_family):
        point = expanded_nodes[node_id]
        cell = tuple(math.floor(value / tolerance) for value in point)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    neighbor = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
                    for other_id in buckets.get(neighbor, []):
                        family_id = expanded_to_family[node_id]
                        other_family_id = expanded_to_family[other_id]
                        if (
                            family_id != other_family_id
                            and may_merge_families(family_id, other_family_id)
                            and other_family_id not in family_references[family_id]
                            and family_id not in family_references[other_family_id]
                            and _distance(point, expanded_nodes[other_id]) <= tolerance
                        ):
                            union(family_id, other_family_id)
        buckets[cell].append(node_id)

    groups: Dict[str, List[str]] = defaultdict(list)
    for family_id in family_names:
        groups[find(family_id)].append(family_id)

    def natural_key(value: str) -> tuple:
        return tuple(
            (0, int(part)) if part.isdigit() else (1, part.lower())
            for part in re.split(r"(\d+)", value)
            if part
        )

    def representative_key(family_id: str) -> tuple:
        row = raw_by_id[family_id]
        is_real = int(row.get("node_type", 0) or 0) == 11
        # Prefer a four-way family so every symmetry sibling has a canonical
        # target. Then prefer a real coordinate node over a reference node.
        return (
            family_depth[family_id],
            not is_real,
            -len(family_ids[family_id]),
            len(family_id),
            natural_key(family_id),
        )

    id_mapping: Dict[str, str] = dict(forced_id_mapping)
    coincident_groups = 0
    for family_group in groups.values():
        if len(family_group) < 2:
            continue
        group_expanded_ids = {
            expanded_id
            for family_id in family_group
            for expanded_id in family_ids[family_id]
        }

        def group_representative_key(family_id: str) -> tuple:
            row = raw_by_id[family_id]
            references = {
                reference_id
                for reference_id in (
                    _decode_node_reference(row.get(axis)) for axis in AXES
                )
                if reference_id is not None
            }
            # Never choose a type-12 node whose coordinate depends on another
            # node in the same merge group: remapping that host would create a
            # self-reference. Prefer an independent/shallower anchor instead.
            dependency_risk = bool(references & group_expanded_ids)
            return (dependency_risk, *representative_key(family_id))

        representative_family = min(family_group, key=group_representative_key)
        target_ids = family_ids[representative_family]
        changed = False
        for source_family in family_group:
            if source_family == representative_family:
                continue
            for source_id in family_ids[source_family]:
                source_point = expanded_nodes[source_id]
                matches = [
                    target_id
                    for target_id in target_ids
                    if _distance(source_point, expanded_nodes[target_id]) <= tolerance
                ]
                if not matches:
                    continue
                target_id = min(matches, key=natural_key)
                if source_id != target_id:
                    id_mapping[source_id] = target_id
                    changed = True
        if changed:
            coincident_groups += 1

    def canonical(node_id: str) -> str:
        seen = set()
        current = str(node_id)
        while current in id_mapping and current not in seen:
            seen.add(current)
            current = id_mapping[current]
        return current

    for member in raw_members:
        for key in ("node1_id", "node2_id"):
            if key in member:
                member[key] = canonical(str(member[key]))

    for row in raw_nodes:
        if int(row.get("node_type", 0) or 0) != 12:
            continue
        for axis in AXES:
            value = row.get(axis)
            if not isinstance(value, str):
                continue
            reference_id = _decode_node_reference(value)
            if reference_id is not None and reference_id in id_mapping:
                row[axis] = "1" + canonical(reference_id)
            elif value in id_mapping:
                row[axis] = canonical(value)

    original_node_count = len(raw_nodes)
    kept_by_id: Dict[str, dict] = {}
    order: List[str] = []
    for row in raw_nodes:
        original_id = str(row.get("node_id", ""))
        canonical_id = canonical(original_id)

        # ``canonical_id`` may be an implicit symmetry child of another
        # exported family (for example 80321 generated by 80320).  Keeping the
        # remapped source as a second explicit row at 80321 is invalid: that
        # row carries its own symmetry flag and overwrites 80320's generated
        # 80321/80322/80323 coordinates during expansion.  Members and
        # references can point directly at the implicit child, so discard only
        # this redundant row and retain the canonical family definition.
        canonical_family = expanded_to_family.get(canonical_id)
        if (
            canonical_id != original_id
            and canonical_family is not None
            and canonical_id != canonical_family
            and canonical_family in raw_by_id
        ):
            continue

        row["node_id"] = canonical_id
        existing = kept_by_id.get(canonical_id)
        if existing is None:
            kept_by_id[canonical_id] = row
            order.append(canonical_id)
        elif (
            int(existing.get("node_type", 0) or 0) != 11
            and int(row.get("node_type", 0) or 0) == 11
        ):
            kept_by_id[canonical_id] = row
    raw_nodes[:] = [kept_by_id[node_id] for node_id in order]

    if pinjie is not None:
        seen_pinjie = set()
        merged_pinjie = []
        for item in pinjie:
            if not isinstance(item, list) or not item:
                merged_pinjie.append(item)
                continue
            new_item = list(item)
            new_item[0] = canonical(str(new_item[0]))
            if new_item[0] in seen_pinjie:
                continue
            seen_pinjie.add(new_item[0])
            merged_pinjie.append(new_item)
        pinjie[:] = merged_pinjie

    return {
        "merged_node_ids": len(id_mapping),
        "removed_node_rows": original_node_count - len(raw_nodes),
        "coincident_groups": coincident_groups,
        "id_mapping": id_mapping,
    }

