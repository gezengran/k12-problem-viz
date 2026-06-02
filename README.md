# K12 Problem Viz

初高中数学、物理题目的 **建模求解 + 几何可视化** 仓库。每道题一个 `case_id`，代码在 `solve/`，导出的 GIF/PNG 在 `ami/`，说明文档在 `docs/`。

## Layout

| 目录 | 说明 |
|------|------|
| `solve/<case_id>/` | 该题的 Python 求解与测试 |
| `ami/<case_id>/` | 导出的动图、静图（无 `.py`） |
| `docs/<case_id>/` | 该题的 PRD、任务拆解、初中生版解答 |
| `docs/_common/` | 跨题共用说明（如 Live Photo 导出 PRD） |
| `pics/` | 题目参考图 |
| `solve/_common/` | 跨题共用路径等工具 |

## Cases

| case_id | 说明 |
|---------|------|
| [umbrella-rain](docs/umbrella-rain/solution-junior.md) | 雨天撑伞（几何淋湿区域） |

## Setup

```bash
conda env create -f environment.yml   # env name: math
conda activate math
export PYTHONPATH="solve/_common:solve/umbrella-rain"
pytest solve/umbrella-rain/tests -q
./solve/umbrella-rain/run.sh
```

## License

TBD.
