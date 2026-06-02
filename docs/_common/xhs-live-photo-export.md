# 小红书 Live Photo（.pvt）通用导出 — PRD

## 问题陈述

项目中的数学可视化需要发布到**小红书**等平台。小红书支持 **Live 实况**（与 iOS Live Photo 同类体验），但**不支持 GIF** 作为动图发布载体。当前 `umbrella-rain` 在 `viz` 内嵌了 JPEG + MOV → `.pvt` 的导出逻辑，且与 GIF 兜底混在同一套 `export_animation_bundle` 中；其他题目无法复用，也不符合「以制作过程为核心、多场景适配」的目标。

创作者需要一条可重复的生产链路：**在 macOS 上从 Python 渲染帧序列 → 严格产出可在小红书使用的 `.pvt` →（调试期可保留中间件）→ AirDrop 或导入相册后发布**。同时需要一道**与具体业务题解耦**的示范动画（`y = x²` 与 `y = 1.01^x` 日积月累对比），用于团队复制流程，而非绑定雨伞几何题。

## 解决方案

在 `solve/_common/` 提供**深模块**「Live Photo 导出器」：对外是简单、稳定的接口（帧列表或 matplotlib 帧生成器 → `.pvt` 路径）；对内封装 letterbox、MOV 编码、`makelive` 打包、平台前置检查与**严格失败**语义。

各 `case_id` 只负责**内容与叙事**（如何画每一帧）；导出规范（尺寸、帧率、失败策略、产物目录）由公共模块统一约束。v1 包含：

1. 通用导出模块落地，并将 `umbrella-rain` 迁为调用方（小红书链路**不再**依赖 GIF）。
2. 新增示范 case（建议 `case_id`: `compound-growth`）：同一坐标系内两条曲线随时间生长，**快—慢—快**节奏，视觉突出两曲线**交点**，导出 Live Photo 至 `ami/compound-growth/`。
3. 环境配置补齐 `makelive`（`pip:`）及已有硬依赖（如 `ffmpeg`），文档说明**仅 macOS** 可执行 Live 导出。

调试阶段默认**保留** `.jpg` / `.mov` 便于排查；稳定后通过配置**仅保留** `.pvt`（删除或不再写入中间文件）。

## 用户故事

1. 作为内容创作者，我希望一键从动画帧得到 `.pvt`，以便在小红书发布 Live 实况而无需 GIF。
2. 作为开发者，我希望导出失败时立即报错并说明缺什么（非 macOS、无 `ffmpeg`、无 `makelive` 等），以便不会误以为「已成功」却无法发布。
3. 作为多题仓库维护者，我希望 Live 导出逻辑集中在 `_common`，以便新题只写渲染、不写打包细节。
4. 作为 matplotlib 用户，我希望用「帧回调 + 帧数」即可导出，以便与现有 `umbrella-rain` 动画写法一致。
5. 作为非 matplotlib 场景作者，我希望直接传入 `PIL.Image` 帧列表也能导出，以便未来接入其他渲染源。
6. 作为调试者，我希望在需要时保留 `.jpg` 与 `.mov` 中间产物，以便检查静帧与视频是否正常，再单独打包 `.pvt`。
7. 作为运营稳定期的维护者，我希望关闭中间产物、只落盘 `.pvt`，以便 `ami/` 目录干净。
8. 作为示范读者，我希望看到 `y = x²` 与 `y = 1.01^x` 在同一坐标系中随时间生长并突出交点，以便理解「日积月累」类指数增长何时反超多项式直觉。
9. 作为 `umbrella-rain` 使用者，我希望雨伞动画仍走同一套 Live 导出，以便行为与示范 case 一致、减少分叉。
10. 作为 CI/协作者，我希望在非 macOS 或无私有依赖时测试仍可运行（测 letterbox、参数校验、严格失败消息等），而完整 `.pvt` 集成测仅在 macOS 执行。

## 实现决策

### 平台与产物契约

- **主交付物**：`.pvt`（Live Photo 包，含 still + video + metadata），面向小红书 Live / iOS 相册链路。
- **不支持**：在本导出器的「小红书模式」下，**不**生成 GIF，**不**以 GIF 作为失败兜底（与平台能力对齐）。
- **严格失败**：任一前置条件不满足（非 Darwin、缺少 `ffmpeg`、缺少 `makelive`、MOV 编码失败、打包失败）则**抛错终止**，返回明确错误信息。
- **运行环境**：Live 导出**仅支持 macOS**；Linux/Windows 可用于开发与单测，但调用 Live 导出 API 应失败并说明原因。

### 深模块：Live Photo 导出器（`solve/_common`）

**设计原则**：浅接口、厚实现——调用方只关心「帧 + 输出 stem + 可选参数」，不接触 `makelive` / `ffmpeg` 命令行细节。

**两层 API（接口 C）**：

| 层级 | 输入 | 职责 |
|------|------|------|
| 底层 | `list[PIL.Image]`（RGB） | letterbox → 写 JPEG（首帧）→ 写 MOV → `save_live_photo_pair_as_pvt` → 返回 `.pvt` 路径 |
| 上层适配 | `frames_builder(i) -> Figure` 或等价 matplotlib 流程、`n_frames`、`figsize/dpi` | 复用单 Figure 逐帧渲染、转 RGB 帧列表，再调用底层 |

**默认参数（可覆盖，决策 B）**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 目标画布 | 720×960（3:4） | 与现有竖屏 9:16 图 letterbox 白边策略一致 |
| letterbox | 白底、等比缩放居中 | 保持小红书竖屏观感 |
| `fps` | 10 | 与现有雨伞动画一致；慢叙事可提高 `n_frames` 或略调 `fps` |
| JPEG 质量 | 高（如 95） | 首帧 still |
| MOV | H.264、`yuv420p`、`+faststart` | 经 `ffmpeg` 由帧序列合成 |

**中间产物策略（两阶段）**：

| 阶段 | 行为 |
|------|------|
| v1 / 调试 | 写入 `.jpg`、`.mov` 及 `.pvt`；便于对比静帧与视频 |
| 稳定后 | 配置项（如 `keep_intermediates=False`）下**仅保留** `.pvt`；可选在成功后删除已生成的中间文件 |

**返回值**：结构化结果（至少包含 `pvt` 路径；调试期可包含 `jpg`、`mov` 路径），便于测试断言与日志。

**与路径助手协作**：各 case 通过既有 `ami_dir(case_id)` 限定输出目录，禁止写入其他 case 的 `ami/`。

### 示范 case：`compound-growth`（日积月累）

- **数学意图**：对比 `y = x²`（短期增长感强）与 `y = 1.01^x`（日积月累），**非**仓库核心业务题，而是**流程样板**。
- **画面**：**同一坐标系**；两曲线随参数 `t`（或等价进度 `u ∈ [0,1]`）从起点向右侧「生长」显示（已画部分保留，未画部分不显示），而非整图淡入。
- **时间节奏**：进度映射采用 **快—慢—快**（ease-in-out 或分段 easing），在接近**两曲线交点**附近放慢，停留或强化标注（交点坐标/辅助线/高亮圆点），突出「反超」时刻。
- **交点**：实现阶段数值求解 `x² = 1.01^x` 的正根（及若需展示的第二交点），动画时间轴在交点附近分配更多帧权重。
- **画布**：竖屏 9:16 绘图，经公共 letterbox 到 3:4 导出；轴域、标题、简短中文说明服务于社交传播，避免代码变量名入图。
- **导出**：调用公共 Live 导出器，产物仅落在 `ami/compound-growth/`；提供与仓库一致的 `run` 入口（脚本或模块 `main`）。

### 迁移：`umbrella-rain`

- 将 letterbox、MOV 合成、`.pvt` 打包从 `viz` **迁出**至 `_common`；`viz` 保留雨伞几何渲染与 `frames_builder` 定义。
- `export_animation_bundle`（或等价批量导出）在小红书路径上：**只**走 Live 导出；**移除**对该路径的 GIF 生成（现有测试若断言 GIF，改为断言 `.pvt` 或拆分「非 Live 测试」）。
- 行为保持：竖屏几何动画、`fps=10`、帧数与场景叙事不变；严格失败替代原先的 `return None` 静默跳过。

### 依赖与环境

- **`environment.yml`**：在 `pip:` 段加入 **`makelive`**；已有 **`ffmpeg`**（conda）继续作为 MOV 硬依赖。
- **文档**：README 或 case 说明中写明 Live 导出 = macOS + `conda env` + AirDrop `.pvt` 包（非散装 JPG/MOV）的小红书发布提示。
- **PYTHONPATH**：沿用 `solve/_common` 在路径中，新模块无需每题复制。

### 模块划分（新建 / 修改）

| 模块 | 类型 | 说明 |
|------|------|------|
| `_common` Live Photo 导出 | 新建 | 深模块：底层 PIL + 上层 matplotlib 适配 |
| `_common` paths | 已有 | `ami_dir` 等不变 |
| `umbrella-rain` viz / 导出 | 修改 | 调用公共导出；删 GIF 小红书路径 |
| `compound-growth` 求解包 | 新建 | 示范渲染 + `run` 入口 + 测试 |
| `environment.yml` | 修改 | `pip: makelive` |
| 根 README Cases 表 | 修改 | 增加 `compound-growth` 一行（实现阶段） |

### 不在 PRD 内规定的细节

- 具体函数名、文件名、类名（实现时与 `ruff` / 现有风格对齐即可）。
- 小红书客户端 UI 操作步骤（仅约定产物格式与 AirDrop 包形态）。

## 测试决策

### 何谓好测试

- 测**对外行为**：letterbox 输出尺寸、严格失败时的异常类型与消息、matplotlib 适配器生成的帧数、导出结果字典含 `.pvt`。
- **不测**：`makelive` 内部实现、`ffmpeg` 命令行每一 flag（除非回归需要）。
- 完整 `.pvt` 端到端：标记 `slow`，**仅在 `Darwin`** 运行；与 `umbrella-rain` 现有 `test_export_all_media_to_ami` 先例一致。

### 建议覆盖

| 模块 | 测试要点 |
|------|----------|
| `_common` Live 导出 | letterbox 默认尺寸；非 Darwin 调用抛错；无 `ffmpeg` 时抛错；`keep_intermediates` 真/假时产物集合；帧数为 0 或空列表非法输入 |
| `_common`（可选 mock） | 在无法调用 `makelive` 的环境，mock 打包函数验证调用顺序（jpg/mov 路径传入） |
| `compound-growth` | 帧序列长度与 easing 单调性；交点时刻附近帧索引落在预期区间（容差）；Darwin 下 `run` 产出 `.pvt` |
| `umbrella-rain` | 迁移后几何单测不变；媒体导出测改为以 `.pvt` 为主；移除对 `scene_*_gif` 的硬性要求（若 GIF 路径删除） |

### 先例

- `umbrella-rain`：`test_letterbox_image_matches_live_photo_size`、`test_export_all_media_to_ami`（Darwin 断言 `.pvt` 为目录包）。

## 不在范围内

- Windows/Linux 上生成可被小红书识别的 `.pvt`（平台限制，不实现）。
- 自动上传到小红书 API（无官方开放发布 API 假设）。
- GIF / WebP / MP4 作为小红书动图的替代方案（明确排除 GIF 主路径）。
- Manim、Web 前端渲染器适配（v1 仅 PIL 底层 + matplotlib 上层；后续可再加适配器）。
- `compound-growth` 的符号推导教案正文（可有简短图内文字，不做完整 `docs/<case_id>/solution-junior.md`）。
- 交互动画播放器、在线预览站。

## 其他说明

### 已对齐的设计决策摘要

| 项 | 决策 |
|----|------|
| 主格式 | `.pvt`（小红书 Live） |
| 失败策略 | 严格失败 |
| 代码组织 | `_common` 通用工具 |
| API | 底层 PIL 帧 + 上层 matplotlib 适配 |
| 帧参数 | 默认 720×960、`fps=10`，可覆盖 |
| v1 范围 | 通用模块 + 迁移 `umbrella-rain` + `compound-growth` 示范 |
| 示范动效 | 同坐标系双曲线随 t 生长；快—慢—快；突出交点 |
| 中间文件 | 调试保留 jpg/mov；稳定后仅 pvt |
| 依赖 | `makelive` 进 `environment.yml` 的 `pip:` |

### 文档与目录

- 本 PRD：`docs/_common/xhs-live-photo-export.md`
- 建议后续：`docs/compound-growth/runbook.md`（发布 checklist：conda → run → AirDrop → 小红书）可在实现后补，非 v1 阻塞。

### 发布流程（用户视角）

1. macOS 上激活 `math` 环境，安装/更新 `environment.yml`。
2. 在目标 case 目录执行 `run`（或等价命令），得到 `ami/<case_id>/` 下 `.pvt`。
3. 将 **`.pvt` 包** AirDrop 至 iPhone（勿只传散装 JPG/MOV）。
4. 相册确认 Live 可播放后，在小红书选择实况图发布。

---

**状态**：已定稿。任务拆分见 [xhs-live-photo-export-tasks.md](./xhs-live-photo-export-tasks.md)；可从任务 1 开始实现。
