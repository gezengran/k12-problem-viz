# 木板–滑块动摩擦可视化 — 任务拆分

**父级文档**：[prd.md](./prd.md)

**开发方式**：测试驱动开发（TDD），纵向 tracer bullet（一次一条测试 → 最少实现 → 通过 → 再写下一条）。禁止「先写完全部测试再写完全部实现」的横向切片。

**本题 case_id**：`plank-block-friction`  
**目录约定**：源代码与测试在 `solve/plank-block-friction/`；动画导出到 `ami/plank-block-friction/`（见 PRD）。

---

## TDD 工作约定

每条任务内按以下循环执行，完成后再进入下一条任务：

1. **红**：写一条描述**可观察行为**的测试（只走公共 API），运行并确认失败。
2. **绿**：写最少产品代码使该测试通过。
3. **重构**（可选）：在全部相关测试仍绿的前提下整理结构；禁止在仍为红时重构。

测试风格：

- 使用 `pytest`；测试放在 `solve/plank-block-friction/tests/`。
- 测行为（速度、共速时刻、摩擦方向符号、文件是否生成、画布比例），不测私有函数名或积分器内部步长。
- 地面–板摩擦质量约定（\(f_1=\mu_1 M g\) 或 \(M+m\) 等效）在**首条相关测试**中锁定，后续测试沿用同一约定。

运行命令（与项目规则一致）：

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
conda run -n math python -m pytest solve/plank-block-friction/tests -q
conda run -n math python -m ruff check solve/plank-block-friction
```

---

## 任务总览

| # | 标题 | 类型 | 阻塞于 | 用户故事 |
|---|------|------|--------|----------|
| 0 | 测试骨架与路径常量 | AFK | — | 6, 7 |
| 1 | 1D 双体仿真与共速检测 | AFK | 0 | 6 |
| 2 | 三预设注册与时长策略 | AFK | 1 | 4 |
| 3 | 9:16 上下双屏单帧渲染 | AFK | 1 | 1, 2 |
| 4 | preset-1 完整 MP4（含共速高亮） | AFK | 2, 3 | 1, 2, 3, 5 |
| 5 | preset-2 / preset-3 MP4 | AFK | 4 | 4 |
| 6 | 统一导出 CLI 与 runbook | AFK | 5 | 5, 7 |
| 7 | macOS Live Photo 可选导出 | AFK | 6 | 5 |

**已确认范围**：不包含讲解稿（原任务 8 已取消）。

**首发 tracer bullet**：任务 0 → 1（一条「有相对滑动时 \(f\) 与 \(v_{\text{rel}}\) 反向」测试 + 最少仿真实现）。

---

## 任务 0：测试骨架与路径常量

**类型**：AFK  
**阻塞于**：无，可立即开始  
**覆盖用户故事**：6, 7

### 要做什么

建立 `solve/plank-block-friction/`、`ami/plank-block-friction/`；`pytest` 可发现测试；通过公共 API 锁定 **case_id**、\(g\)、\(v_0\)、\(M/m\) 等默认常量及 `ami` 输出目录可写。

### TDD 步骤（示例顺序）

| 步骤 | 红（先写测试） | 绿（最少实现） |
|------|----------------|----------------|
| 0.1 | `pytest` 发现 `solve/plank-block-friction/tests` 并通过空套件 | `conftest.py` |
| 0.2 | `ami_dir("plank-block-friction")` 指向本题 `ami` 且可创建 | 复用 `solve/_common/paths` |
| 0.3 | 默认常量：`g=10`、`v_0=4`、`mass_ratio=15` | `constants.py` |

### 验收标准

- [ ] `conda run -n math python -m pytest solve/plank-block-friction/tests` 退出码为 0
- [ ] `solve/plank-block-friction/` 与 `ami/plank-block-friction/` 已创建
- [ ] `ruff check solve/plank-block-friction` 无错误
- [ ] 测试不依赖未实现的仿真或绘图逻辑

---

## 任务 1：1D 双体仿真与共速检测

**类型**：AFK  
**阻塞于**：0  
**覆盖用户故事**：6

### 要做什么

实现端到端仿真内核：\(t=0\) 全静止，\(t=0^+\) 木板突获 \(v_0\)；板–块动摩擦与可选板–地摩擦；输出时间序列（\(v_{\text{块}}, v_{\text{板}}, v_{\text{rel}}\)，是否处于板–块动摩擦、是否画地面摩擦）；检测**首次共速时刻** \(t_{\text{sync}}\)。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 1.1 | \(\mu_1=0,\mu_2=0.2\)：\(t>0\) 且有相对滑动时，\(f\) 方向与 \(\operatorname{sgn}(v_{\text{rel}})\) 相反 | `simulation.py` 或等价公共 API |
| 1.2 | 共速后 \(|v_{\text{rel}}|\) 保持 \(<\varepsilon\)（固定 \(\varepsilon\) 写入测试） | 分段积分 / 事件检测 |
| 1.3 | \(\mu_1=0,\mu_2=0.6\) 的 \(t_{\text{sync}}\) **小于** \(\mu_2=0.2\) 情形 | preset-2 快于 preset-1 |
| 1.4 | \(\mu_1=0.15,\mu_2=0.2\)：共速后一段时间内 \(v_{\text{板}}\) 单调减小 | preset-3 地面耗散 |
| 1.5 | \(t_{\text{sync}}\) 对 preset-1 落在合理区间（如 0.5–1.2 s 量级，容差写明） | 防回归黄金区间 |

### 验收标准

- [ ] 公共 API 为「配置 in → 轨迹 out」，不暴露积分器内部状态
- [ ] 板–地摩擦质量约定在 1.4 或首条 \(\mu_1>0\) 测试中写死
- [ ] 不实现撞墙、反弹、二维

---

## 任务 2：三预设注册与时长策略

**类型**：AFK  
**阻塞于**：1  
**覆盖用户故事**：4

### 要做什么

注册 **preset-1 / preset-2 / preset-3** 的 \((\mu_1,\mu_2)\) 与 PRD 一致的**共速后续播时长**（1 s / 1 s / 2 s）；由 `preset_id` 返回仿真配置 + 动画总时长 \(T = t_{\text{sync}} + \Delta t_{\text{tail}}\)（每预设 \(\Delta t_{\text{tail}}\) 不同，不拉齐绝对时长）。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 2.1 | `preset("preset-1")` 的 \(\mu_1=0,\mu_2=0.2\)，tail=1 s | `presets.py` |
| 2.2 | `preset("preset-2")` 的 \(\mu_2=0.6\)，tail=1 s | |
| 2.3 | `preset("preset-3")` 的 \(\mu_1=0.15,\mu_2=0.2\)，tail=2 s | |
| 2.4 | `animation_duration(preset_id)` 等于该预设仿真得到的 \(t_{\text{sync}}+\) tail（容差内） | 与任务 1 集成 |

### 验收标准

- [ ] 未知 `preset_id` 失败行为明确（异常或 Result）
- [ ] 测试只读预设表，不硬编码在 viz 里

---

## 任务 3：9:16 上下双屏单帧渲染

**类型**：AFK  
**阻塞于**：1  
**覆盖用户故事**：1, 2

### 要做什么

对给定时刻状态渲染**一帧**竖屏图：上屏「地面系」含 \(v_{\text{块}}, v_{\text{板}}\)；下屏「滑块视角」共动（滑块固定于画面参考位），含 \(v_{\text{rel}}\) 与板–块 \(f\)（同色、反向）；角标「地面系」「滑块视角」；共用图例；画布 **9:16**。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 3.1 | `render_dual_frame(state)` 不抛错 | `viz.py` |
| 3.2 | 图高/宽比在 \(16/9\) 容差内 | 复用 `_common` portrait 约定 |
| 3.3 | 有相对滑动时：下屏 \(f\) 与 \(v_{\text{rel}}\) 反向（可用箭头夹角或符号断言） | 向量层 |
| 3.4 | 输出写入 `ami/plank-block-friction/` 下测试用 PNG 且非空 | 路径冒烟 |
| 3.5 | 下屏背景/木板有相对运动视觉（条纹或位移），且不改变 3.3 方向关系 | 共动增强 |

### 验收标准

- [ ] 单帧即可演示双屏反差（不必等 MP4）
- [ ] 不画惯性力/科氏力
- [ ] 共速高亮**不在**本任务强制（留给任务 4）

---

## 任务 4：preset-1 完整 MP4（含共速高亮）

**类型**：AFK  
**阻塞于**：2, 3  
**覆盖用户故事**：1, 2, 3, 5

### 要做什么

为 **preset-1** 生成完整竖屏 MP4：从 \(t=0\) 到 \(t_{\text{sync}}+1\,\text{s}\)；在 \(t_{\text{sync}}\) 附近触发**共速高亮**（字幕或等价提示：\(v_{\text{rel}}=0\)，动摩擦消失）；共速后下屏不再画板–块 \(f\)。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 4.1 | `export_mp4("preset-1")` 在 `ami/plank-block-friction/` 生成 `preset-1.mp4`（或约定 stem） | `matplotlib.animation` + ffmpeg |
| 4.2 | 文件存在、扩展名正确、大小 > 阈值 | 冒烟 |
| 4.3 | 帧数对应时长 > 0（如 ≥ 30 帧） | 基本完整性 |
| 4.4 | 共速后区间内测试/元数据断言：板–块动摩擦标志为 false | 与高亮叙事一致 |
| 4.5 | （可选 `@pytest.mark.slow`）全片导出；CI 可只测短片段 | `conftest` marker |

### 验收标准

- [ ] 第一条可课堂播放的端到端动图（tracer bullet 闭环）
- [ ] 产物仅落在 `ami/plank-block-friction/`
- [ ] MP4 为主，不依赖 GIF

---

## 任务 5：preset-2 / preset-3 MP4

**类型**：AFK  
**阻塞于**：4  
**覆盖用户故事**：4

### 要做什么

复用任务 4 管线导出 **preset-2**（\(\mu_2=0.6\)，共速后 1 s）与 **preset-3**（\(\mu_1=0.15\)，共速后 2 s）。preset-3 在**共速后**上屏补充**地面摩擦力**箭头，板–块界面不画 \(f\)。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 5.1 | `preset-2.mp4` 生成且 \(t_{\text{sync}}\) 短于 preset-1（由仿真元数据或旁路断言） | 导出 |
| 5.2 | `preset-3.mp4` 生成且时长 ≈ \(t_{\text{sync}}+2\,\text{s}\) | 导出 |
| 5.3 | preset-3 共速后：上屏存在地面摩擦指示（测试可通过帧采样或导出回调标志） | 条件渲染 |
| 5.4 | 三条 MP4 均 9:16、双屏角标存在 | 与任务 3 一致 |

### 验收标准

- [ ] `ami/plank-block-friction/` 下三条命名 MP4 齐全
- [ ] preset-3 叙事与 PRD「共速后仅地面摩擦」一致

---

## 任务 6：统一导出 CLI 与 runbook

**类型**：AFK  
**阻塞于**：5  
**覆盖用户故事**：5, 7

### 要做什么

提供 `python -m plank_block_friction`（或等价入口）一次导出三预设 MP4；在 `docs/plank-block-friction/` 增加简短 **runbook**（环境、`PYTHONPATH`、pytest、导出命令、产物路径）。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 6.1 | `export_all_presets()` 返回三路径且文件均存在 | 聚合模块 |
| 6.2 | CLI 退出码 0，stdout 含三预设 stem 或成功标记 | `__main__.py` |
| 6.3 | 集成测试：CLI 后 `ami` 内三 MP4 非空 | 防漂移 |
| 6.4 | `runbook.md` 存在且含 conda/pytest/导出命令 | 文档 |

### 验收标准

- [ ] 一条命令可复现三预设 MP4
- [ ] 可视化不渗入仿真内核（保持模块边界）
- [ ] README 根表可链到本题 runbook（可选一行，非阻塞）

---

## 任务 7：macOS Live Photo 可选导出

**类型**：AFK  
**阻塞于**：6  
**覆盖用户故事**：5

### 要做什么

在 macOS 上提供 `run.sh`：在 MP4 已存在前提下，将指定预设（或全部）打包为 `.pvt`，写入 `ami/plank-block-friction/`；复用 `solve/_common` Live Photo 导出器；非 macOS 调用**严格失败**并给出可读错误。

### TDD 步骤

| 步骤 | 红 | 绿 |
|------|----|----|
| 7.1 | 非 Darwin 调用 Live 导出 API 抛错且消息含 macOS | 与 `_common` 先例一致 |
| 7.2 | （macOS 本地/可选 CI）`run.sh` 产出至少一个 `.pvt` | `run.sh` + 文档 |
| 7.3 | runbook 补充 AirDrop / 小红书说明，指向 `docs/_common/xhs-live-photo-export.md` | 文档 |

### 验收标准

- [ ] Live Photo **不**作为 v1 阻塞项；MP4 无 `.pvt` 仍算任务 6 完成
- [ ] 不以 GIF 作为小红书兜底
- [ ] `run.sh` 仅在本题 `solve` 目录，不写 sibling `ami`

---

## 推荐实施顺序（依赖图）

```text
0 → 1 → 2 ─┐
      └→ 3 ─┼→ 4 → 5 → 6 → 7
```

---

## 与 PRD 的追溯

| PRD 交付项 | 任务 |
|------------|------|
| 1D 仿真、摩擦方向、共速 | 1 |
| 三预设 \(\mu\) 与续播 1s/1s/2s | 2, 5 |
| 9:16 上惯性 / 下共动、标注 B | 3, 4, 5 |
| 共速高亮 | 4 |
| preset-3 共速后地面摩擦 | 5 |
| 三条 MP4 | 4, 5, 6 |
| Live Photo 可选 | 7 |
| `ami/plank-block-friction/` 唯一导出 | 0, 4–7 |

---

## 发布为 GitHub Issue（可选）

批准本任务表后，可按上表每条创建 Issue，正文使用 [拆分任务 skill](../.cursor/skills/拆分任务/templates/issue-slice-template.md) 模板：

- **父级**：链接 `docs/plank-block-friction/prd.md` 或仓库 Tracking Issue
- **阻塞于**：填依赖任务对应 Issue 号
- 若仓库有 `ready-for-agent` 类标签，**AFK** 任务可加上

建议创建顺序：**0 → 1 → 2 → 3 → 4 → 5 → 6 → 7**，以便「阻塞于」引用真实编号。

---

## 后续可选（不在当前切片内）

- 初中物理讲解稿（`solution-junior.md`，已明确不做）
- 共速关键帧 PNG 讲义插图
- 第四预设、交互扫参、GIF 副产品
- `pytest.ini` / 根 `README` Cases 表增加 `plank-block-friction` 一行
- CI 将 `solve/plank-block-friction` 纳入默认 `pytest` 路径
