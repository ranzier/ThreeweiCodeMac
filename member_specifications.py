import json


def load_member_specifications(file_path):
    """Load and merge the JSON objects embedded in a guige.txt file."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gb18030") as file:
            content = file.read()

    decoder = json.JSONDecoder()
    specifications = {}
    cursor = 0
    block_count = 0

    while True:
        block_start = content.find("{", cursor)
        if block_start == -1:
            break

        try:
            block, block_end = decoder.raw_decode(content, block_start)
        except json.JSONDecodeError as exc:
            line_number = content.count("\n", 0, exc.pos) + 1
            raise ValueError(
                f"Invalid specification dictionary near line {line_number}: {exc.msg}"
            ) from exc

        if not isinstance(block, dict):
            raise ValueError(
                f"Specification block {block_count + 1} must be a dictionary"
            )

        for raw_member_id, raw_specification in block.items():
            member_id = str(raw_member_id).strip()
            if not member_id:
                raise ValueError(
                    f"Specification block {block_count + 1} contains an empty member id"
                )
            if not isinstance(raw_specification, str):
                raise ValueError(
                    f"Specification for member {member_id} must be text"
                )

            specification = raw_specification.strip()
            existing = specifications.get(member_id)
            if existing is not None and existing != specification:
                raise ValueError(
                    f"Conflicting specifications for member {member_id}: "
                    f"{existing!r} and {specification!r}"
                )
            specifications[member_id] = specification

        block_count += 1
        cursor = block_end

    if block_count == 0:
        raise ValueError(f"No specification dictionaries found in {file_path}")

    return specifications


def _member_specification(
    member_id, specifications, prefer_numeric_instance_suffix=False
):
    member_id = str(member_id).strip()

    base_id, separator, instance = member_id.rpartition("_")
    if separator and instance.isdigit() and base_id in specifications:
        return specifications[base_id]

    # xintrans loads unquoted numeric keys with exec(), so IDs such as 156_1
    # become 1561. Stretcher members therefore prefer the recovered base ID.
    numeric_instance_base = None
    if member_id[-1:] in {"1", "2"} and member_id[:-1] in specifications:
        numeric_instance_base = member_id[:-1]

    if prefer_numeric_instance_suffix and numeric_instance_base is not None:
        return specifications[numeric_instance_base]
    if member_id in specifications:
        return specifications[member_id]
    if numeric_instance_base is not None:
        return specifications[numeric_instance_base]
    return ""


def add_member_specifications(
    members, specifications, prefer_numeric_instance_suffix=False
):
    """Add a specifications field and return member IDs without a match."""
    missing_member_ids = set()
    for member in members:
        member_id = str(member.get("member_id", "")).strip()
        specification = _member_specification(
            member_id,
            specifications,
            prefer_numeric_instance_suffix=prefer_numeric_instance_suffix,
        )
        member["specifications"] = specification
        if not specification:
            missing_member_ids.add(member_id)

    return sorted(missing_member_ids)
