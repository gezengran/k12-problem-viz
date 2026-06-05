# K12 Problem Viz

初高中数学、物理题目的 **建模求解 + 几何可视化** 仓库。每道题一个 `case_id`，代码在 `solve/`，导出的媒体在 `ami/`，说明文档在 `docs/`。

## Layout

| 目录 | 说明 |
|------|------|
| `solve/<case_id>/` | 该题的 Python 求解与测试 |
| `ami/<case_id>/` | 导出的动图、静图（无 `.py`） |
| `docs/<case_id>/` | 该题的 PRD、任务拆解、初中生版解答 |
| `docs/_common/` | 跨题共用说明（如 Live Photo 导出 PRD） |
| `pics/` | 题目参考图 |
| `solve/_common/` | 跨题共用路径、小红书 Live Photo 导出 |

## Cases

| case_id | 说明 |
|---------|------|
| [umbrella-rain](docs/umbrella-rain/solution-junior.md) | 雨天撑伞（几何淋湿区域） |
| [compound-growth](docs/compound-growth/runbook.md) | 日积月累示范（`y=x²` vs `y=1.01^x` → Live Photo） |
| [plank-block-friction](docs/plank-block-friction/runbook.md) | 木板–滑块动摩擦方向（双屏 9:16 MP4） |

## Setup

```bash
conda env create -f environment.yml   # env name: math
conda activate math
export PYTHONPATH="solve/_common:solve/umbrella-rain:solve/compound-growth:solve/plank-block-friction"
pytest -q
./solve/umbrella-rain/run.sh
./solve/compound-growth/run.sh      # macOS only → .pvt
./solve/plank-block-friction/run.sh # → ami/plank-block-friction/*.mp4
```

### 小红书 Live Photo（`.pvt`）

- **仅 macOS**：依赖 `makelive`（pip）与 `ffmpeg`（conda）
- 动画主路径导出 **`.pvt`**，AirDrop **整个包** 到 iPhone 后发小红书实况；平台不支持 GIF 作为主载体
- 详见 [docs/_common/xhs-live-photo-export.md](docs/_common/xhs-live-photo-export.md) 与 [compound-growth runbook](docs/compound-growth/runbook.md)

## License

TBD.
