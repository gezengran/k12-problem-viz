# plank-block-friction — 运行说明

木板–滑块动摩擦方向可视化：9:16 上下双屏（地面系 / 滑块视角），三预设 MP4。

## 环境

```bash
conda env update -f environment.yml
conda activate math
```

需要 **ffmpeg**（导出 MP4）：

```bash
conda install -n math -c conda-forge ffmpeg
```

## 测试

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
conda run -n math python -m pytest solve/plank-block-friction/tests -q
conda run -n math python -m ruff check solve/plank-block-friction
```

慢测（完整 MP4）：

```bash
conda run -n math python -m pytest solve/plank-block-friction/tests -m slow
```

## 导出 MP4

```bash
export PYTHONPATH="solve/_common:solve/plank-block-friction"
./solve/plank-block-friction/run.sh
```

或：

```bash
conda run -n math python -m plank_block_friction
```

产物目录：`ami/plank-block-friction/`

- `preset-1.mp4` — \(\mu_1=0,\ \mu_2=0.2\)  
- `preset-2.mp4` — \(\mu_1=0,\ \mu_2=0.6\)  
- `preset-3.mp4` — \(\mu_1=0.15,\ \mu_2=0.2\)  

初始状态：滑块在**木板正中**；动画在**滑块离开木板并落到地面**后立刻结束（无额外尾帧）。物理过程约 0.1–0.5 s，播放时拉伸为约 **5 s**（`PLAYBACK_SECONDS=5`，`EXPORT_FPS=10`）。

## Live Photo（可选）

v1 以 MP4 为主。若需小红书 `.pvt`，在 macOS 上可参考 [docs/_common/xhs-live-photo-export.md](../_common/xhs-live-photo-export.md)，将 MP4 或帧序列接入 `solve/_common` 的 Live 导出器（后续任务 7 可接 `run.sh`）。

## 文档

- 需求：[prd.md](./prd.md)  
- 任务：[tasks.md](./tasks.md)
