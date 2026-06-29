#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 T7833 目录下的坐标数据到 tashen 和 danjia 两个目录。

规则:
1. 以数字(0x)为前缀分组。
2. 如果某个前缀下只有一个文件(如 03_front、04_front),直接复制该文件到 tashen 目录(保留原文件名)。
3. 否则按前缀合并:
   - danjia 组: 文件名含 "danjia" 或 "top" 的文件,内容合并到 danjia/0x.txt,
     并对变量名做重命名(danjia_coordinatesBottom_data -> coordinatesBottom_data,
     danjia_coordinatesFront_data -> coordinatesFront_data,
     coordinatesTop_data -> coordinatesOverhead_data)
   - tashen 组: 文件名含 "tashen" 或 "side" 的文件,内容合并到 tashen/0x.txt,
     先删除 tashen_coordinatesBottom_data 整个数据块,再对变量名做重命名
     (tashen_coordinatesFront_data -> coordinatesFront_data,
     coordinatesSide_data -> coordinatesOverhead_data)
4. 剔除不属于塔身的杆件: 断裂的担架残段会从塔身两侧伸出,其端点在 x 方向上
   明显离群(与塔身主体之间存在远大于常规间距的空隙)。检测这类边缘离群端点,
   并删除任何触及它们的杆件。
"""

import os
import re
import shutil
import statistics
from collections import defaultdict

# 源目录(脚本所在目录下的 T7833)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "T7833")
TASHEN_DIR = os.path.join(BASE_DIR, "tashen")
DANJIA_DIR = os.path.join(BASE_DIR, "danjia")

# 匹配数字前缀,如 01_xxx.txt -> 01
PREFIX_RE = re.compile(r"^(\d+)_")

# danjia 文件内变量名的重命名规则
DANJIA_RENAMES = [
    ("danjia_coordinatesBottom_data", "coordinatesBottom_data"),
    ("danjia_coordinatesFront_data", "coordinatesFront_data"),
    ("coordinatesTop_data", "coordinatesOverhead_data"),
]

# tashen 文件内要删除的整个数据块的变量名
TASHEN_DROPS = ["tashen_coordinatesBottom_data"]

# tashen 文件内变量名的重命名规则
TASHEN_RENAMES = [
    ("tashen_coordinatesFront_data", "coordinatesFront_data"),
    ("coordinatesSide_data", "coordinatesOverhead_data"),
]

# 边缘离群检测参数:间隙超过 max(EDGE_MIN_GAP, EDGE_GAP_FACTOR*常规间距) 视为离群
EDGE_GAP_FACTOR = 3.0
EDGE_MIN_GAP = 100

# 单根杆件:  key:[(x1,y1),(x2,y2)]
ROD_RE = re.compile(
    r"\[\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*,\s*\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*\]"
)
# 数据块:  varname={ ... }
BLOCK_RE = re.compile(r"\w+\s*=\s*\{.*?\n\}", re.DOTALL)


def find_edge_outlier_values(values):
    """找出位于最小/最大边缘、且与主体之间存在异常大间隙的离群坐标值。

    塔身主体的端点在某一坐标轴上分布相对均匀;断裂担架残段会从塔身一侧伸出,
    其端点与主体之间隔着远大于常规杆距的空隙。从两侧边缘向内扩展标记这类离群值。
    """
    uniq = sorted(set(values))
    if len(uniq) < 3:
        return set()
    gaps = [b - a for a, b in zip(uniq, uniq[1:])]
    threshold = max(EDGE_MIN_GAP, EDGE_GAP_FACTOR * statistics.median(gaps))
    outliers = set()
    # 从左边缘向内扩展
    i = 0
    while i < len(uniq) - 1 and (uniq[i + 1] - uniq[i]) > threshold:
        outliers.add(uniq[i])
        i += 1
    # 从右边缘向内扩展
    j = len(uniq) - 1
    while j > 0 and (uniq[j] - uniq[j - 1]) > threshold:
        outliers.add(uniq[j])
        j -= 1
    return outliers


def drop_edge_outlier_rods(content):
    """删除触及 x 方向边缘离群端点的杆件(断裂担架残段),逐数据块独立判断。"""

    def process_block(m):
        block = m.group(0)
        lines = block.split("\n")
        # 收集本块所有杆件端点的 x 值
        xs = []
        parsed = []  # (line, (x1, x2) 或 None)
        for ln in lines:
            rm = ROD_RE.search(ln)
            if rm:
                x1, x2 = int(rm.group(1)), int(rm.group(3))
                xs += [x1, x2]
                parsed.append((ln, (x1, x2)))
            else:
                parsed.append((ln, None))
        outliers = find_edge_outlier_values(xs)
        if not outliers:
            return block
        kept = []
        for ln, ex in parsed:
            if ex and (ex[0] in outliers or ex[1] in outliers):
                print(f"    [剔除担架残段] {ln.strip()}")
                continue
            kept.append(ln)
        return "\n".join(kept)

    return BLOCK_RE.sub(process_block, content)


def drop_data_blocks(content, var_names):
    """删除形如 `var_name={ ... }` 的整个数据块"""
    for var in var_names:
        # 匹配 var={ 一直到对应的换行后第一个单独的 } 行
        pattern = re.compile(
            r"^" + re.escape(var) + r"\s*=\s*\{.*?^\}\s*$\n?",
            re.DOTALL | re.MULTILINE,
        )
        content = pattern.sub("", content)
    return content


def group_by_prefix(files):
    """按数字前缀分组"""
    groups = defaultdict(list)
    for name in files:
        m = PREFIX_RE.match(name)
        if m:
            groups[m.group(1)].append(name)
    return groups


def read_content(path):
    """读取文件内容"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def merge_files(file_names, out_path, renames=None, drops=None, drop_outliers=False):
    """把多个文件内容合并写入 out_path,可选删除数据块、做变量名替换、剔除离群杆件"""
    parts = []
    for name in sorted(file_names):
        content = read_content(os.path.join(SRC_DIR, name))
        if drops:
            content = drop_data_blocks(content, drops)
        if renames:
            for old, rep in renames:
                content = content.replace(old, rep)
        if drop_outliers:
            content = drop_edge_outlier_rods(content)
        content = content.strip()
        if not content:
            continue
        parts.append(content + "\n")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main():
    if not os.path.isdir(SRC_DIR):
        raise SystemExit(f"源目录不存在: {SRC_DIR}")

    os.makedirs(TASHEN_DIR, exist_ok=True)
    os.makedirs(DANJIA_DIR, exist_ok=True)

    files = [f for f in os.listdir(SRC_DIR)
             if os.path.isfile(os.path.join(SRC_DIR, f)) and f.endswith(".txt")]
    groups = group_by_prefix(files)

    for prefix, names in sorted(groups.items()):
        # 该前缀下只有一个文件 -> 直接复制到 tashen
        if len(names) == 1:
            src = os.path.join(SRC_DIR, names[0])
            dst = os.path.join(TASHEN_DIR, names[0])
            shutil.copy2(src, dst)
            print(f"[复制] {names[0]} -> tashen/{names[0]}")
            continue

        # 多文件 -> 分别归入 danjia / tashen 组并合并
        danjia_files = [n for n in names if "danjia" in n or "top" in n]
        tashen_files = [n for n in names if "tashen" in n or "side" in n]

        if danjia_files:
            out = os.path.join(DANJIA_DIR, f"{prefix}.txt")
            merge_files(danjia_files, out, renames=DANJIA_RENAMES)
            print(f"[合并] danjia/{prefix}.txt <- {sorted(danjia_files)}")

        if tashen_files:
            out = os.path.join(TASHEN_DIR, f"{prefix}.txt")
            merge_files(tashen_files, out, renames=TASHEN_RENAMES, drops=TASHEN_DROPS,
                        drop_outliers=True)
            print(f"[合并] tashen/{prefix}.txt <- {sorted(tashen_files)}")

    print("整理完成。")


if __name__ == "__main__":
    main()
