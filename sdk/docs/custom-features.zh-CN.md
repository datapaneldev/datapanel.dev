# 用自己的行情特征训练第一个模型

本教程带你完成：**选择一段盘口行情 → 编写四个特征 → 提交 CPU 训练 → 下载模型 → 计算预测值**。你只需要 Python 3.10 或更新版本，以及 DataPanel API key。

示例预测“下一次盘口更新的中间价收益”，单位是 bps（1 bps = 0.01%）。它是学习平台流程的小模型，不是可以直接交易的策略。先用合成数据在本机熟悉操作，再提交真实行情任务。

## 1. 准备示例项目

打开已下载的 `datapanel-agent-examples` 文件夹，在这个文件夹内启动终端。后面的命令都从这里执行。

```bash
python -m venv .venv
```

Windows PowerShell 激活环境：

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux 激活环境：

```bash
source .venv/bin/activate
```

安装示例依赖：

```bash
python -m pip install -e ".[dev]"
```

## 2. 先跑一次，不需要 API key

```bash
python examples/training/cpu_model.py --features examples/training/custom_features.py --work-dir work/my-first-model
```

这一步使用合成行情，在本机运行，不访问 DataPanel、不消耗平台积分。完成后打开 `work/my-first-model/outputs/result.json`：

- `model.architecture` 是 `linear_4_to_1`：四个特征输入，一个预测输出。
- `model.feature_order` 是特征顺序。
- `model.weights` 是四个学到的权重。
- `metrics` 是训练、验证及留出区段的误差。

## 3. 在哪里编写自己的特征

**打开 [examples/training/custom_features.py](../examples/training/custom_features.py)，修改 `build_features(previous, current)`。** 这是本教程需要你编辑的主要文件，无需修改上传、排队或下载代码。

`previous` 是上一条盘口，`current` 是当前盘口。它们是 Python 字典，例如 `current["Bp1"]` 表示当前第一档买价。函数返回一个数值列表，每个数对应一个特征。

文件中的完整例子如下：

```python
FEATURE_NAMES = ("last_mid_return_bps", "spread_bps", "level1_imbalance", "level2_imbalance")
FEATURE_INPUT_FIELDS = ("Bp1", "Ap1", "Bq1", "Aq1", "Bq2", "Aq2")


def build_features(previous, current):
    mid = (current["Bp1"] + current["Ap1"]) / 2
    previous_mid = (previous["Bp1"] + previous["Ap1"]) / 2
    level2_total = current["Bq2"] + current["Aq2"]
    level2 = (current["Bq2"] - current["Aq2"]) / level2_total if level2_total > 0 else 0.0
    return [
        (mid / previous_mid - 1) * 10000,
        (current["Ap1"] - current["Bp1"]) / mid * 10000,
        (current["Bq1"] - current["Aq1"]) / (current["Bq1"] + current["Aq1"]),
        level2,
    ]
```

这四个数依次表示：上一次更新以来的中价变化、买卖点差、一档买卖数量不平衡、二档买卖数量不平衡。数量不平衡为正，表示该档买侧数量大于卖侧。

新增特征时同步改三处：在 `FEATURE_NAMES` 增加名字，在 `FEATURE_INPUT_FIELDS` 声明新增原始字段，在 `return` 列表相同位置增加计算结果。最多 32 个特征；每个结果必须是有限数，不能为 NaN 或无穷大。特征只能使用当时及过去的信息，不能使用下一条行情或标签。

## 4. 有哪些行情字段可以用

本教程使用 **MBP-20 二十档盘口**，不是 K 线或逐笔成交数据。

| 字段 | 含义与用途 |
|---|---|
| `lcTsNs` | 纳秒时间戳，供排序及时间过滤；保持整数精度 |
| `Bp1` ～ `Bp20` | 买侧第一至第二十档价格 |
| `Ap1` ～ `Ap20` | 卖侧第一至第二十档价格 |
| `Bq1` ～ `Bq20` | 对应买档数量 |
| `Aq1` ～ `Aq20` | 对应卖档数量 |
| `exSeq` | 文件中存在，但语义尚未确认；本示例不允许作为特征输入 |

例如，想使用第五档数量，就在 `FEATURE_INPUT_FIELDS` 中加入 `"Bq5", "Aq5"`，然后读取 `current["Bq5"]` 和 `current["Aq5"]`。价格档位的扩展方式相同。

本样本没有 `open`、`close`、成交量、资金费率等字段，不能直接在代码里引用。数量单位尚未确认，示例仅计算相同口径的比例，不把数量直接当作币数或合约张数。[查看完整字段说明](market-fields.md)。

## 5. 连接自己的 DataPanel 账户

在当前终端设置 API key。不要把 key 写进特征文件或提交到 Git。

Windows PowerShell（输入时不回显）：

```powershell
$secret = Read-Host "DataPanel API key" -AsSecureString
$env:DATAPANEL_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
Remove-Variable secret
```

macOS / Linux（Bash，输入时不回显）：

```bash
read -rsp "DataPanel API key: " DATAPANEL_API_KEY
export DATAPANEL_API_KEY
```

检查账户及实际可用数据：

```bash
datapanel-demo account --mode live
datapanel-demo catalog --mode live
```

账户需要具备 CPU 任务执行权限及足够积分。若提示未获准执行，先处理账户权限，重复提交不会解除限制。

## 6. 选择市场、品种和时间段

打开 [examples/training/selection.mbp20.json](../examples/training/selection.mbp20.json)：

```json
{
  "market": "binance_usdt_swap",
  "data_type": "MBP-20",
  "symbol": "movr_usdt",
  "start": "2025-08-08T14:06:16+00:00",
  "end": "2025-08-08T14:07:16+00:00"
}
```

这是已运行过的真实行情选择。`+00:00` 表示 UTC；更换品种或日期时，以目录查询返回的可用范围为准，不要仅修改名称就假设数据存在。这个入门示例要求所选行情含 120～5,000 行，不适合直接选择整年的 tick 数据。

模型标签为下一次更新的中价收益：`(下一条中价 / 当前中价 - 1) × 10000`，并非固定一秒后的收益。代码按时间分割训练、验证和留出数据，标准化只使用训练部分。[标签实现](../src/datapanel_agent/training_program.py) 中的 `samples()` 可供进一步修改。

## 7. 报价，然后提交训练

先运行下面一行，准备训练输入并查看报价；此时不会启动训练。准备过程会创建私有资产及数据快照。

```bash
python examples/training/cpu_model.py --mode live --selection examples/training/selection.mbp20.json --features examples/training/custom_features.py --work-dir work/my-live-model --profile cpu-small --allow-writes --wall-seconds 120 --max-credits 1
```

确认报价后，加上 `--submit` 启动任务：

```bash
python examples/training/cpu_model.py --mode live --selection examples/training/selection.mbp20.json --features examples/training/custom_features.py --work-dir work/my-live-model --profile cpu-small --allow-writes --submit --wall-seconds 120 --max-credits 1
```

`--max-credits 1` 是本次可接受的报价上限，`--wall-seconds 120` 是这个小样例的运行时限。Demo 会上传特征源码、提交任务、查询进度，并在完成后下载模型和验证文件完整性。

如果本次查询结束时仍在排队或运行，**重新执行相同命令、保留同一个运行目录**，即可继续查询原任务。不要删掉 `run.json` 后反复提交。修改了特征或时间范围，则使用新的运行目录，例如 `work/my-live-model-v2`。

## 8. 取回模型并计算预测值

成功后，模型保存在 `work/my-live-model/result.json`，任务进度保存在同目录的 `run.json`。

在项目根目录新建 `predict_my_model.py`，粘贴下面的代码。它读取模型附带的一组特征，计算并打印预测值，不执行下载的源码：

```python
import json
from pathlib import Path
from datapanel_agent.training import verify_model
from datapanel_agent.training_program import predict

path = Path("work/my-live-model/result.json")
print("模型校验：", verify_model(path)["status"])
result = json.loads(path.read_text(encoding="utf-8"))
features = result["reload_probes"][0]["x"]
print("特征顺序：", result["model"]["feature_order"])
print("特征值：", features)
print("预测收益（bps）：", predict(result["model"], features))
print("原始预测（bps）：", result["reload_probes"][0]["prediction_bps"])
```

```bash
python predict_my_model.py
```

新行情预测时，用**训练时同一份** `build_features` 计算特征，再传给 `predict(model, features)`；保持字段、顺序和计算方法一致。`predict` 会应用模型内保存的标准化参数，不要自己再标准化一次。正值表示预测中价上涨，负值表示下跌；它没有包含手续费、成交概率或交易执行逻辑。

## 常见问题

| 现象 | 怎么处理 |
|---|---|
| `No module named datapanel_agent` | 确认激活了安装依赖的 Python 环境，并在项目根目录重新安装 |
| 无权限或 API key 无效 | 先运行账户查询，核对 key 及账户执行权限 |
| 字段缺失或数据行数不符 | 核对选择的是 MBP-20，检查目录覆盖，缩小或调整区间 |
| 特征输出包含 NaN / Inf | 检查除零和缺失值；显式处理，不要假定所有档位都有数量 |
| 报价超过预算 | 核对资源与时限；确认接受费用后才提高 `--max-credits` |
| 查询结束但任务未完成 | 用相同命令与原运行目录续接，不创建重复任务 |
| 模型表现不好 | 比较验证误差与基线；流程成功并不保证预测有效 |
