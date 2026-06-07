# 木板–滑块动摩擦可视化 — 任务拆分

**父级文档**：[prd.md](./prd.md)

**开发方式**：测试驱动开发（TDD），纵向 tracer bullet（一次一条测试 → 最少实现 → 通过 → 再写下一条）。

**本题 case_id**：`plank-block-friction`  
**目录约定**：源代码与测试在 `solve/plank-block-friction/`；动画导出到 `ami/plank-block-friction/`（见 PRD）。

---

## v2 迭代摘要（2026-06 已落地）

相对 v1 任务表，实现阶段完成以下**设计转向**（详见 PRD「迭代记录」）：

| 变更项 | 原任务描述 | 当前实现 |
|--------|------------|----------|
| 画幅与布局 | 9:16 上下双屏 `render_dual_frame` | **4:3 满幅**单视角：`render_ground_frame` / `render_block_frame` / `render_plank_frame` |
| 导出形态 | 每预设一条双屏 `preset-N.mp4` | **preset-1** 三条：`preset-1-{ground,block,plank}.mp4` |
| 共动视野 | 下屏窄窗放大 | 与地面系同为 **8 m** 跨度 |
| 滑块初位 | 偏左叙事 | **板中**（`BLOCK_INITIAL_OFFSET_FRAC=0.50`） |
| \(\mu_2\) | preset-1: 0.2 | preset-1: **1.0**；preset-2: **1.5** |
| 第三视角 | 未规划 | **木板视角** `VIEW_PLANK=plank` |
| 接触模型 | 可离板 | **板端 clamp** 教学模型（不离板） |
| 共速高亮 | 下屏 | **三视角字幕**；block / plank 另加接触高亮 |

**当前 tracer bullet 闭环**：任务 0–4 + v2 扩展（plank 视角、三文件导出）已在代码与 `ami/` 产物中验证。

---

## TDD 工作约定

每条任务内按以下循环执行，完成后再进入下一条任务：

1. **红**：写一条描述**可观察行为**的测试（只走公共 API），运行并确认失败。
2. **绿**：写最少产品代码使该测试通过。
3. **重构**（可选）：在全部相关测试仍绿的前提下整理结构。

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
conda run -n math python -m pytest solve/plank-block-friction/tests -q
conda run -n math python -m ruff check solve/plank-block-friction
```

---

## 任务总览

| # | 标题 | 类型 | 状态 | 阻塞于 | 用户故事 |
|---|------|------|------|--------|----------|
| 0 | 测试骨架与路径常量 | AFK | **完成** | — | 6, 7 |
| 1 | 1D 双体仿真与共速检测 | AFK | **完成** | 0 | 6 |
| 2 | 三预设注册与时长策略 | AFK | **完成**（\(\mu_2\) 已按 v2 更新） | 1 | 4 |
| 3 | 单视角帧渲染（ground / block / plank） | AFK | **完成** | 1 | 1, 2 |
| 4 | preset-1 三视角 MP4（含共速高亮） | AFK | **完成** | 2, 3 | 1, 2, 3, 5 |
| 5 | preset-2 / preset-3 全视角 MP4 | AFK | **待做** | 4 | 4 |
| 6 | 统一导出 CLI 与 runbook | AFK | **部分完成** | 5 | 5, 7 |
| 7 | macOS Live Photo 可选导出 | AFK | **完成**（preset-1 三视角） | 6 | 5 |

**已确认范围**：不包含讲解稿（`solution-junior.md`）。

---

## 任务 0：测试骨架与路径常量

**状态**：**完成**

### 验收标准

- [x] `pytest solve/plank-block-friction/tests` 通过
- [x] `constants.py`：`g=10`、`v_0=4`、`mass_ratio=15`、`CASE_ID`
- [x] `ami_dir("plank-block-friction")` 可写
- [x] v2 增补：`VIEW_GROUND/BLOCK/PLANK`、`FIG_WIDTH/HEIGHT`（4:3）、`LAB_VIEW_X_SPAN=8`

---

## 任务 1：1D 双体仿真与共速检测

**状态**：**完成**

### 要做什么

\(t=0\) 全静止，\(t=0^+\) 木板突获 \(v_0\)；板–块 / 板–地动摩擦；输出时间序列与 \(t_{\text{sync}}\)；**板端 clamp** 保持滑块在木板段内。

### 验收标准

- [x] 有相对滑动时 \(f\) 与 \(\operatorname{sgn}(v_{\text{rel}})\) 相反
- [x] 共速后 \(|v_{\text{rel}}|\) 保持 \(<\varepsilon\)
- [x] preset-2 共速早于 preset-1（\(\mu_2=1.5\) vs \(1.0\)）
- [x] preset-3 共速后 \(v_{\text{板}}\) 单调减小
- [x] v2：preset-1 共速时块–板偏移不在左端（`test_preset1_block_not_at_left_edge_at_sync`）

### TDD 步骤（已实现）

| 步骤 | 测试要点 | 模块 |
|------|----------|------|
| 1.1 | 摩擦方向与 \(v_{\text{rel}}\) 反向 | `simulation.py` |
| 1.2 | 共速后 \(v_{\text{rel}}\) 近零 | 事件检测 |
| 1.3 | 高 \(\mu_2\) 更早共速 | presets 集成 |
| 1.4 | preset-3 地面耗散 | |
| 1.5 | preset-1 \(t_{\text{sync}}\approx 0.38\,\text{s}\)（\(\mu_2=1.0\)） | 更新黄金区间 |

---

## 任务 2：三预设注册与时长策略

**状态**：**完成**（参数已按 v2 PRD 更新）

### 当前预设表（与代码 `presets.py` 一致）

| preset_id | \(\mu_1\) | \(\mu_2\) | tail |
|-----------|----------|----------|------|
| preset-1 | 0 | **1.0** | 1 s |
| preset-2 | 0 | **1.5** | 1 s |
| preset-3 | 0.15 | 0.2 | 2 s |

### 验收标准

- [x] `get_preset` / `sim_config_for_preset` / `animation_duration`
- [x] `animation_duration` = \(t_{\text{sync}}+\) tail（容差内）
- [x] 未知 `preset_id` 抛 `KeyError`

---

## 任务 3：单视角帧渲染（ground / block / plank）

**状态**：**完成**（由原「9:16 双屏」任务改写）

### 要做什么

对给定时刻状态渲染**一帧** 4:3 满幅图：

| 函数 | 参考系 | 标注 |
|------|--------|------|
| `render_ground_frame` | 固定 \([0,8]\,\text{m}\) | \(v_{\text{块}}, v_{\text{板}}\) |
| `render_block_frame` | 滑块共动，块居中 | \(v_{\text{rel}}, f\)（在滑块上） |
| `render_plank_frame` | 木板共动，板居中 | \(v_{\text{rel}}, f\)（在木板上） |

角标「地面系」「滑块视角」「木板视角」；共动系地面条纹滚动；`export_frame_png(sample, view, path)`。

### 验收标准

- [x] 三 `render_*_frame` 冒烟不抛错
- [x] 画幅比例 4:3（`figure_aspect_ratio ≈ 3/4`）
- [x] 等比例米制：\( \Delta x / \Delta y = 4/3 \) 数据跨度
- [x] ground 与共动系水平跨度均为 8 m
- [x] block 视角不标 \(v_{\text{块}}, v_{\text{板}}\)（仅 \(v_{\text{rel}}, f\)）
- [x] block 视角：滑块固定在 `BLOCK_ANCHOR_X`；plank 视角：板左缘固定在 `PLANK_ANCHOR_X - L/2`
- [x] `render_dual_frame` 保留作遗留调试，非发布路径

### TDD 步骤（已实现）

| 步骤 | 测试文件 | 要点 |
|------|----------|------|
| 3.1 | `test_plank_viz.py` | 三视角渲染 |
| 3.2 | `test_plank_viz.py` | 4:3 比例 |
| 3.3 | `test_plank_viz.py` | \(f \perp v_{\text{rel}}\) |
| 3.4 | `test_plank_viz.py` | PNG 导出冒烟 |
| 3.5 | `test_plank_viz.py` | 共动系滚动 vs 固定地纹 |
| 3.6 | `test_plank_viz.py` | `test_plank_panel_pins_plank_and_scrolls_ground` |

---

## 任务 4：preset-1 三视角 MP4（含共速高亮）

**状态**：**完成**

### 要做什么

为 **preset-1** 导出三条 MP4，物理时长 \(t_{\text{sync}}+1\,\text{s}\)，播放拉伸约 5 s：

- `preset-1-ground.mp4`
- `preset-1-block.mp4`（共速高亮）
- `preset-1-plank.mp4`（共速高亮）

API：`export_view_mp4(preset_id, view)`、`export_classic_preset1()`。

### 验收标准

- [x] 三条 MP4 写入 `ami/plank-block-friction/`
- [x] 960×720（4:3）
- [x] 短 MP4 冒烟（`test_export_view_mp4_smoke`）
- [x] 慢测 `test_export_classic_preset1_full`（`@pytest.mark.slow`）
- [x] CLI：`python -m plank_block_friction` 打印三路径

### TDD 步骤（已实现）

| 步骤 | 要点 |
|------|------|
| 4.1 | `export_view_mp4` + ffmpeg |
| 4.2 | 文件非空 |
| 4.3 | `export_classic_preset1` 返回三键 |
| 4.4 | block/plank 在 \(t_{\text{sync}}\) 后 1 s 内高亮 |

---

## 任务 5：preset-2 / preset-3 全视角 MP4

**状态**：**待做**

**阻塞于**：4

### 要做什么

复用任务 4 管线，为 **preset-2**、**preset-3** 各导出 `ground` / `block` / `plank` 三条 MP4（共 6 条）。preset-3 在**共速后** ground 视角补充 \(f_{\text{地}}\)。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 5.1 | `export_all_presets()` 或扩展 CLI 导出 9 条（3 预设 × 3 视角） | 聚合导出 |
| 5.2 | preset-2 的 \(t_{\text{sync}} <\) preset-1（元数据断言） | |
| 5.3 | preset-3 共速后 ground 帧含地面摩擦指示 | 条件渲染 |
| 5.4 | 九条 MP4 均为 4:3 | 与任务 3 一致 |

### 验收标准

- [ ] `ami/plank-block-friction/` 下 preset-2/3 各三视角 MP4 齐全
- [ ] preset-3 叙事与 PRD「共速后仅地面摩擦」一致

---

## 任务 6：统一导出 CLI 与 runbook

**状态**：**部分完成**

### 已完成

- [x] `python -m plank_block_friction` 导出 preset-1 三视角
- [x] `./solve/plank-block-friction/run.sh`
- [x] `runbook.md` 存在（**待同步 v2 产物说明**）

### 待完成

- [ ] 更新 `runbook.md`：4:3、三视角命名、\(\mu_2=1.0\)、无离板结束
- [ ] 任务 5 完成后：`export_all_presets()` 覆盖三预设 × 三视角
- [ ] （可选）根 `README` Cases 表增加本题一行

---

## 任务 7：macOS Live Photo 可选导出

**状态**：**完成**（preset-1 三视角）

### 要做什么

macOS 上 `run.sh` / `python -m plank_block_friction` 在 MP4 后导出 Live Photo；非 macOS 仅 MP4。

### 验收标准

- [x] 非 Darwin 调用 `export_view_live` 失败且消息可读（`test_live_export_requires_macos`）
- [x] macOS slow 测三视角 `.pvt` 冒烟
- [x] `export_view_live` / `export_classic_preset1_live` 接入 `_common/live_photo_export`
- [x] 产物：`preset-1-{ground,block,plank}_live.pvt`（默认不保留散装 `.jpg`/`.mov`）
- [x] `runbook.md` 已更新发布说明

---

## 推荐实施顺序（依赖图）

```text
0 → 1 → 2 ─┐
      └→ 3 ─┼→ 4 [完成] → 5 → 6（收尾文档）→ 7
```

---

## 与 PRD 的追溯（v2）

| PRD 交付项 | 任务 | 状态 |
|------------|------|------|
| 1D 仿真、摩擦方向、共速、板端 clamp | 1 | 完成 |
| 三预设 \(\mu\) 与续播 | 2 | 完成 |
| 4:3 满幅单视角 ground/block/plank | 3 | 完成 |
| preset-1 三视角 MP4 + 共速高亮 | 4 | 完成 |
| preset-2/3 全视角 MP4 | 5 | 待做 |
| CLI + runbook | 6 | 部分 |
| Live Photo 可选（preset-1 三视角） | 7 | 完成 |
| `ami/plank-block-friction/` 唯一导出 | 0, 4–7 | 完成（preset-1） |

---

## v2 决策追溯（对话 → 代码）

| 决策 | 代码 / 产物落点 |
|------|----------------|
| 取消双屏拼图 | `viz.py` 单视角 `render_*_frame`；`export_classic_preset1` |
| 4:3 满幅 | `constants.py` `FIG_WIDTH/HEIGHT`；`viz._configure_full_bleed` |
| 共动系不放大 | `BLOCK_VIEW_X_SPAN = LAB_VIEW_X_SPAN = 8` |
| 滑块初位板中 | `BLOCK_INITIAL_OFFSET_FRAC = 0.50` |
| 提高 \(\mu_2\) 避免共速在板左缘 | `presets.py` preset-1 \(\mu_2=1.0\) |
| 木板视角 | `VIEW_PLANK`、`render_plank_frame`、`preset-1-plank.mp4` |
| 木板 2.5 m 示意 | `PLANK_LENGTH = 2.5` |
| 播放拉伸 5 s | `PLAYBACK_SECONDS=5`, `EXPORT_FPS=10` |

---

## 发布为 GitHub Issue（可选）

批准后可按任务表创建 Issue；当前 **任务 5–7** 为剩余可领取切片。

---

## 后续可选（不在当前阻塞路径）

- 共速关键帧 PNG（三视角各一帧）
- 初中生讲解稿
- 交互扫参、GIF 副产品
- CI 默认纳入 `solve/plank-block-friction`
- 更新 `runbook.md` 与 PRD 保持同步（任务 6 收尾）
