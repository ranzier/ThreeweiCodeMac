"""Conservative 2D normalization for high/low-slope tower drawings."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, TypeAlias
import math


Coord: TypeAlias = Tuple[float, float]
CoordDict: TypeAlias = Dict[str, List[Coord]]


@dataclass
class AsymmetricNormalizationResult:
    coordinates: CoordDict
    applied: bool = False
    main_rod_ids: List[str] = field(default_factory=list)
    symmetry_axis: Optional[float] = None
    source_side: Optional[str] = None
    virtual_supports: CoordDict = field(default_factory=dict)
    removed_ids: Set[str] = field(default_factory=set)
    reason: str = "normal tower"


@dataclass(frozen=True)
class _SupportFeature:
    member_id: str
    side: str
    coverage: float
    envelope: float
    slope_score: float
    id_prior: float
    score: float


def _base_id(member_id: object) -> str:
    text = str(member_id).strip()
    base, separator, instance = text.rpartition("_")
    return base if separator and instance.isdigit() else text


def _is_conventional_main_id(member_id: object) -> bool:
    return _base_id(member_id).endswith(("01", "02", "03"))


def _clean_coordinates(coordinates: CoordDict) -> CoordDict:
    cleaned: CoordDict = {}
    for member_id, segment in (coordinates or {}).items():
        if not isinstance(segment, (list, tuple)) or len(segment) != 2:
            continue
        p1 = (float(segment[0][0]), float(segment[0][1]))
        p2 = (float(segment[1][0]), float(segment[1][1]))
        if math.dist(p1, p2) <= 1e-9:
            continue
        cleaned[str(member_id)] = [p1, p2]
    return cleaned


def _drawing_bounds(coordinates: CoordDict) -> Optional[Tuple[float, float, float, float]]:
    points = [point for segment in coordinates.values() for point in segment]
    if len(points) < 4:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), max(xs), min(ys), max(ys)


def _find_symmetry_axis(
    coordinates: CoordDict,
    width: float,
    height: float,
) -> Tuple[Optional[float], float]:
    horizontal_tolerance = max(5.0, height * 0.015)
    broad_horizontals: List[Tuple[float, float]] = []
    for segment in coordinates.values():
        (x1, y1), (x2, y2) = segment
        span = abs(x2 - x1)
        if abs(y2 - y1) <= horizontal_tolerance and span >= width * 0.45:
            broad_horizontals.append(((x1 + x2) / 2.0, span))
    if not broad_horizontals:
        return None, 0.0

    broad_horizontals.sort(key=lambda item: item[0])
    total_weight = sum(item[1] for item in broad_horizontals)
    weighted_axis = sum(mid * span for mid, span in broad_horizontals) / total_weight
    spread = max(abs(mid - weighted_axis) for mid, _ in broad_horizontals)
    confidence = max(0.0, 1.0 - spread / max(width * 0.08, 1.0))
    return weighted_axis, confidence


def _support_feature(
    member_id: str,
    segment: List[Coord],
    axis_x: float,
    height: float,
) -> Optional[_SupportFeature]:
    (x1, y1), (x2, y2) = segment
    vertical_span = abs(y2 - y1)
    if vertical_span <= height * 0.15:
        return None

    midpoint_x = (x1 + x2) / 2.0
    side = "left" if midpoint_x < axis_x else "right"
    radial1 = abs(x1 - axis_x)
    radial2 = abs(x2 - axis_x)
    max_radial = max(radial1, radial2)
    if max_radial <= 1e-9:
        return None

    coverage = min(1.0, vertical_span / max(height, 1e-9))
    envelope = min(radial1, radial2) / max_radial
    tilt = abs(x2 - x1) / vertical_span
    slope_score = 1.0 / (1.0 + (tilt / 0.45) ** 2)
    id_prior = 1.0 if _is_conventional_main_id(member_id) else 0.0
    score = (
        0.45 * coverage
        + 0.30 * envelope
        + 0.20 * slope_score
        + 0.05 * id_prior
    )
    return _SupportFeature(
        member_id=member_id,
        side=side,
        coverage=coverage,
        envelope=envelope,
        slope_score=slope_score,
        id_prior=id_prior,
        score=score,
    )


def _mirror_segment(segment: List[Coord], axis_x: float) -> List[Coord]:
    return [(2.0 * axis_x - x, y) for x, y in segment]


def _segment_pair_distance(first: List[Coord], second: List[Coord]) -> float:
    direct = max(math.dist(first[0], second[0]), math.dist(first[1], second[1]))
    reversed_distance = max(
        math.dist(first[0], second[1]),
        math.dist(first[1], second[0]),
    )
    return min(direct, reversed_distance)


def _mirrored_structure_match_ratio(
    coordinates: CoordDict,
    axis_x: float,
    source_side: str,
    side_tolerance: float,
    match_tolerance: float,
) -> float:
    opposite_side = "left" if source_side == "right" else "right"
    source_segments: List[List[Coord]] = []
    target_segments: List[List[Coord]] = []
    for segment in coordinates.values():
        midpoint_x = (segment[0][0] + segment[1][0]) / 2.0
        if abs(midpoint_x - axis_x) <= side_tolerance:
            continue
        side = "left" if midpoint_x < axis_x else "right"
        if side == source_side:
            source_segments.append(segment)
        elif side == opposite_side:
            target_segments.append(segment)
    if not source_segments or not target_segments:
        return 0.0

    matched = 0
    unused_targets = set(range(len(target_segments)))
    for source_segment in source_segments:
        mirrored = _mirror_segment(source_segment, axis_x)
        candidates = [
            (_segment_pair_distance(mirrored, target_segments[index]), index)
            for index in unused_targets
        ]
        if not candidates:
            continue
        distance, target_index = min(candidates)
        if distance <= match_tolerance:
            matched += 1
            unused_targets.remove(target_index)
    return matched / max(1, min(len(source_segments), len(target_segments)))


def normalize_asymmetric_tower_view(
    coordinates: CoordDict,
    min_support_score: float = 0.72,
    min_axis_confidence: float = 0.70,
) -> AsymmetricNormalizationResult:
    """Normalize a high/low-slope view only when normal support pairing fails.

    Normal drawings are returned byte-for-byte equivalent in geometry.  The
    exceptional path keeps the trusted conventional side and cross-axis
    members, removes the opposite raw half, and exposes a virtual mirrored
    support for downstream geometry calculations.
    """
    cleaned = _clean_coordinates(coordinates)
    result = AsymmetricNormalizationResult(coordinates=cleaned)
    bounds = _drawing_bounds(cleaned)
    if bounds is None:
        result.reason = "insufficient geometry"
        return result

    min_x, max_x, min_y, max_y = bounds
    width = max_x - min_x
    height = max_y - min_y
    if width <= 1e-9 or height <= 1e-9:
        result.reason = "degenerate drawing bounds"
        return result

    axis_x, axis_confidence = _find_symmetry_axis(cleaned, width, height)
    if axis_x is None or axis_confidence < min_axis_confidence:
        result.reason = "no reliable structural symmetry axis"
        return result

    features = [
        feature
        for member_id, segment in cleaned.items()
        if (feature := _support_feature(member_id, segment, axis_x, height)) is not None
    ]
    strong = [feature for feature in features if feature.score >= min_support_score]
    conventional = [feature for feature in strong if feature.id_prior > 0.0]

    conventional_sides = {feature.side for feature in conventional}
    if len(conventional) >= 2 and conventional_sides == {"left", "right"}:
        left = max((f for f in conventional if f.side == "left"), key=lambda f: f.score)
        right = max((f for f in conventional if f.side == "right"), key=lambda f: f.score)
        overlap_ratio = min(left.coverage, right.coverage) / max(left.coverage, right.coverage)
        if overlap_ratio >= 0.80:
            result.main_rod_ids = [left.member_id, right.member_id]
            result.symmetry_axis = axis_x
            result.reason = "valid conventional support pair"
            return result

    if not conventional:
        result.reason = "no trusted conventional main rod"
        return result

    source = max(conventional, key=lambda feature: (feature.score, feature.coverage))
    opposite = [
        feature
        for feature in strong
        if feature.side != source.side and feature.member_id != source.member_id
    ]
    if not opposite:
        result.reason = "no opposite-side structure evidence"
        return result

    best_opposite = max(opposite, key=lambda feature: feature.score)
    if best_opposite.coverage > source.coverage * 1.20:
        result.reason = "conventional side is not the longer support side"
        return result

    side_tolerance = max(5.0, width * 0.01)
    coverage_ratio = min(source.coverage, best_opposite.coverage) / max(
        source.coverage,
        best_opposite.coverage,
    )
    structure_match_ratio = _mirrored_structure_match_ratio(
        cleaned,
        axis_x,
        source.side,
        side_tolerance,
        max(35.0, width * 0.03),
    )
    if coverage_ratio >= 0.80 and structure_match_ratio >= 0.50:
        ordered_pair = sorted(
            (source, best_opposite),
            key=lambda feature: 0 if feature.side == "left" else 1,
        )
        result.main_rod_ids = [feature.member_id for feature in ordered_pair]
        result.symmetry_axis = axis_x
        result.reason = "valid geometric support pair"
        return result

    source_member_count = 0
    target_member_count = 0
    for segment in cleaned.values():
        sides = []
        for x_value, _ in segment:
            delta = x_value - axis_x
            sides.append(
                "center" if abs(delta) <= side_tolerance
                else "left" if delta < 0
                else "right"
            )
        if all(side in (source.side, "center") for side in sides):
            source_member_count += 1
        opposite_side = "left" if source.side == "right" else "right"
        if all(side in (opposite_side, "center") for side in sides):
            target_member_count += 1

    if source_member_count < 3 or target_member_count < 1:
        result.reason = "one-sided structure is incomplete"
        return result

    kept: CoordDict = {}
    removed: Set[str] = set()
    opposite_side = "left" if source.side == "right" else "right"
    for member_id, segment in cleaned.items():
        endpoint_sides = []
        for x_value, _ in segment:
            delta = x_value - axis_x
            endpoint_sides.append(
                "center" if abs(delta) <= side_tolerance
                else "left" if delta < 0
                else "right"
            )
        if all(side in (opposite_side, "center") for side in endpoint_sides) and any(
            side == opposite_side for side in endpoint_sides
        ):
            removed.add(member_id)
            continue
        kept[member_id] = segment

    virtual_id = f"__asym_mirror__{source.member_id}"
    virtual_supports = {
        virtual_id: _mirror_segment(cleaned[source.member_id], axis_x)
    }
    return AsymmetricNormalizationResult(
        coordinates=kept,
        applied=True,
        main_rod_ids=[source.member_id],
        symmetry_axis=axis_x,
        source_side=source.side,
        virtual_supports=virtual_supports,
        removed_ids=removed,
        reason=(
            f"high/low-slope normalization from {source.side} support "
            f"{source.member_id}"
        ),
    )
