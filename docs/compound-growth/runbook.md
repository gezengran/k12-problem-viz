# compound-growth — 小红书 Live 发布 runbook

示范 case：对比 `y=x²` 与 `y=1.01^x`，导出 **Live Photo（`.pvt`）**。

## 环境

- **macOS**（必须；Linux/CI 无法打包 `.pvt`）
- Conda 环境 `math`，已安装 `ffmpeg`（conda）与 `makelive`（pip，见根目录 `environment.yml`）

```bash
conda env update -f environment.yml
conda activate math
```

## 生成

```bash
export PYTHONPATH="solve/_common:solve/compound-growth"
./solve/compound-growth/run.sh
```

产物目录：`ami/compound-growth/`（含 `compound_growth_live.pvt` 及调试期的 `.jpg`/`.mov`）。

## 发布到小红书

1. 将 **`compound_growth_live.pvt` 整个包** AirDrop 到 iPhone（不要只传散装 `.jpg`/`.mov`）。
2. 在「照片」中确认该图可 **Live 播放**。
3. 小红书发帖时选择 **实况图** / Live 入口。

## 故障排查

| 现象 | 处理 |
|------|------|
| 报错需要 macOS | 在 Mac 上执行 `run.sh` |
| 缺少 makelive | `conda env update -f environment.yml` |
| 缺少 ffmpeg | `conda install -n math -c conda-forge ffmpeg` |
| 相册无 Live | 确认 AirDrop 的是 `.pvt` 目录包，不是单张 JPG |
