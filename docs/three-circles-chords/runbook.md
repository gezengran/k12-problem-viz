# three-circles-chords — Runbook

**case_id**: `three-circles-chords`  
**主产物**: 四个选项各一条 **3:4 竖屏 Live Photo**（`.pvt`）→ `ami/three-circles-chords/`  
**平台**: Live 导出仅 **macOS**（见 [xhs-live-photo-export.md](../_common/xhs-live-photo-export.md)）

## 环境

```bash
conda activate math
export PYTHONPATH="solve/_common:solve/three-circles-chords"
```

## 测试

```bash
conda run -n math python -m pytest solve/three-circles-chords/tests -q
conda run -n math python -m ruff check solve/three-circles-chords
```

## 导出 Live Photo（macOS）

**四条一起导出**（推荐）：

```bash
./solve/three-circles-chords/run.sh
```

产物：

| 选项 | 文件 | 约束与画面 |
|------|------|------------|
| A | `option-a-live.pvt` | 固定 \(b\) 增大 \(k\) 至某圆相切（弦消失）并定格 |
| B | `option-b-live.pvt` | 仅展示 3 条 \(s_1=s_2=s_3\) 解析解 |
| C | `option-c-live.pvt` | 说明 1 方程 2 未知数 → 无穷多；快切 ≥4 条不同直线（>3） |
| D | `option-d-live.pvt` | 总和升高 → 峰值 → 再转 \(k\) 总和下降 |

所有画面含 **平面直角坐标系**（\(x,y\) 轴、网格）。

**只导出某一选项**：

```bash
conda run -n math python -m three_circles_chords --option C
```

调试帧（人工验收折线淡化等）：

```bash
export PYTHONPATH="solve/_common:solve/three-circles-chords"
conda run -n math python -c "
from three_circles_chords.export import export_debug_png_sequence
export_debug_png_sequence('C')
"
```

## 发布到小红书

每个选项单独 AirDrop 对应 `.pvt` 到 iPhone，按需选一条或多条发实况。动画为**选项场景索引**，片内不公布多选答案。
