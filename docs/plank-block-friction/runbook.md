# plank-block-friction — 运行说明

木板–滑块动摩擦方向可视化：**4:3 满幅**单视角 MP4 + macOS **Live Photo（`.pvt`）**。

## 环境

```bash
conda env update -f environment.yml
conda activate math
```

需要 **ffmpeg**（conda）与 **makelive**（仅 macOS，见 `requirements-macos.txt`）：

```bash
conda install -n math -c conda-forge ffmpeg
pip install -r requirements-macos.txt   # macOS only
```

## 测试

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
conda run -n math python -m pytest solve/plank-block-friction/tests -q
conda run -n math python -m ruff check solve/plank-block-friction
```

慢测（完整 MP4 / Live Photo）：

```bash
conda run -n math python -m pytest solve/plank-block-friction/tests -m slow
```

## 导出

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
./solve/plank-block-friction/run.sh
```

或：

```bash
conda run -n math python -m plank_block_friction
```

在 **macOS** 上，`run.sh` / CLI 会依次导出 **MP4** 与 **Live Photo**；Linux/Windows 仅导出 MP4（Live 调用会严格失败）。

### 产物目录：`ami/plank-block-friction/`

**preset-1**（\(\mu_1=0,\ \mu_2=1.0\)）三视角：

| 视角 | MP4 | Live Photo |
|------|-----|------------|
| 地面系 | `preset-1-ground.mp4` | `preset-1-ground_live.pvt` |
| 滑块视角 | `preset-1-block.mp4` | `preset-1-block_live.pvt` |
| 木板视角 | `preset-1-plank.mp4` | `preset-1-plank_live.pvt` |

Live 导出默认**仅保留** `.pvt`（打包后删除散装 `.jpg`/`.mov`）。调试时可传 `keep_intermediates=True`。

物理过程约 0.4–1.4 s（含共速后续播），播放时拉伸为约 **5 s**（`PLAYBACK_SECONDS=5`，`EXPORT_FPS=10`）。Live 静帧/视频经 letterbox 适配 **720×960（3:4）** 竖屏。

## 小红书发布（Live Photo）

1. 将 **`preset-1-*_live.pvt` 整个包** AirDrop 到 iPhone（勿只传散装 `.jpg`/`.mov`）。
2. 在相册确认有 **Live** 标识并可长按播放。
3. 小红书发笔记时选择 **实况图**。

详见 [docs/_common/xhs-live-photo-export.md](../_common/xhs-live-photo-export.md)。

| 现象 | 处理 |
|------|------|
| 缺少 makelive | `pip install -r requirements-macos.txt`（仅 macOS） |
| 缺少 ffmpeg | `conda install -n math -c conda-forge ffmpeg` |
| 非 macOS 报错 | Live 仅支持 macOS；MP4 可在任意平台导出 |
| 相册无 Live | 确认 AirDrop 的是 `.pvt` 目录包 |

## 文档

- 需求：[prd.md](./prd.md)
- 任务：[tasks.md](./tasks.md)
