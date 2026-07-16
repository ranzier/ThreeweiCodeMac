# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目概述

输电铁塔（担架部分）的二维工程图转三维坐标系统。输入为担架三视图（正视图、底视图、顶视图）的杆件二维坐标，输出为节点和杆件的三维信息（含对称性）。

本仓库负责**担架**的二维转三维，塔身部分由 `tower_body_reconstruction.py` 等文件处理（已完成）。

## 运行方式

```bash
python testAll.py
```

`testAll.py` 是主入口，配置输入输出路径后调用 `tran2dto3d.tran2dto3d()`。路径需根据本地环境修改（Mac/Windows 路径格式不同）。

依赖：`pandas`, `openpyxl`（用于输出 Excel）

## 核心架构（担架部分）

调用链：`testAll.py` → `tran2dto3d.py` → `xintrans.py` → `get_first_ganjian_id.py`

### tran2dto3d.py — 总调度

1. 调用塔身重建获取塔身节点/杆件及**拼接点**（`pinjie_tashen`，即担架与塔身的连接点三维坐标）
2. 调用 `xintrans.work()` 处理所有担架图纸
3. 合并担架+塔身结果，归一化节点编号（`normalize_node_ids`），输出 Excel

### xintrans.py — 单个担架的转换核心

`trans(file_path, drawing_id, data1, drawing_type)` 处理一个担架：

- **if 分支**（`drawing_id*100+1 in coordinatesBottom_data`）：处理非最上层担架（3-8号）
- **else 分支**：处理最上层担架（1-2号）

每个担架的处理流程：
1. **尖点生成**（一类节点）：`calc_jiandian_xyz()` 计算一类杆件非连接端的真实三维坐标
2. **三视图处理**：对正视图/底视图/顶视图分别找交点→计算真实X→生成二类节点和杆件
3. **三类节点/杆件**（底视图）：`find_missing_members()` + `get_jiaodian_on_ganjian_by_missing_members()` 处理剩余杆件
4. **添加一类杆件**：删除自动生成的一类杆件信息，手动添加正确的一类杆件

### get_first_ganjian_id.py — 一类杆件识别

`detect_main_rods_enhanced(coordinates_data)` 从每个视图中识别两根一类杆件：长度最长 + 编号最小的组合判断。

## 关键领域概念

- **一类杆件**：每个视图中最长的两根主杆件（编号如 101、103）
- **一类节点（尖点）**：一类杆件的非连接端节点，用真实 (x,y,z) 表示
- **二类节点**：X 用真实值，Y/Z 用引用表示法（`"1{节点编号}"`）
- **三类节点/杆件**：底视图中未被二类处理覆盖的剩余杆件
- **pj 数组**：`pj[担架ID][上下端点0/1][节点编号/坐标]`，存储担架与塔身连接点信息
- **对称性**：0=无对称，1=左右，2=前后，3=关于Z轴，4=四角对称
- **drawing_type**：图纸类型（J1/J3/J4/Z1/1E2-SDJ），影响 pj 索引排列和对称性后处理
- **yuzhi（阈值）**：150像素，用于判断点是否在杆件上

## 数据流

输入文件（`.txt`）通过 `exec()` 加载，包含三个字典变量：
- `coordinatesFront_data` — 正视图
- `coordinatesBottom_data` — 底视图
- `coordinatesOverhead_data` — 顶视图

格式：`{杆件ID: [(x1,y1), (x2,y2)]}`

输出为两个 Excel 文件（`chushi_data.xlsx` 初始数据，`zhenghe_data.xlsx` 归一化后数据），包含节点信息和杆件信息两个 sheet。

## 注意事项

- `xintrans.py` 中 `jiedian` 和 `ganjian` 是模块级全局列表，多次调用会累积数据
- 文件路径在 `xintrans.work()` 中有 Mac/Windows 注释切换
- 最上层担架（1-2号）和非最上层担架（3-8号）的视图对应关系不同（if/else 分支中一类杆件的检测顺序不同）
