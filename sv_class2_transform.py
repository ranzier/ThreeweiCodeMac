import math
import io_utils as rw
from sv_class1_transform import extract_target_members


# CAD coordinates are millimetres; reconstructed single-view coordinates are metres.
EPS = 150.0
NODE_REUSE_TOLERANCE = EPS / 1000.0

# ================= 核心工具 =================
def dist_pt_seg(p, a, b):
    """计算点到线段的最短距离，用于容差吸附"""
    x0, y0 = p; x1, y1 = a; x2, y2 = b
    dx = x2 - x1; dy = y2 - y1
    l2 = dx*dx + dy*dy
    if l2 == 0: return math.hypot(x0-x1, y0-y1)
    t = max(0, min(1, ((x0-x1)*dx + (y0-y1)*dy) / l2))
    px = x1 + t * dx; py = y1 + t * dy
    return math.hypot(x0-px, y0-py)

def clean_id(raw_id):
    """去除 CAD 图纸解析时带入的 _1 等后缀"""
    text = str(raw_id).strip()
    if not text:
        return text
    head, sep, tail = text.rpartition("_")
    if sep and tail.isdigit():
        return head
    return text


def member_instance_id(raw_id):
    """Return the original member id, preserving duplicate-instance suffixes."""
    return str(raw_id).strip()


def node_id_base(raw_id):
    """Build the numeric node-ID prefix while preserving duplicate instances."""
    return member_instance_id(raw_id).replace("_", "")

# ================= 1. 先找一类杆件 =================
def extract_lines01(lines_dict, main_rod_ids=None):
    return extract_target_members(lines_dict, main_rod_ids)
# ================= 辅助：算真实坐标的投影仪 =================
def build_projector(lines01):
    lines = list(lines01.values())
    if len(lines) < 2: return None

    centers = [((seg[0][0]+seg[1][0])/2.0, seg) for seg in lines]
    centers.sort(key=lambda x: x[0])

    mid = len(centers)//2
    left_group = [seg for _, seg in centers[:mid]]
    right_group = [seg for _, seg in centers[mid:]]

    left_line = min(left_group, key=lambda s: min(s[0][0], s[1][0]))
    right_line = max(right_group, key=lambda s: max(s[0][0], s[1][0]))

    y_min = min(left_line[0][1], left_line[1][1], right_line[0][1], right_line[1][1])
    y_max = max(left_line[0][1], left_line[1][1], right_line[0][1], right_line[1][1])
    h_cad = abs(y_max - y_min)

    def get_x(y, line):
        (x1, y1), (x2, y2) = line
        if abs(y2 - y1) < 1e-9: return (x1+x2)/2.0
        return x1 + (y - y1)*(x2-x1)/(y2-y1)

    # CAD segments are not guaranteed to use the same endpoint order.  Using
    # left_line[0]/right_line[0] can therefore average one upper endpoint with
    # one lower endpoint and move the detected tower axis hundreds of units.
    center_x_avg = (get_x(y_min, left_line) + get_x(y_min, right_line)) / 2.0

    w_top = abs(get_x(y_min, right_line) - get_x(y_min, left_line))
    w_bot = abs(get_x(y_max, right_line) - get_x(y_max, left_line))
    span_sq = max(h_cad**2 - ((w_bot - w_top)/2.0)**2, 0.0)
    z_top_3d = math.sqrt(span_sq) / 1000.0

    def project(x, y):
        t = (y - y_min)/h_cad if h_cad > 1e-9 else 0
        z3d = t * z_top_3d
        xl = get_x(y, left_line)
        xr = get_x(y, right_line)
        cx = (xl + xr)/2.0
        cw = abs(xr - xl)
        rel_x = (x - cx)/cw if cw > 1e-9 else 0
        x3d = rel_x * (w_top + t*(w_bot - w_top)) / 1000.0
        return round(x3d,6), round(x3d,6), round(z3d,6)

    return project, center_x_avg

# ================= 六步拓扑主函数 =================
# Legacy implementation kept for reference; production uses single_view0201 below.
def _legacy_single_view0201(line_coord):
    print("\n" + "="*50)
    print("====== 开始执行严格 6 步引用拓扑法（完全遵照原版指令） ======")

    ganjian = []
    jiedian = []

    # === 1. 一类杆件 ===
    lines01 = extract_lines01(line_coord)
    if len(lines01) < 2: return [], []

    proj_result = build_projector(lines01)
    if not proj_result: return [], []
    projector, center_x_cad = proj_result

    special_bar_id = node_id_base(next(iter(lines01.keys())))

    # 用于防冲突的节点 ID 分配器
    used_nids = set()
    def get_safe_nid(base_id):
        """每一根线，必定生成属于自己的 10/20 节点！绝不跳过！"""
        for suffix in range(10, 100, 10):
            test_nid = f"{base_id}{suffix}"
            if test_nid not in used_nids:
                used_nids.add(test_nid)
                return test_nid
        return f"{base_id}99"

    # 核心字典：记录二类杆件的干爹节点 ID，供三类辅材引用
    tier2_nodes_map = {} 

    # === Step 2: 找一类节点 ===
    for k, seg in lines01.items():
        clean_k = clean_id(k)
        member_k = member_instance_id(k)
        node_ids = []
        for i, pt in enumerate(seg):
            nid = get_safe_nid(node_id_base(k))
            x3d, y3d, z3d = projector(pt[0], pt[1])
            jiedian.append({
                "node_id": str(nid), "node_type": 11, "symmetry_type": 4,
                "X": x3d, "Y": y3d, "Z": z3d
            })
            node_ids.append(str(nid))

        ganjian.append({
            "member_id": clean_k, "node1_id": node_ids[0], "node2_id": node_ids[1], "symmetry_type": 4
        })

    # ================= 拓扑分类准备 =================
    unclassified = {k: v for k, v in line_coord.items() if k not in lines01}
    TOLERANCE = EPS

    def find_host(pt, host_dict):
        best_d = float("inf")
        best_k = None
        for k, seg in host_dict.items():
            d = dist_pt_seg(pt, seg[0], seg[1])
            if d < best_d:
                best_d = d; best_k = k
        return best_k if best_d < TOLERANCE else None

    # === Step 3 & 4: 找二类节点与杆件 ===
    tier2_members = {}
    for k, seg in list(unclassified.items()):
        h1 = find_host(seg[0], lines01)
        h2 = find_host(seg[1], lines01)

        if h1 and h2:
            tier2_members[k] = seg
            del unclassified[k]
            
            clean_k = clean_id(k)
            member_k = member_instance_id(k)
            node_ids = []
            for i, pt in enumerate(seg):
                # 必定生成 110910 和 110920！
                nid = get_safe_nid(node_id_base(k))
                _, _, z3d = projector(pt[0], pt[1])

                if pt[0] < center_x_cad:
                    ref_x, ref_y = f"{special_bar_id}10", f"{special_bar_id}20"
                else:
                    ref_x, ref_y = f"{special_bar_id}11", f"{special_bar_id}21"

                jiedian.append({
                    "node_id": str(nid), "node_type": 12, "symmetry_type": 4,
                    "X": ref_x, "Y": ref_y, "Z": z3d
                })
                node_ids.append(str(nid))

            # 记录二类杆件真实的 10 和 20 节点
            tier2_nodes_map[member_k] = (node_ids[0], node_ids[1])

            # ================== 完美复刻你的侧面生成逻辑 ==================
            is_horiz = abs(seg[0][1] - seg[1][1]) < 25.0
            if is_horiz:
                ganjian.append({"member_id": clean_k, "node1_id": node_ids[0], "node2_id": f"{node_ids[0][:-1]}1", "symmetry_type": 2})
                ganjian.append({"member_id": clean_k, "node1_id": node_ids[0], "node2_id": f"{node_ids[0][:-1]}2", "symmetry_type": 1})
            else:
                # 生成正面交叉杆
                ganjian.append({"member_id": clean_k, "node1_id": node_ids[0], "node2_id": node_ids[1], "symmetry_type": 4})
                # 生成侧面交叉杆 (依靠 symmetry_type=4 让引擎处理对称)
                ganjian.append({"member_id": clean_k, "node1_id": node_ids[0], "node2_id": f"{node_ids[1][:-1]}3", "symmetry_type": 4})

    # === Step 5 & 6: 找三类节点与杆件 (0202辅材) ===
# ==============================================
    # === Step 5 & 6: 三类杆件（0202辅材）【修复完整版】
    # ==============================================
    for k, seg in list(unclassified.items()):
        pt1, pt2 = seg[0], seg[1]

        # ======================
        # 吸附规则：优先一类，再二类（修复乱吸附）
        # ======================
        h1_t1 = find_host(pt1, lines01)
        h2_t1 = find_host(pt2, lines01)

        h1_t2 = find_host(pt1, tier2_members) if not h1_t1 else None
        h2_t2 = find_host(pt2, tier2_members) if not h2_t1 else None

        # 两端都在一类 → 已经是二类，跳过
        if h1_t1 and h2_t1:
            continue

        # 必须至少一端吸附到有效宿主
        if not (h1_t1 or h1_t2) or not (h2_t1 or h2_t2):
            print(f"[跳过] 杆件 {k} 无有效宿主")
            continue


        # ======================
        # 正式生成三类杆件
        # ======================
        clean_k = clean_id(k)
        node_ids = []
        print(f"\n=== [处理三类杆件] {clean_k} ===")

        for i, pt in enumerate(seg):
            nid = get_safe_nid(node_id_base(k))
            x3d, _, z3d = projector(pt[0], pt[1])

            h_t1 = h1_t1 if i == 0 else h2_t1
            h_t2 = h1_t2 if i == 0 else h2_t2

            # --------------------
            # 情况 A：吸附在【一类主腿】
            # --------------------
            if h_t1:
                real_host_id = node_id_base(h_t1)  # 关键修复：用真实吸附的主腿ID
                ref_x = f"{real_host_id}10"
                ref_y = f"{real_host_id}20"

                jiedian.append({
                    "node_id": str(nid),
                    "node_type": 12,
                    "symmetry_type": 4,
                    "X": ref_x,
                    "Y": ref_y,
                    "Z": z3d
                })
                print(f"节点 {nid} → 吸附一类 {real_host_id} | 引用: {ref_x}, {ref_y} | Z={z3d}")

            # --------------------
            # 情况 B：吸附在【二类杆件】
            # --------------------
            elif h_t2:
                real_host_id = node_id_base(h_t2)
                if real_host_id in tier2_nodes_map:
                    rn1, rn2 = tier2_nodes_map[real_host_id]
                    jiedian.append({
                        "node_id": str(nid),
                        "node_type": 12,
                        "symmetry_type": 4,
                        "X": x3d,
                        "Y": rn1,
                        "Z": rn2
                    })
                    print(f"节点 {nid} → 吸附二类 {real_host_id} | 引用节点: {rn1}, {rn2} | X={x3d}")
                else:
                    jiedian.append({
                        "node_id": str(nid),
                        "node_type": 12,
                        "symmetry_type": 4,
                        "X": x3d,
                        "Y": f"{real_host_id}10",
                        "Z": f"{real_host_id}20"
                    })
                    print(f"节点 {nid} → 吸附二类 {real_host_id}（兜底）")

            node_ids.append(str(nid))

        # ======================
        # 生成正面 + 侧面 杆件（不重复、不乱来）
        # ======================
        if len(node_ids) == 2:
            n1, n2 = node_ids[0], node_ids[1]

            # 正面
            ganjian.append({
                "member_id": clean_k,
                "node1_id": n1,
                "node2_id": n2,
                "symmetry_type": 4
            })
            # 侧面（引擎自动90度）
            ganjian.append({
                "member_id": clean_k,
                "node1_id": n1,
                "node2_id": f"{n2[:-1]}3",
                "symmetry_type": 2
            })
            print(f"[生成三类杆件] {clean_k} 正面 {n1}→{n2} | 侧面 {n1}→{n2[:-1]}3")

    print(f"[完成] 1109 必生成版结束，共生成节点数: {len(jiedian)}")
    print("="*50 + "\n")

    return ganjian, jiedian


def _make_node_record(
    node_id,
    node_type,
    symmetry_type,
    x_value,
    y_value,
    z_value,
    front_xy,
    export=True,
    view_face="front",
):
    return {
        "node_id": str(node_id),
        "node_type": int(node_type),
        "symmetry_type": int(symmetry_type),
        "X": x_value,
        "Y": y_value,
        "Z": z_value,
        "_xyz": (x_value, y_value, z_value),
        "_front_xy": tuple(front_xy) if front_xy is not None else None,
        "_view_face": str(view_face),
        "_member_links": [],
        "_export": bool(export),
    }


def _upsert_node_record(
    node_records,
    node_id,
    node_type,
    symmetry_type,
    x_value,
    y_value,
    z_value,
    front_xy,
    export=True,
    view_face="front",
):
    node_id = str(node_id)
    record = node_records.get(node_id)
    if record is None:
        record = _make_node_record(
            node_id, node_type, symmetry_type, x_value, y_value, z_value, front_xy,
            export=export, view_face=view_face
        )
        node_records[node_id] = record
        return record

    record["node_type"] = int(node_type)
    record["symmetry_type"] = int(symmetry_type)
    record["X"] = x_value
    record["Y"] = y_value
    record["Z"] = z_value
    record["_xyz"] = (x_value, y_value, z_value)
    record["_front_xy"] = tuple(front_xy) if front_xy is not None else None
    record["_view_face"] = str(view_face)
    record["_export"] = record["_export"] or bool(export)
    return record


def _ensure_virtual_node(node_records, node_id, source_id):
    node_id = str(node_id)
    if node_id in node_records:
        return node_records[node_id]

    source = node_records.get(str(source_id))
    if source is None:
        source = _make_node_record(node_id, 11, 4, None, None, None, None, export=False)
    record = _make_node_record(
        node_id,
        source["node_type"],
        source["symmetry_type"],
        source["X"],
        source["Y"],
        source["Z"],
        source["_front_xy"],
        export=False,
        view_face=source.get("_view_face", "front"),
    )
    node_records[node_id] = record
    return record


def _register_member_from_nodes(
    node_records,
    member_specs,
    member_order,
    member_id,
    symmetry_type,
    node_ids,
    variant,
    source_ids=None,
    debug_member_trace=False,
):
    connection_key = f"{member_id}|{symmetry_type}|{variant}"
    if debug_member_trace:
        print(
            f"[TRACE register] init connection_key={connection_key} | "
            f"member_id={member_id} symmetry_type={symmetry_type} variant={variant}"
        )
    if connection_key not in member_specs:
        member_specs[connection_key] = {
            "member_id": str(member_id),
            "symmetry_type": int(symmetry_type),
            "variant": str(variant),
            "preferred_nodes": tuple(str(node_id) for node_id in node_ids),
        }
        member_order.append(connection_key)
        if debug_member_trace:
            print(f"[TRACE register] new member_spec created for {connection_key}")
    elif debug_member_trace:
        print(f"[TRACE register] member_spec already exists for {connection_key}")

    source_ids = source_ids or node_ids
    pair_list = list(zip(node_ids, source_ids))
    if debug_member_trace:
        print(
            f"[TRACE register] node_ids={tuple(str(n) for n in node_ids)} | "
            f"source_ids={tuple(str(s) for s in source_ids)} | pairs={pair_list}"
        )

    for node_id, source_id in zip(node_ids, source_ids):
        node_id = str(node_id)
        source_id = str(source_id)
        if node_id not in node_records:
            _ensure_virtual_node(node_records, node_id, source_id)
            if debug_member_trace:
                print(
                    f"[TRACE register] virtual node created: node_id={node_id} "
                    f"from source_id={source_id}"
                )
        links = node_records[node_id]["_member_links"]
        if connection_key not in links:
            links.append(connection_key)
            if debug_member_trace:
                print(
                    f"[TRACE register] append link: node_id={node_id} "
                    f"link={connection_key}"
                )
        elif debug_member_trace:
            print(
                f"[TRACE register] link already exists: node_id={node_id} "
                f"link={connection_key}"
            )


def _build_members_from_node_records(
    node_records,
    member_specs,
    member_order,
    resolve_node_xyz=None,
    debug_member_trace=False,
):
    source_id_counts = {}
    for connection_key in member_order:
        source_id = str(member_specs[connection_key]["member_id"])
        source_id_counts[source_id] = source_id_counts.get(source_id, 0) + 1

    source_id_seen = {}
    reserved_source_ids = set(source_id_counts)
    used_output_ids = set()
    ganjian = []
    for connection_key in member_order:
        spec = member_specs[connection_key]
        endpoints = [
            node_id for node_id, record in node_records.items()
            if connection_key in record["_member_links"]
        ]
        if debug_member_trace:
            print(
                f"[TRACE build] connection_key={connection_key} "
                f"-> endpoints={endpoints} (count={len(endpoints)})"
            )
        if len(endpoints) < 2:
            print(f"[警告] 杆件 {spec['member_id']} 找到 {len(endpoints)} 个端点，已跳过")
            continue

        preferred = list(spec["preferred_nodes"])
        ordered = [node_id for node_id in preferred if node_id in endpoints]
        ordered.extend(node_id for node_id in endpoints if node_id not in ordered)
        endpoint_pairs = [(ordered[0], ordered[1])]
        if len(endpoints) > 2:
            if resolve_node_xyz is None:
                print(
                    f"[警告] 杆件 {spec['member_id']} 找到 {len(endpoints)} 个端点，"
                    "但没有坐标解析器，已跳过"
                )
                continue
            start_point = resolve_node_xyz(ordered[0])
            end_point = resolve_node_xyz(ordered[1])
            if start_point is None or end_point is None:
                print(f"[警告] 杆件 {spec['member_id']} 的分段端点无法解析，已跳过")
                continue
            direction = tuple(end_point[index] - start_point[index] for index in range(3))
            length_squared = sum(value * value for value in direction)
            if length_squared <= 1e-18:
                print(f"[警告] 杆件 {spec['member_id']} 两端重合，已跳过")
                continue

            positioned = []
            for node_id in endpoints:
                point = resolve_node_xyz(node_id)
                if point is None:
                    continue
                parameter = sum(
                    (point[index] - start_point[index]) * direction[index]
                    for index in range(3)
                ) / length_squared
                positioned.append((parameter, str(node_id)))
            positioned.sort(key=lambda item: (item[0], item[1]))
            endpoint_pairs = [
                (positioned[index][1], positioned[index + 1][1])
                for index in range(len(positioned) - 1)
                if positioned[index][1] != positioned[index + 1][1]
            ]

        source_member_id = str(spec["member_id"])
        for node1_id, node2_id in endpoint_pairs:
            instance_index = source_id_seen.get(source_member_id, 0) + 1
            source_id_seen[source_member_id] = instance_index

            # A single front drawing exports one front-face family and one
            # rotated side-face family. Splitting at real contacts can create
            # further physical instances; every row therefore needs a unique
            # collision-safe ID while retaining the source ID prefix.
            output_member_id = source_member_id
            if instance_index > 1:
                suffix = instance_index
                output_member_id = f"{source_member_id}_{suffix}"
                while (
                    output_member_id in used_output_ids
                    or output_member_id in reserved_source_ids
                ):
                    suffix += 1
                    output_member_id = f"{source_member_id}_{suffix}"
            used_output_ids.add(output_member_id)

            ganjian.append({
                "member_id": output_member_id,
                "node1_id": node1_id,
                "node2_id": node2_id,
                "symmetry_type": spec["symmetry_type"],
            })
    return ganjian


def _debug_dump_member_links(node_records):
    print("\n" + "-" * 50)
    print("[调试] 节点 _member_links 明细")
    print("-" * 50)
    for node_id in sorted(node_records.keys(), key=lambda x: (len(str(x)), str(x))):
        record = node_records[node_id]
        links = record.get("_member_links", [])
        print(
            f"node_id={node_id} | export={record.get('_export')} | "
            f"node_type={record.get('node_type')} | links_count={len(links)}"
        )
        if links:
            for idx, link in enumerate(links, start=1):
                print(f"  {idx:02d}. {link}")
        else:
            print("  (empty)")
    print("-" * 50 + "\n")


def _export_node_records(node_records, include_view_face=False):
    jiedian = []
    for record in node_records.values():
        if not record["_export"]:
            continue
        node = {
            "node_id": record["node_id"],
            "node_type": record["node_type"],
            "symmetry_type": record["symmetry_type"],
            "X": record["X"],
            "Y": record["Y"],
            "Z": record["Z"],
        }
        if include_view_face:
            node["_view_face"] = record.get("_view_face", "front")
        jiedian.append(node)
    return jiedian


def _export_debug_node_records(node_records):
    debug_nodes = []
    for record in node_records.values():
        debug_nodes.append({
            "node_id": record["node_id"],
            "node_type": record["node_type"],
            "symmetry_type": record["symmetry_type"],
            "X": record["X"],
            "Y": record["Y"],
            "Z": record["Z"],
            "_xyz": record.get("_xyz"),
            "_front_xy": record.get("_front_xy"),
            "_member_links": list(record.get("_member_links", [])),
            "_export": bool(record.get("_export", False)),
            "_view_face": record.get("_view_face", "front"),
        })
    return debug_nodes


def single_view0201(
    line_coord,
    debug_member_links=False,
    return_debug_nodes=False,
    debug_member_trace=False,
    front_only=False,
    keep_view_face=False,
    main_rod_ids=None,
    symmetry_axis=None,
):
    print("\n" + "=" * 50)
    print("====== 开始执行严格 6 步引用拓扑法（节点记录驱动版） ======")

    real_lines01 = extract_lines01(line_coord, main_rod_ids)
    if not real_lines01:
        return ([], [], []) if return_debug_nodes else ([], [])

    lines01 = dict(real_lines01)
    virtual_support_aliases = {}
    if len(lines01) == 1:
        if symmetry_axis is None:
            return ([], [], []) if return_debug_nodes else ([], [])
        real_id, real_segment = next(iter(lines01.items()))
        virtual_id = f"__asym_mirror__{real_id}"
        axis_x = float(symmetry_axis)
        lines01[virtual_id] = [
            (2.0 * axis_x - point[0], point[1])
            for point in real_segment
        ]
        virtual_support_aliases[virtual_id] = str(real_id)

    proj_result = build_projector(lines01)
    if not proj_result:
        return ([], [], []) if return_debug_nodes else ([], [])
    projector, center_x_cad = proj_result

    special_bar_id = node_id_base(next(iter(lines01.keys())))
    def has_explicit_mirror_pair(raw_member_id):
        """Return whether the front drawing already contains the mirrored rod."""

        source_segment = line_coord.get(raw_member_id)
        if not source_segment or len(source_segment) != 2:
            return False

        mirrored = [
            (2.0 * center_x_cad - float(point[0]), float(point[1]))
            for point in source_segment
        ]

        def endpoint_error(candidate):
            direct = max(
                math.dist(mirrored[0], candidate[0]),
                math.dist(mirrored[1], candidate[1]),
            )
            reversed_error = max(
                math.dist(mirrored[0], candidate[1]),
                math.dist(mirrored[1], candidate[0]),
            )
            return min(direct, reversed_error)

        for candidate_id, candidate_segment in line_coord.items():
            if candidate_id == raw_member_id or len(candidate_segment) != 2:
                continue
            candidate = [
                (float(point[0]), float(point[1]))
                for point in candidate_segment
            ]
            # The two sides in real CAD drawings are often tens of drawing
            # units apart after reflection because endpoints are not drafted
            # perfectly symmetrically. Both endpoints must match, so 100 is
            # still narrow enough to avoid pairing unrelated members.
            if endpoint_error(candidate) <= 100.0:
                return True
        return False

    used_nids = set()
    node_records = {}
    member_specs = {}
    member_order = []
    tier1_nodes_map = {}
    tier1_symmetry_map = {}

    def get_safe_nid(base_id):
        for suffix in range(10, 100, 10):
            test_nid = f"{base_id}{suffix}"
            if test_nid not in used_nids:
                used_nids.add(test_nid)
                return test_nid
        return f"{base_id}99"

    def add_node(
        node_id,
        node_type,
        symmetry_type,
        x_value,
        y_value,
        z_value,
        front_xy,
        export=True,
        view_face="front",
    ):
        return _upsert_node_record(
            node_records, node_id, node_type, symmetry_type, x_value, y_value, z_value,
            front_xy, export=export, view_face=view_face
        )

    def add_member(member_id, symmetry_type, node1_id, node2_id, variant, source1=None, source2=None):
        _register_member_from_nodes(
            node_records,
            member_specs,
            member_order,
            member_id=str(member_id),
            symmetry_type=int(symmetry_type),
            node_ids=(str(node1_id), str(node2_id)),
            variant=str(variant),
            source_ids=(source1 or node1_id, source2 or node2_id),
            debug_member_trace=debug_member_trace,
        )

    def _replace_node_suffix(node_id, suffix):
        node_id = str(node_id)
        return f"{node_id[:-1]}{suffix}"

    def _front_x(node_id):
        record = node_records.get(str(node_id), {})
        front_xy = record.get("_front_xy")
        if not front_xy:
            return None
        return front_xy[0]

    def _front_y(node_id):
        record = node_records.get(str(node_id), {})
        front_xy = record.get("_front_xy")
        if not front_xy:
            return None
        return front_xy[1]

    def _side_face_endpoint_pair(node1_id, node2_id):
        """
        Build an explicit side-face diagonal from a front-view member.
        Cross-body members use the opposite-corner (+3) endpoint; same-side
        members use the depth mirror (+2). This avoids depending on CAD input
        order, which can flip X-brace side members.
        """
        node1_id = str(node1_id)
        node2_id = str(node2_id)
        x1 = _front_x(node1_id)
        x2 = _front_x(node2_id)

        if x1 is None or x2 is None:
            return node1_id, _replace_node_suffix(node2_id, "3"), node2_id

        side1 = -1 if x1 < center_x_cad else 1
        side2 = -1 if x2 < center_x_cad else 1

        if side1 != side2:
            left_id, right_id = (node1_id, node2_id) if x1 < x2 else (node2_id, node1_id)
            return left_id, _replace_node_suffix(right_id, "3"), right_id

        y1 = _front_y(node1_id)
        y2 = _front_y(node2_id)
        if y1 is not None and y2 is not None and y2 < y1:
            node1_id, node2_id = node2_id, node1_id
        return node1_id, _replace_node_suffix(node2_id, "2"), node2_id

    def _side_face_projection(node1_id, node2_id):
        side_node1, side_node2, source2 = _side_face_endpoint_pair(node1_id, node2_id)
        source1 = str(node1_id) if side_node1 == str(node1_id) else str(node2_id)
        return side_node1, side_node2, {
            source1: str(side_node1),
            str(source2): str(side_node2),
        }

    def _resolve_node_xyz(node_id, resolving=None):
        """Resolve a local type-11/type-12 record to a real 3D point."""
        node_id = str(node_id)
        resolving = set() if resolving is None else resolving
        if node_id in resolving:
            return None
        record = node_records.get(node_id)
        if record is None:
            return None

        values = record.get("_xyz", (record["X"], record["Y"], record["Z"]))
        reference_indexes = [index for index, value in enumerate(values) if isinstance(value, str)]
        if not reference_indexes:
            return tuple(float(value) for value in values)
        if len(reference_indexes) != 2:
            return None

        real_index = next(index for index in range(3) if index not in reference_indexes)
        point_a = _resolve_node_xyz(values[reference_indexes[0]], resolving | {node_id})
        point_b = _resolve_node_xyz(values[reference_indexes[1]], resolving | {node_id})
        if point_a is None or point_b is None:
            return None

        span = point_b[real_index] - point_a[real_index]
        if abs(span) < 1e-9:
            return None
        ratio = (float(values[real_index]) - point_a[real_index]) / span
        return tuple(
            float(values[real_index]) if index == real_index
            else point_a[index] + ratio * (point_b[index] - point_a[index])
            for index in range(3)
        )

    def _symmetry_point(point, delta):
        """Return the point represented by one SmartTower symmetry suffix."""
        x_value, y_value, z_value = point
        return (
            -x_value if delta in (1, 3) else x_value,
            -y_value if delta in (2, 3) else y_value,
            z_value,
        )

    def _symmetry_node_id(node_id, delta):
        """Apply SmartTower's two-digit node-suffix expansion rule."""
        node_id = str(node_id)
        suffix = node_id[-2:]
        if not suffix.isdigit():
            return None
        return f"{node_id[:-2]}{int(suffix) + delta:02d}"

    def _find_existing_spatial_node(
        point,
        point_tolerance=NODE_REUSE_TOLERANCE,
        source_node_id=None,
        side_reuse_only=False,
    ):
        """
        Find an exported node, including an implicit symmetry copy, at point.

        Side-face rods must connect to the same topology IDs as the front-face
        family at a tower corner.  Merely creating another node at the same
        coordinates leaves two disconnected graph vertices.
        """
        matches = []
        for source_id, record in node_records.items():
            if not record.get("_export"):
                continue
            if source_node_id is not None and str(source_id) != str(source_node_id):
                continue

            linked_variants = {
                str(member_specs[connection_key].get("variant", ""))
                for connection_key in record.get("_member_links", [])
            }
            is_tier1 = "tier1-main" in linked_variants
            is_side_node = (
                record.get("_view_face") == "side"
                or any(variant.endswith("-side") for variant in linked_variants)
            )
            if side_reuse_only and not (is_tier1 or is_side_node):
                continue

            source_point = _resolve_node_xyz(source_id)
            if source_point is None:
                continue
            symmetry_type = int(record.get("symmetry_type", 0) or 0)
            deltas = [0]
            if symmetry_type in (1, 2, 3):
                deltas.append(symmetry_type)
            elif symmetry_type == 4:
                deltas.extend((1, 2, 3))
            for delta in deltas:
                candidate_point = (
                    source_point if delta == 0
                    else _symmetry_point(source_point, delta)
                )
                distance = math.dist(point, candidate_point)
                if distance > point_tolerance:
                    continue
                candidate_id = (
                    str(source_id) if delta == 0
                    else _symmetry_node_id(source_id, delta)
                )
                if candidate_id is not None:
                    matches.append(
                        (
                            distance,
                            not is_tier1,
                            delta != 0,
                            candidate_id,
                            candidate_point,
                        )
                    )
        if not matches:
            return None
        _, _, _, candidate_id, candidate_point = min(
            matches, key=lambda item: item[:4]
        )
        if candidate_id not in node_records:
            add_node(
                candidate_id,
                11,
                0,
                candidate_point[0],
                candidate_point[1],
                candidate_point[2],
                None,
                export=False,
                view_face="side" if side_reuse_only or source_node_id else "front",
            )
        return candidate_id

    def _reuse_or_add_tier1_side_node(node_base, point, source_node_id):
        """Snap a side endpoint to a real tier-1 instance and reference it."""
        candidates = []
        for host_key, endpoint_ids in tier1_nodes_map.items():
            if str(host_key) not in tier1_symmetry_map:
                continue
            point1 = _resolve_node_xyz(endpoint_ids[0])
            point2 = _resolve_node_xyz(endpoint_ids[1])
            if point1 is None or point2 is None:
                continue

            symmetry_type = tier1_symmetry_map.get(str(host_key), 4)
            deltas = [0]
            if symmetry_type in (1, 2, 3):
                deltas.append(symmetry_type)
            elif symmetry_type == 4:
                deltas.extend((1, 2, 3))

            for delta in deltas:
                host_point1 = (
                    point1 if delta == 0 else _symmetry_point(point1, delta)
                )
                host_point2 = (
                    point2 if delta == 0 else _symmetry_point(point2, delta)
                )
                direction = tuple(
                    host_point2[index] - host_point1[index]
                    for index in range(3)
                )
                length_squared = sum(value * value for value in direction)
                if length_squared <= 1e-18:
                    continue
                raw_ratio = sum(
                    (point[index] - host_point1[index]) * direction[index]
                    for index in range(3)
                ) / length_squared
                ratio = max(0.0, min(1.0, raw_ratio))
                host_length = math.sqrt(length_squared)
                endpoint_margin_ratio = min(
                    0.5,
                    (NODE_REUSE_TOLERANCE * 0.1) / host_length,
                )
                if ratio <= endpoint_margin_ratio:
                    ratio = 0.0
                elif ratio >= 1.0 - endpoint_margin_ratio:
                    ratio = 1.0
                projected = tuple(
                    host_point1[index] + ratio * direction[index]
                    for index in range(3)
                )
                distance = math.dist(point, projected)
                if distance > NODE_REUSE_TOLERANCE:
                    continue

                base_projected = tuple(
                    point1[index] + ratio * (point2[index] - point1[index])
                    for index in range(3)
                )
                candidates.append(
                    (
                        distance,
                        str(host_key),
                        delta,
                        projected,
                        base_projected,
                        endpoint_ids,
                    )
                )

        if not candidates:
            return None

        _, host_key, delta, projected, base_projected, endpoint_ids = min(
            candidates, key=lambda item: item[:3]
        )

        ref1, ref2 = str(endpoint_ids[0]), str(endpoint_ids[1])
        ref1_point = _resolve_node_xyz(ref1)
        ref2_point = _resolve_node_xyz(ref2)

        real_axis = max(
            range(3),
            key=lambda index: abs(ref2_point[index] - ref1_point[index]),
        )
        values = []
        reference_values = iter((str(ref1), str(ref2)))
        for axis_index in range(3):
            if axis_index == real_axis:
                values.append(round(base_projected[axis_index], 9))
            else:
                values.append(next(reference_values))

        host_connection_key = next(
            (
                connection_key
                for connection_key, spec in member_specs.items()
                if str(spec.get("member_id")) == str(host_key)
                and str(spec.get("variant")) == "tier1-main"
            ),
            None,
        )
        canonical_id = find_existing_tier1_front_node(
            host_key,
            base_projected,
            point_tolerance=NODE_REUSE_TOLERANCE,
        )
        if canonical_id is None:
            canonical_id = str(get_safe_nid(node_base))
            add_node(
                canonical_id,
                12,
                4,
                values[0],
                values[1],
                values[2],
                None,
                export=True,
                view_face="front",
            )
            node_records[canonical_id].setdefault("_tier1_host_keys", set()).add(
                str(host_key)
            )

        # The tier-1 member is split by the canonical front node. Its member
        # symmetry then creates the same split on the side instance, where the
        # rotated brace reuses the corresponding suffix node.
        if host_connection_key is not None:
            links = node_records[canonical_id]["_member_links"]
            if host_connection_key not in links:
                links.append(host_connection_key)

        if delta == 0:
            return canonical_id
        side_id = _symmetry_node_id(canonical_id, delta)
        if side_id is None:
            return None
        if side_id not in node_records:
            canonical_point = _resolve_node_xyz(canonical_id)
            if canonical_point is None:
                return None
            side_point = _symmetry_point(canonical_point, delta)
            add_node(
                side_id,
                11,
                0,
                side_point[0],
                side_point[1],
                side_point[2],
                None,
                export=False,
                view_face="side",
            )
        return str(side_id)

    def _reuse_or_add_side_host_node(node_base, point, host_kind, host_key):
        """Create a type-12 endpoint on the already-built side host."""
        if host_kind == "tier2":
            side_info = tier2_side_nodes_map.get(str(host_key))
        elif host_kind == "tier3":
            side_info = tier3_side_nodes_map.get(str(host_key))
        else:
            return None
        if not side_info:
            return None
        host_candidates = []
        for ref1, ref2 in side_info.get(
            "segments", (side_info["endpoints"],)
        ):
            point1 = _resolve_node_xyz(ref1)
            point2 = _resolve_node_xyz(ref2)
            if point1 is None or point2 is None:
                continue

            direction = tuple(point2[index] - point1[index] for index in range(3))
            length_squared = sum(value * value for value in direction)
            if length_squared <= 1e-18:
                continue
            raw_ratio = sum(
                (point[index] - point1[index]) * direction[index]
                for index in range(3)
            ) / length_squared
            ratio = max(0.0, min(1.0, raw_ratio))
            host_length = math.sqrt(length_squared)
            endpoint_margin_ratio = min(
                0.5,
                (NODE_REUSE_TOLERANCE * 0.1) / host_length,
            )
            if ratio <= endpoint_margin_ratio:
                ratio = 0.0
            elif ratio >= 1.0 - endpoint_margin_ratio:
                ratio = 1.0
            projected = tuple(
                point1[index] + ratio * direction[index]
                for index in range(3)
            )
            distance = math.dist(point, projected)
            if distance <= NODE_REUSE_TOLERANCE:
                host_candidates.append(
                    (distance, str(ref1), str(ref2), point1, point2, projected)
                )
        if not host_candidates:
            return None
        _, ref1, ref2, point1, point2, projected = min(
            host_candidates, key=lambda item: item[:3]
        )

        existing_id = _find_existing_spatial_node(
            projected,
            point_tolerance=1e-7,
            side_reuse_only=True,
        )
        if existing_id is not None:
            return str(existing_id)

        real_axis = max(
            range(3),
            key=lambda index: abs(point2[index] - point1[index]),
        )
        values = []
        reference_values = iter((str(ref1), str(ref2)))
        for axis_index in range(3):
            if axis_index == real_axis:
                values.append(round(projected[axis_index], 9))
            else:
                values.append(next(reference_values))

        node_id = get_safe_nid(node_base)
        add_node(
            node_id,
            12,
            4,
            values[0],
            values[1],
            values[2],
            None,
            export=True,
            view_face="side",
        )
        return str(node_id)

    def _reuse_or_add_side_node(
        node_base,
        point,
        source_node_id,
        host_kind=None,
        host_key=None,
    ):
        """Reuse the endpoint's own symmetry or a side/tier-1 node only."""
        tier1_node_id = _reuse_or_add_tier1_side_node(
            node_base, point, source_node_id
        )
        if tier1_node_id is not None:
            return tier1_node_id

        side_host_node_id = _reuse_or_add_side_host_node(
            node_base, point, host_kind, host_key
        )
        if side_host_node_id is not None:
            return side_host_node_id

        # At a tower corner, the rotated endpoint is an implicit symmetry copy
        # of the front endpoint.  That identity is stronger than a global
        # nearest-node match and preserves the type-12 host reference.
        existing_id = _find_existing_spatial_node(
            point,
            source_node_id=source_node_id,
        )
        if existing_id is None:
            # Never let a side endpoint attach to an unrelated front
            # horizontal/X-brace merely because it is inside the 150 mm EPS.
            existing_id = _find_existing_spatial_node(
                point,
                side_reuse_only=True,
            )
        if existing_id is not None:
            # Reuse the canonical coordinate verbatim.  Replacing an implicit
            # main-rod symmetry node with the noisy rotated endpoint would
            # move that node off the straight tier-1 line.
            return str(existing_id)

        node_id = get_safe_nid(node_base)
        add_node(
            node_id,
            11,
            4,
            point[0],
            point[1],
            point[2],
            None,
            export=True,
            view_face="side",
        )
        return str(node_id)

    def _add_rotated_side_member(
        member_id,
        node_base,
        node1_id,
        node2_id,
        variant,
        member_symmetry_type=4,
        endpoint_infos=None,
    ):
        """Create one true side-face member by rotating both front endpoints."""
        point1 = _resolve_node_xyz(node1_id)
        point2 = _resolve_node_xyz(node2_id)
        if point1 is None or point2 is None:
            print(f"[跳过侧面] 杆件 {member_id} 的正面端点无法解析")
            return None

        x1, y1, z1 = point1
        x2, y2, z2 = point2
        endpoint_infos = endpoint_infos or ({}, {})
        side_node1 = _reuse_or_add_side_node(
            node_base,
            (y1, -x1, z1),
            node1_id,
            endpoint_infos[0].get("host_kind"),
            endpoint_infos[0].get("host_key"),
        )
        side_node2 = _reuse_or_add_side_node(
            node_base,
            (y2, -x2, z2),
            node2_id,
            endpoint_infos[1].get("host_kind"),
            endpoint_infos[1].get("host_key"),
        )
        use_explicit_mirror = member_symmetry_type == 1
        add_member(
            member_id,
            0 if use_explicit_mirror else member_symmetry_type,
            side_node1,
            side_node2,
            variant=variant,
        )
        segments = [(str(side_node1), str(side_node2))]
        if use_explicit_mirror:
            mirrored_node1 = _reuse_or_add_side_node(
                node_base,
                _symmetry_point((y1, -x1, z1), 1),
                node1_id,
                endpoint_infos[0].get("host_kind"),
                endpoint_infos[0].get("host_key"),
            )
            mirrored_node2 = _reuse_or_add_side_node(
                node_base,
                _symmetry_point((y2, -x2, z2), 1),
                node2_id,
                endpoint_infos[1].get("host_kind"),
                endpoint_infos[1].get("host_key"),
            )
            add_member(
                member_id,
                0,
                mirrored_node1,
                mirrored_node2,
                variant=variant.replace("-side", "-mirror-side"),
            )
            segments.append((str(mirrored_node1), str(mirrored_node2)))
        return {
            "endpoints": segments[0],
            "segments": tuple(segments),
        }

    tier2_nodes_map = {}
    tier2_side_nodes_map = {}

    for k, seg in real_lines01.items():
        clean_k = clean_id(k)
        member_k = member_instance_id(k)
        node_ids = []
        # Keep the main-leg endpoint IDs consistent with single_view01:
        # ..10 is the lower endpoint and ..20 is the upper endpoint.  CAD
        # segments are not consistently ordered, while later seam correction
        # uses these suffixes as physical bottom/top identifiers.
        ordered_points = sorted(seg, key=lambda pt: projector(pt[0], pt[1])[2])
        for pt in ordered_points:
            nid = get_safe_nid(node_id_base(k))
            x3d, y3d, z3d = projector(pt[0], pt[1])
            # Keep the two tier1 main legs on the same reference side plane
            # while preserving their left/right X symmetry.
            tier1_y3d = -abs(x3d)
            add_node(nid, 11, 4, x3d, tier1_y3d, z3d, pt, export=True)
            node_ids.append(str(nid))
        tier1_nodes_map[member_k] = (node_ids[0], node_ids[1])
        tier1_symmetry_type = 2 if has_explicit_mirror_pair(k) else 4
        tier1_symmetry_map[member_k] = tier1_symmetry_type
        add_member(
            member_k,
            tier1_symmetry_type,
            node_ids[0],
            node_ids[1],
            variant="tier1-main",
        )

    # A symmetric single-view sheet describes one horizontal tower segment,
    # but CAD endpoints on its left/right main legs are commonly several
    # drawing units apart in Y.  If those raw values become Z unchanged, each
    # splice aligns only one side and the error accumulates up the tower.
    # Level the two physical main-leg endpoints before dependent nodes are
    # resolved.  Asymmetric/high-low-slope sheets expose only one real leg and
    # are intentionally left untouched.
    real_main_pairs = [
        tier1_nodes_map[member_instance_id(member_id)]
        for member_id in real_lines01
        if member_instance_id(member_id) in tier1_nodes_map
    ]
    if len(real_main_pairs) >= 2:
        for endpoint_index in (0, 1):
            records = [
                node_records[str(node_pair[endpoint_index])]
                for node_pair in real_main_pairs
            ]
            level_z = sum(float(record["Z"]) for record in records) / len(records)
            for record in records:
                record["Z"] = round(level_z, 6)
                xyz = record.get("_xyz")
                if xyz is not None:
                    record["_xyz"] = (xyz[0], xyz[1], round(level_z, 6))

    def find_existing_front_node_at_point(expected_point, point_tolerance=1e-7):
        """Reuse a front node only when its resolved 3-D point is identical."""

        candidates = []
        for source_id, record in node_records.items():
            if record.get("_view_face") != "front" or not record.get("_export"):
                continue
            source_point = _resolve_node_xyz(source_id)
            if source_point is None:
                continue
            symmetry_type = int(record.get("symmetry_type", 0) or 0)
            deltas = [0]
            if symmetry_type in (1, 2, 3):
                deltas.append(symmetry_type)
            elif symmetry_type == 4:
                deltas.extend((1, 2, 3))
            for delta in deltas:
                candidate_point = (
                    source_point if delta == 0
                    else _symmetry_point(source_point, delta)
                )
                distance = math.dist(expected_point, candidate_point)
                if distance > point_tolerance:
                    continue
                candidate_id = (
                    str(source_id) if delta == 0
                    else _symmetry_node_id(source_id, delta)
                )
                if candidate_id is not None:
                    candidates.append((distance, delta != 0, candidate_id))

        if not candidates:
            return None

        _, is_implicit, node_id = min(
            candidates, key=lambda item: (item[0], item[1], item[2])
        )
        if is_implicit and node_id not in node_records:
            add_node(
                node_id,
                11,
                0,
                expected_point[0],
                expected_point[1],
                expected_point[2],
                None,
                export=False,
                view_face="front",
            )
        return str(node_id)

    def find_existing_tier1_front_node(
        host_key,
        expected_point,
        point_tolerance=NODE_REUSE_TOLERANCE,
    ):
        """Reuse the nearest front node attached to the same tier-1 host."""
        host_key = str(host_key)
        candidates = []
        for node_id, record in node_records.items():
            if not record.get("_export") or record.get("_view_face") != "front":
                continue
            linked_to_host = any(
                str(member_specs[connection_key].get("member_id")) == host_key
                and str(member_specs[connection_key].get("variant")) == "tier1-main"
                for connection_key in record.get("_member_links", [])
            )
            tagged_hosts = {
                str(value) for value in record.get("_tier1_host_keys", set())
            }
            if not linked_to_host and host_key not in tagged_hosts:
                continue
            candidate_point = _resolve_node_xyz(node_id)
            if candidate_point is None:
                continue
            distance = math.dist(expected_point, candidate_point)
            if distance <= point_tolerance:
                candidates.append((distance, str(node_id)))
        if not candidates:
            return None
        return min(candidates, key=lambda item: (item[0], item[1]))[1]

    for virtual_id, real_id in virtual_support_aliases.items():
        real_nodes = tier1_nodes_map.get(member_instance_id(real_id))
        if not real_nodes:
            continue
        virtual_nodes = []
        for real_node_id in real_nodes:
            virtual_node_id = _replace_node_suffix(real_node_id, "1")
            real_record = node_records.get(str(real_node_id))
            if real_record is not None:
                x_value, y_value, z_value = real_record.get(
                    "_xyz",
                    (real_record["X"], real_record["Y"], real_record["Z"]),
                )
                front_xy = real_record.get("_front_xy")
                mirrored_front_xy = (
                    (2.0 * float(symmetry_axis) - front_xy[0], front_xy[1])
                    if front_xy is not None
                    else None
                )
                add_node(
                    virtual_node_id,
                    11,
                    4,
                    -float(x_value),
                    float(y_value),
                    float(z_value),
                    mirrored_front_xy,
                    export=False,
                )
            virtual_nodes.append(virtual_node_id)
        tier1_nodes_map[member_instance_id(virtual_id)] = tuple(virtual_nodes)

    def _front_face_y_at_z(z3d):
        """Interpolate the front-face depth from the two outer main legs."""
        in_span_values = []
        nearest_values = []

        for main_rod_id in real_lines01:
            node_pair = tier1_nodes_map.get(member_instance_id(main_rod_id))
            if not node_pair:
                continue

            point1 = _resolve_node_xyz(node_pair[0])
            point2 = _resolve_node_xyz(node_pair[1])
            if point1 is None or point2 is None:
                continue

            z1, z2 = point1[2], point2[2]
            if abs(z2 - z1) < 1e-9:
                continue

            ratio = (z3d - z1) / (z2 - z1)
            clamped_ratio = max(0.0, min(1.0, ratio))
            y_value = point1[1] + clamped_ratio * (point2[1] - point1[1])
            z_min, z_max = sorted((z1, z2))
            span_gap = max(z_min - z3d, 0.0, z3d - z_max)
            nearest_values.append((span_gap, y_value))

            if -1e-6 <= ratio <= 1.0 + 1e-6:
                in_span_values.append(y_value)

        if in_span_values:
            return sum(in_span_values) / len(in_span_values)
        if nearest_values:
            min_gap = min(item[0] for item in nearest_values)
            closest = [
                y_value
                for gap, y_value in nearest_values
                if abs(gap - min_gap) < 1e-9
            ]
            return sum(closest) / len(closest)

        raise ValueError(
            f"Cannot determine the single-view front face at Z={z3d}"
        )

    unclassified = {k: v for k, v in line_coord.items() if k not in lines01}
    tolerance = EPS

    def find_host(pt, host_dict, host_depth=0):
        """Select a 2-D host and retain the original projection ratio."""
        best = None
        for host_key, seg in host_dict.items():
            if not seg or len(seg) < 2:
                continue
            d = dist_pt_seg(pt, seg[0], seg[1])
            if d > tolerance:
                continue
            dx = float(seg[1][0]) - float(seg[0][0])
            dy = float(seg[1][1]) - float(seg[0][1])
            length_squared = dx * dx + dy * dy
            if length_squared <= 1e-12:
                continue
            raw_ratio = (
                (float(pt[0]) - float(seg[0][0])) * dx
                + (float(pt[1]) - float(seg[0][1])) * dy
            ) / length_squared
            ratio = max(0.0, min(1.0, raw_ratio))
            length = math.sqrt(length_squared)
            endpoint_margin = max(1.0, tolerance * 0.1)
            margin_ratio = min(0.5, endpoint_margin / length)
            is_interior = margin_ratio < raw_ratio < 1.0 - margin_ratio
            candidate = (
                d,
                0 if is_interior else 1,
                int(host_depth),
                str(host_key),
                {
                    "host": member_instance_id(host_key),
                    "ratio": ratio,
                    "distance": d,
                    "interior": is_interior,
                    "depth": int(host_depth),
                },
            )
            if best is None or candidate[:4] < best[:4]:
                best = candidate
        return best[4] if best is not None else None

    def _host_reference_node_values(
        host_info,
        host_nodes_map,
        target_point,
    ):
        """Build a type-12 point using its original 2-D host ratio."""
        host_key = str(host_info["host"])
        if host_key in host_nodes_map:
            ref1, ref2 = host_nodes_map[host_key]
        else:
            real_host_id = node_id_base(host_key)
            ref1, ref2 = f"{real_host_id}10", f"{real_host_id}20"

        point1 = _resolve_node_xyz(ref1)
        point2 = _resolve_node_xyz(ref2)
        if point1 is None or point2 is None:
            raise ValueError(f"宿主杆件 {host_key} 的引用端点无法解析")

        source_ratio = max(0.0, min(1.0, float(host_info["ratio"])))
        candidates = (source_ratio, 1.0 - source_ratio)

        def candidate_point(ratio):
            return tuple(
                point1[index] + ratio * (point2[index] - point1[index])
                for index in range(3)
            )

        # CAD segment direction and exported node order are independent.
        # Select r or 1-r by the reconstructed X/Z target, then keep that
        # ratio unchanged through later sheet transformations.
        ratio = min(
            candidates,
            key=lambda value: (
                (candidate_point(value)[0] - target_point[0]) ** 2
                + (candidate_point(value)[2] - target_point[2]) ** 2
            ),
        )
        host_point = candidate_point(ratio)
        deltas = [abs(point2[index] - point1[index]) for index in range(3)]
        real_axis = max(range(3), key=lambda index: deltas[index])
        if deltas[real_axis] <= 1e-9:
            raise ValueError(f"宿主杆件 {host_key} 没有可用于引用的坐标跨度")

        values = [str(ref1), str(ref2)]
        result = []
        reference_index = 0
        for axis_index in range(3):
            if axis_index == real_axis:
                result.append(round(host_point[axis_index], 9))
            else:
                result.append(values[reference_index])
                reference_index += 1
        return tuple(result), host_point

    tier2_members = {}
    for k, seg in list(unclassified.items()):
        h1 = find_host(seg[0], lines01, host_depth=0)
        h2 = find_host(seg[1], lines01, host_depth=0)

        if h1 and h2:
            tier2_members[k] = seg
            del unclassified[k]

            clean_k = clean_id(k)
            member_k = member_instance_id(k)
            node_ids = []
            endpoint_hosts = {}
            for idx, pt in enumerate(seg):
                host_info = h1 if idx == 0 else h2
                host_key = str(host_info["host"])
                x3d, y3d, z3d = projector(pt[0], pt[1])
                node_values, host_point = _host_reference_node_values(
                    host_info,
                    tier1_nodes_map,
                    (x3d, y3d, z3d),
                )
                existing_node_id = find_existing_tier1_front_node(
                    host_key,
                    host_point,
                )
                if existing_node_id is not None:
                    node_id = existing_node_id
                else:
                    nid = get_safe_nid(node_id_base(k))
                    node_x, node_y, node_z = node_values
                    add_node(nid, 12, 4, node_x, node_y, node_z, pt, export=True)
                    node_id = str(nid)
                node_records[str(node_id)].setdefault(
                    "_tier1_host_keys", set()
                ).add(host_key)
                node_ids.append(str(node_id))
                endpoint_hosts[str(node_id)] = host_key

            is_horiz = abs(seg[0][1] - seg[1][1]) < 25.0
            side_nodes = None
            side_by_source = {}
            if is_horiz:
                # Use both real front endpoints.  The left/right main rods can
                # differ slightly, so mirroring one endpoint onto the other
                # would recreate the side-node gap this topology is avoiding.
                resolved_endpoints = [
                    _resolve_node_xyz(node_ids[0]),
                    _resolve_node_xyz(node_ids[1]),
                ]
                anchor_index = min(
                    range(2),
                    key=lambda index: (
                        resolved_endpoints[index][0]
                        if resolved_endpoints[index] is not None
                        else float("inf")
                    ),
                )
                anchor_id = str(node_ids[anchor_index])
                opposite_id = str(node_ids[1 - anchor_index])
                tier2_nodes_map[member_k] = (anchor_id, opposite_id)
                if not front_only:
                    add_member(
                        member_k,
                        2,
                        anchor_id,
                        opposite_id,
                        variant="tier2-horizontal-front",
                    )
                    side_segments = []
                    for side_index, source_id in enumerate(
                        (anchor_id, opposite_id), start=1
                    ):
                        source_point = _resolve_node_xyz(source_id)
                        virtual_id = _symmetry_node_id(source_id, 2)
                        if source_point is None or virtual_id is None:
                            continue
                        virtual_point = _symmetry_point(source_point, 2)
                        add_node(
                            virtual_id,
                            11,
                            0,
                            virtual_point[0],
                            virtual_point[1],
                            virtual_point[2],
                            None,
                            export=False,
                            view_face="side",
                        )
                        add_member(
                            member_k,
                            0,
                            source_id,
                            virtual_id,
                            variant=f"tier2-horizontal-{side_index}-side",
                        )
                        side_segments.append((source_id, virtual_id))
                    tier2_side_nodes_map[member_k] = {
                        "endpoints": side_segments[0],
                        "segments": tuple(side_segments),
                        "by_source": {anchor_id: anchor_id},
                        "endpoint_hosts": endpoint_hosts,
                    }
                else:
                    add_member(
                        member_k,
                        2,
                        anchor_id,
                        opposite_id,
                        variant="tier2-horizontal-front",
                    )
            else:
                tier2_nodes_map[member_k] = (node_ids[0], node_ids[1])
                paired = has_explicit_mirror_pair(k)
                add_member(
                    member_k,
                    2 if paired else 4,
                    node_ids[0],
                    node_ids[1],
                    variant="tier2-main",
                )
                if not front_only:
                    side_nodes = _add_rotated_side_member(
                        member_k,
                        node_id_base(k),
                        node_ids[0],
                        node_ids[1],
                        "tier2-side",
                        member_symmetry_type=1 if paired else 4,
                        endpoint_infos=(
                            {
                                "host_kind": "tier1",
                                "host_key": endpoint_hosts.get(str(node_ids[0])),
                            },
                            {
                                "host_kind": "tier1",
                                "host_key": endpoint_hosts.get(str(node_ids[1])),
                            },
                        ),
                    )
                    if side_nodes:
                        tier2_side_nodes_map[member_k] = {
                            **side_nodes,
                            "by_source": {},
                            "endpoint_hosts": endpoint_hosts,
                        }
    def _tier3_side_endpoint(node_base, endpoint_info, paired_info):
        node_id = str(endpoint_info["node_id"])
        host_kind = endpoint_info.get("host_kind")
        host_key = endpoint_info.get("host_key")

        if host_kind in {"tier2", "tier3"}:
            side_maps = {
                "tier2": tier2_side_nodes_map,
                "tier3": tier3_side_nodes_map,
            }
            side_info = side_maps[host_kind].get(str(host_key))
            if side_info:
                side_node_id = get_safe_nid(node_base)
                side_ref1, side_ref2 = side_info["endpoints"]
                add_node(
                    side_node_id,
                    12,
                    4,
                    side_ref1,
                    side_ref2,
                    endpoint_info["z"],
                    endpoint_info["front_xy"],
                    export=True,
                    view_face="side",
                )
                return str(side_node_id), str(side_node_id)
            return _replace_node_suffix(node_id, "2"), node_id

        if host_kind == "tier1":
            suffix = "2"
            if paired_info and paired_info.get("host_kind") in {"tier2", "tier3"}:
                paired_kind = paired_info["host_kind"]
                paired_maps = {
                    "tier2": tier2_side_nodes_map,
                    "tier3": tier3_side_nodes_map,
                }
                side_info = paired_maps[paired_kind].get(str(paired_info.get("host_key")))
                if side_info:
                    for source_id, source_host in side_info.get("endpoint_hosts", {}).items():
                        if source_host == host_key:
                            side_id = side_info.get("by_source", {}).get(source_id)
                            if side_id:
                                suffix = str(side_id)[-1]
                                break
            return _replace_node_suffix(node_id, suffix), node_id

        return _replace_node_suffix(node_id, "2"), node_id

    # Tier-3 braces may depend on another tier-3 brace.  Keep propagating
    # recognized hosts until no remaining member can be resolved.
    tier3_members = {}
    tier3_nodes_map = {}
    tier3_side_nodes_map = {}
    pending = dict(unclassified)
    shared_point_tol = max(3.0, tolerance * 0.1)
    shared_clusters = []
    shared_endpoint_keys = {}
    for member_id, seg in pending.items():
        for endpoint_index, pt in enumerate(seg):
            matched_index = None
            for cluster_index, cluster in enumerate(shared_clusters):
                cx, cy = cluster["centroid"]
                if math.hypot(pt[0] - cx, pt[1] - cy) <= shared_point_tol:
                    matched_index = cluster_index
                    break
            if matched_index is None:
                shared_clusters.append({
                    "centroid": (float(pt[0]), float(pt[1])),
                    "items": [],
                })
                matched_index = len(shared_clusters) - 1

            cluster = shared_clusters[matched_index]
            cluster["items"].append((member_id, endpoint_index, pt))
            count = len(cluster["items"])
            cx, cy = cluster["centroid"]
            cluster["centroid"] = (
                (cx * (count - 1) + float(pt[0])) / count,
                (cy * (count - 1) + float(pt[1])) / count,
            )
            shared_endpoint_keys[(member_id, endpoint_index)] = matched_index

    shared_cluster_keys = {
        cluster_index
        for cluster_index, cluster in enumerate(shared_clusters)
        if len({item[0] for item in cluster["items"]}) >= 2
    }
    shared_node_map = {}

    def resolve_host(pt):
        candidates = []
        for host_kind, host_members, host_depth in (
            ("tier1", lines01, 0),
            ("tier2", tier2_members, 1),
            ("tier3", tier3_members, 2),
        ):
            host_info = find_host(pt, host_members, host_depth=host_depth)
            if host_info is None:
                continue
            candidates.append((
                int(host_info["depth"]),
                float(host_info["distance"]),
                0 if host_info["interior"] else 1,
                str(host_info["host"]),
                host_kind,
                host_info,
            ))
        if not candidates:
            return None, None
        selected = min(candidates, key=lambda item: item[:4])
        return selected[4], selected[5]

    def shared_key_for(member_id, endpoint_index):
        cluster_key = shared_endpoint_keys.get((member_id, endpoint_index))
        if cluster_key in shared_cluster_keys:
            return cluster_key
        return None

    def get_or_create_shared_node(cluster_key, member_id, pt):
        if cluster_key in shared_node_map:
            return shared_node_map[cluster_key]

        nid = get_safe_nid(node_id_base(member_id))
        x3d, _, z3d = projector(pt[0], pt[1])
        front_y3d = _front_face_y_at_z(z3d)
        add_node(nid, 11, 4, x3d, front_y3d, z3d, pt, export=True)
        shared_node_map[cluster_key] = str(nid)
        return str(nid)

    while pending:
        resolved_count = 0
        for k, seg in list(pending.items()):
            endpoint_hosts = [resolve_host(pt) for pt in seg]
            endpoint_shared_keys = [
                shared_key_for(k, endpoint_index)
                for endpoint_index, _ in enumerate(seg)
            ]
            endpoint_ready = []
            for (_, host_info), shared_key in zip(endpoint_hosts, endpoint_shared_keys):
                endpoint_ready.append(
                    bool(host_info)
                    or shared_key in shared_node_map
                    or shared_key is not None
                )

            if not all(endpoint_ready):
                continue

            has_host = any(host_info for _, host_info in endpoint_hosts)
            has_existing_shared = any(
                shared_key in shared_node_map
                for shared_key in endpoint_shared_keys
                if shared_key is not None
            )
            if not has_host and not has_existing_shared:
                continue

            clean_k = clean_id(k)
            member_k = member_instance_id(k)
            node_ids = []
            endpoint_infos = []
            print(f"\n=== [处理三类杆件] {clean_k} ===")

            for endpoint_index, (pt, (host_kind, host_info)) in enumerate(zip(seg, endpoint_hosts)):
                x3d, _, z3d = projector(pt[0], pt[1])
                shared_key = endpoint_shared_keys[endpoint_index]
                if host_info:
                    host_key = str(host_info["host"])
                    if host_kind == "tier1":
                        host_nodes_map = tier1_nodes_map
                    elif host_kind == "tier2":
                        host_nodes_map = tier2_nodes_map
                    else:
                        host_nodes_map = tier3_nodes_map
                    front_y3d = _front_face_y_at_z(z3d)
                    node_values, host_point = _host_reference_node_values(
                        host_info,
                        host_nodes_map,
                        (x3d, front_y3d, z3d),
                    )
                    if host_kind == "tier1":
                        existing_node_id = find_existing_tier1_front_node(
                            host_key,
                            host_point,
                        )
                    else:
                        existing_node_id = find_existing_front_node_at_point(
                            host_point
                        )
                    if existing_node_id is not None:
                        node_id = existing_node_id
                    else:
                        nid = get_safe_nid(node_id_base(k))
                        node_x, node_y, node_z = node_values
                        add_node(nid, 12, 4, node_x, node_y, node_z, pt, export=True)
                        node_id = str(nid)
                    if host_kind == "tier1":
                        node_records[str(node_id)].setdefault(
                            "_tier1_host_keys", set()
                        ).add(host_key)
                else:
                    shared_node_id = shared_node_map.get(shared_key)
                    if shared_node_id is not None:
                        node_id = shared_node_id
                    else:
                        node_id = get_or_create_shared_node(shared_key, k, pt)
                    host_kind = "shared"
                endpoint_infos.append({
                    "node_id": str(node_id),
                    "host_kind": host_kind,
                    "host_key": (
                        str(host_info["host"])
                        if host_info is not None
                        else None
                    ),
                    "host_ratio": (
                        float(host_info["ratio"])
                        if host_info is not None
                        else None
                    ),
                    "z": z3d,
                    "front_xy": pt,
                })
                node_ids.append(str(node_id))

            tier3_members[k] = seg
            tier3_nodes_map[member_k] = (node_ids[0], node_ids[1])
            paired = has_explicit_mirror_pair(k)
            add_member(
                member_k,
                2 if paired else 4,
                node_ids[0],
                node_ids[1],
                variant="tier3-main",
            )
            if not front_only:
                side_nodes = _add_rotated_side_member(
                    member_k,
                    node_id_base(k),
                    node_ids[0],
                    node_ids[1],
                    "tier3-side",
                    member_symmetry_type=1 if paired else 4,
                    endpoint_infos=endpoint_infos,
                )
                if side_nodes:
                    tier3_side_nodes_map[member_k] = {
                        **side_nodes,
                        "by_source": {},
                        "endpoint_hosts": {
                            endpoint_infos[0]["node_id"]: endpoint_infos[0]["host_key"],
                            endpoint_infos[1]["node_id"]: endpoint_infos[1]["host_key"],
                        },
                    }
            del pending[k]
            resolved_count += 1

        if not resolved_count:
            for k in pending:
                print(f"[跳过] 杆件 {k} 无有效宿主")
            break

    def _connect_endpoints_on_host_members(contact_tolerance=1e-7):
        """Connect endpoint contacts and exact interior crossings topologically."""
        def member_face(connection_key):
            variant = str(member_specs[connection_key].get("variant", ""))
            return "side" if variant.endswith("-side") else "front"

        used_node_ids = {
            str(node_id)
            for node_id, record in node_records.items()
            if record.get("_member_links")
        }
        resolved_points = {
            node_id: _resolve_node_xyz(node_id)
            for node_id in used_node_ids
        }
        node_faces = {
            node_id: {
                member_face(connection_key)
                for connection_key in node_records[node_id]["_member_links"]
            }
            for node_id in used_node_ids
        }

        for connection_key in member_order:
            spec = member_specs[connection_key]
            host_face = member_face(connection_key)
            preferred = [str(node_id) for node_id in spec["preferred_nodes"]]
            if len(preferred) != 2:
                continue
            start = _resolve_node_xyz(preferred[0])
            end = _resolve_node_xyz(preferred[1])
            if start is None or end is None:
                continue

            direction = tuple(end[index] - start[index] for index in range(3))
            length_squared = sum(value * value for value in direction)
            if length_squared <= 1e-18:
                continue

            for node_id, point in resolved_points.items():
                if node_id in preferred or point is None:
                    continue
                # Front and rotated-side nodes can coincide before sheet
                # splicing but receive different Z corrections afterwards.
                # Treating such a cross-face coincidence as an interior joint
                # bends the side rod after transformation.
                if host_face not in node_faces.get(node_id, set()):
                    continue
                parameter = sum(
                    (point[index] - start[index]) * direction[index]
                    for index in range(3)
                ) / length_squared
                if parameter <= 1e-7 or parameter >= 1.0 - 1e-7:
                    continue
                projected = tuple(
                    start[index] + parameter * direction[index]
                    for index in range(3)
                )
                if math.dist(point, projected) > contact_tolerance:
                    continue
                links = node_records[node_id]["_member_links"]
                if connection_key not in links:
                    links.append(connection_key)

        def closest_points_on_segments(start1, end1, start2, end2):
            direction1 = tuple(end1[i] - start1[i] for i in range(3))
            direction2 = tuple(end2[i] - start2[i] for i in range(3))
            offset = tuple(start1[i] - start2[i] for i in range(3))

            def dot(first, second):
                return sum(first[i] * second[i] for i in range(3))

            a_value = dot(direction1, direction1)
            e_value = dot(direction2, direction2)
            if a_value <= 1e-18 or e_value <= 1e-18:
                return None
            b_value = dot(direction1, direction2)
            c_value = dot(direction1, offset)
            f_value = dot(direction2, offset)
            denominator = a_value * e_value - b_value * b_value
            if abs(denominator) <= 1e-18:
                return None
            parameter1 = (b_value * f_value - c_value * e_value) / denominator
            parameter2 = (a_value * f_value - b_value * c_value) / denominator
            if not (1e-7 < parameter1 < 1.0 - 1e-7):
                return None
            if not (1e-7 < parameter2 < 1.0 - 1e-7):
                return None
            point1 = tuple(
                start1[i] + parameter1 * direction1[i]
                for i in range(3)
            )
            point2 = tuple(
                start2[i] + parameter2 * direction2[i]
                for i in range(3)
            )
            if math.dist(point1, point2) > contact_tolerance:
                return None
            return tuple((point1[i] + point2[i]) / 2.0 for i in range(3))

        base_segments = []
        for connection_key in member_order:
            preferred = [
                str(node_id)
                for node_id in member_specs[connection_key]["preferred_nodes"]
            ]
            if len(preferred) != 2:
                continue
            start = _resolve_node_xyz(preferred[0])
            end = _resolve_node_xyz(preferred[1])
            if start is not None and end is not None:
                base_segments.append((connection_key, preferred, start, end))

        for first_index, first in enumerate(base_segments):
            first_key, first_ids, first_start, first_end = first
            for second in base_segments[first_index + 1:]:
                second_key, second_ids, second_start, second_end = second
                if member_face(first_key) != member_face(second_key):
                    continue
                if set(first_ids) & set(second_ids):
                    continue
                intersection = closest_points_on_segments(
                    first_start, first_end, second_start, second_end
                )
                if intersection is None:
                    continue

                intersection_id = _find_existing_spatial_node(
                    intersection, point_tolerance=contact_tolerance
                )
                if intersection_id is None:
                    first_member_id = member_specs[first_key]["member_id"]
                    intersection_id = str(get_safe_nid(node_id_base(first_member_id)))
                    add_node(
                        intersection_id,
                        11,
                        4,
                        intersection[0],
                        intersection[1],
                        intersection[2],
                        None,
                        export=True,
                    )
                elif intersection_id not in node_records:
                    add_node(
                        intersection_id,
                        11,
                        0,
                        intersection[0],
                        intersection[1],
                        intersection[2],
                        None,
                        export=False,
                    )

                links = node_records[str(intersection_id)]["_member_links"]
                for connection_key in (first_key, second_key):
                    if connection_key not in links:
                        links.append(connection_key)

    _connect_endpoints_on_host_members()

    if debug_member_links:
        _debug_dump_member_links(node_records)

    ganjian = _build_members_from_node_records(
        node_records,
        member_specs,
        member_order,
        resolve_node_xyz=_resolve_node_xyz,
        debug_member_trace=debug_member_trace,
    )
    jiedian = _export_node_records(node_records, include_view_face=keep_view_face)

    print(f"[完成] 单视图二/三类节点数: {len(jiedian)} | 杆件数: {len(ganjian)}")
    print("=" * 50 + "\n")

    if return_debug_nodes:
        debug_nodes = _export_debug_node_records(node_records)
        return ganjian, jiedian, debug_nodes
    return ganjian, jiedian
