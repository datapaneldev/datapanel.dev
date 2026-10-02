# Datapanel · 用户指南

[Live documentation](https://datapanel.dev/developers.html?lang=zh)

## GitHub

[datapaneldev/datapanel.dev](https://github.com/datapaneldev/datapanel.dev)

```
git clone git@github.com:datapaneldev/datapanel.dev.git
```

## 常用研究提示词

输入关键词后按 Tab 补全；点击列表可填入完整提示词。不会自动发送或提交计算任务。

7:3 应按时间顺序划分训练／验证，不随机打散；请另外预留独立 OOS，分割边界按 5min 标签跨度 purge/embargo。查询清单不代表所有股票或订单簿数据已可用。先确认真实数据、引擎、手续费与预算，缺失条件时要求 AI 明确说明；报价后由你确认执行。

### 平台入门

帮我查阅datapanel.dev的文章 告诉我它的功能

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=start)

### 股票数据清单

帮我查询datapanel.dev的股票数据清单

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=stocks)

### 加密价量特征

基于datapanel.dev的加密1min bar数据 帮我构建一批价量特征

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=features)

### MOVR 时序模型与双引擎回测

我想用MOVR/USDT 的数据 训练一个时序模型 用orderbook imbalance + lgb模型 标签用5min未来收益率 你帮我训练 训练集和验证集按照7:3划分 帮我跑py+cpp双回测引擎对拍 最终给我oos curve图

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=movr)

### 确认数据与字段

帮我查询当前账户可用的数据集、品种、日期覆盖和行情字段，区分已发布与待建设的数据。给我一个读取真实行情的最小示例，指出我在哪里编写特征；缺失数据请直接说明。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=schema)

### 并行参数搜索

基于可用的加密1min bar数据，帮我设计 LightGBM 并行搜参实验，比较不同标签周期、参数和随机种子。按时间顺序划分训练、验证和独立 OOS，锁定参数后再看 OOS；先给实验数量、算力规格和积分报价，等我确认再提交。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=search)

### 三套回测对拍

帮我把自己开发的回测、平台 Python 简易回测和 C++ 高精度回放回测进行对拍。统一信号时间、成交延迟、仓位、手续费、滑点和资金费率，比较逐笔成交、PnL、Sharpe、换手率与最大回撤，解释差异；不能运行的引擎请标明。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=compare)

### 稳健性与未来信息检查

帮我检查这个策略的时间戳、特征、标签和成交时序，排查未来信息泄漏；做不同年份、市场状态、成本和参数扰动的稳健性检查。保留失败实验，区分验证集表现与独立 OOS，不要虚构结果。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=robustness)

### 任务跟踪与结果解释

帮我查询我自己的任务排队和运行状态、积分使用及结果文件。任务失败时说明错误和重试建议，不要自动重复提交。取得实际结果后，解释 IC、Sharpe、换手率、回撤与 OOS 曲线，并给出可复现步骤。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=jobs)

### 股票截面因子研究

先查询我可用的股票行情、字段和日期范围，帮我设计动量、反转和量价截面因子实验。说明复权口径、停牌和退市处理；按时间顺序划分训练、验证和独立 OOS，比较 IC、分组收益、换手率及扣费表现。缺失数据请明确说明，先报价再由我确认执行。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=stock_factors)

### 多模型训练对比

使用同一份已发布行情、特征、标签和时间分割，对比 LightGBM、XGBoost、CatBoost 与 PyTorch 模型。先确认运行环境和可用 CPU/GPU，固定随机种子并记录版本；验证集选型后再评估独立 OOS，同时比较效果、训练时间和积分成本。先给出实验方案与报价，等我确认后再运行。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=model_compare)

### 交易成本与容量分析

基于我的实际回测信号和可用行情，分析手续费、滑点、成交延迟及资金费率变化对收益的影响；检查不同仓位规模和成交量占比下的策略容量。区分 bar 近似与真实回放，缺少深度或逐笔成交数据时明确限制。给出成本盈亏平衡点、结果对比和下一步验证计划，运行前先给资源与积分报价。

[在工作台使用](https://datapanel.dev/workbench.html?lang=zh&preset=cost_sensitivity)

# 全流程量化投研流水线

行情读取 → 特征生成 → CPU/GPU 训练 → 预测与回测 → 样本外验证 → 结果比较。

授权行情在平台计算环境内用于特征、训练与验证。实际数据版本及覆盖以目录为准。

注册并验证邮箱，使用 API key 查询实际规格、权限与预算，然后提交计算任务。请先阅读计算指南，再运行会消耗积分的请求。

[量化算力服务](https://datapanel.dev#compute)

当前开放状态： 邮箱注册 已启用 · USDT 付款 已启用

## 错误报告 · Error reports · 問題の報告 · 문제 신고

登录账户后提交错误报告，或使用 API key 调用以下接口。不要附带密钥、签名链接、私有代码或数据。每账户每小时最多 5 次，收到 429 后按 Retry-After 等待。received 表示已收件，不代表已修复。

Sign in to report a problem, or use your API key. Never include credentials, signed URLs, private code or data. Five reports per account per hour; honor Retry-After on 429. Received does not mean resolved.

ログインまたは API key で報告できます。認証情報、署名付きURL、非公開コード・データは送信しないでください。1アカウント毎時5件まで。429では Retry-After に従います。received は受付済みを意味します。

로그인하거나 API key로 문제를 신고하세요. 인증 정보, 서명 URL, 비공개 코드나 데이터를 포함하지 마세요. 계정당 시간당 5건이며 429 시 Retry-After를 따르세요. received는 접수 상태입니다.

```
POST /v1/reports
X-API-Key: YOUR_API_KEY
Content-Type: application/json

{"title":"Result retrieval failed","description":"Expected a downloadable result; received a timeout when querying my completed task.","category":"compute"}

GET /v1/reports?limit=20
X-API-Key: YOUR_API_KEY
```

title: 3–160 characters; description: 10–8000; category: account / data / compute / billing / other. GET lists only your own reports. No attachments. After a POST timeout, check your report list before retrying; duplicate prevention is not automatic.

[AI reporting Skill](https://datapanel.dev/datapanel-reporting-skill.md) · [AI research workbench](https://datapanel.dev/workbench.html)

## Datapanel 已核验数据集

### 全市场数据服务

美股 · 港股 · 期权 · 期货 · 外汇 · A股 · 加密

加密市场已有核验样例；美股、港股、期权、期货、外汇与 A 股正在接入。具体品种、字段和可申请日期以数据目录为准。

目录更新为跨市场代表性样例。日期表示该行实际核验的样例分区，不代表所有品种完整连续覆盖。可申请范围以实时 API 目录为准。

选择市场查看行情类型、样例日期、品种和字段。公开目录只展示数据属性，不展示部署位置或存储路径。

2026-09-24T21:25:02.824039+00:00 · 38 个核验样例 · 代表性样例；非完整覆盖清单

| 市场 | 行情类型 | 格式 / 样例数 | 核验样例日期 | 品种示例 | Demo |
| --- | --- | --- | --- | --- | --- |
| binance 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| binance_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| binance_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-17 → 2025-09-17 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| bit_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-08-28 → 2025-08-28 1 个观测日期；连续性未确认 | ada_usdt 1 个目录品种 | 查看 Demo |
| bit_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-08-28 → 2025-08-28 1 个观测日期；连续性未确认 | ada_usdt 1 个目录品种 | 查看 Demo |
| bitget 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| bitget_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-17 → 2025-09-17 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| bitget_spot.um 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-27 → 2025-09-27 1 个观测日期；连续性未确认 | pepe_usdt 1 个目录品种 | 查看 Demo |
| bitget_usdt_swap.um 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-27 → 2025-09-27 1 个观测日期；连续性未确认 | pepe_usdt 1 个目录品种 | 查看 Demo |
| bitmart 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| bitmart_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-05-21 → 2025-05-21 1 个观测日期；连续性未确认 | launchcoin_usdt 1 个目录品种 | 查看 Demo |
| bitmart_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| bybit 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| bybit_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-15 → 2025-06-15 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| bybit_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-17 → 2025-09-17 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| coinex 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| coinex_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-15 → 2025-06-15 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| coinex_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| gate 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| gate_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-15 → 2025-06-15 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| gate_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| hashkey_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-03 → 2025-06-03 1 个观测日期；连续性未确认 | arb_usdt 1 个目录品种 | 查看 Demo |
| huobi 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| huobi_spot 已核验样例 | MBP-20 | csv.gz 1 个文件 | 2025-10-09 → 2025-10-09 1 个观测日期；连续性未确认 | ada_usdt 1 个目录品种 | 查看 Demo |
| huobi_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| kucoin 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| kucoin_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-15 → 2025-06-15 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| kucoin_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| mexc_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-08-26 → 2025-08-26 1 个观测日期；连续性未确认 | h_usdt 1 个目录品种 | 查看 Demo |
| okx 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| okx_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-06-15 → 2025-06-15 1 个观测日期；连续性未确认 | a_usdt 1 个目录品种 | 查看 Demo |
| okx_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| phemex 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| phemex_usdt_swap 已核验样例 | MBP-20 | csv.gz 1 个文件 | 2025-09-05 → 2025-09-05 1 个观测日期；连续性未确认 | ach_usdt 1 个目录品种 | 查看 Demo |
| phemex_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2024-07-22 → 2024-07-22 1 个观测日期；连续性未确认 | ach_usdt 1 个目录品种 | 查看 Demo |
| upbit_spot 已核验样例 | bbo | csv.gz 1 个文件 | 2025-08-19 → 2025-08-19 1 个观测日期；连续性未确认 | api3_usdt 1 个目录品种 | 查看 Demo |
| woo 已核验样例 | bbo | csv.gz 1 个文件 | 2025-01-07 → 2025-01-07 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |
| woo_usdt_swap 已核验样例 | bbo | csv.gz 1 个文件 | 2025-09-01 → 2025-09-01 1 个观测日期；连续性未确认 | 1inch_usdt 1 个目录品种 | 查看 Demo |

## 真实 Demo 与字段说明

选择一个已盘点数据集，查看实际文件头与少量样例行。表格按原文件顺序展示；未确认语义的字段明确标记，不推断单位。空值不等于 0；ID 与微秒/纳秒时间在 JavaScript 中建议保留字符串或 BigInt。

### binance / bbo

文件格式： `csv.gz` · 样例文件： `binance@1inch_usdt@1736214097381000000.csv.gz`

样例为真实文件前几行，不代表完整数据质量验收。

### Demo 数据

| lcTsNs | exSeq | binance@1inch_usdt*bp | binance@1inch_usdt*bq | binance@1inch_usdt*ap | binance@1inch_usdt*aq |
| --- | --- | --- | --- | --- | --- |
| 1736214097381000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |
| 1736214097393000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |

### 逐字段说明

| 字段名 | 说明 / 单位 | 示例值 |
| --- | --- | --- |
| lcTsNs | 本地采集/接收时间，Unix epoch 纳秒（UTC）；19 位整数，Python 用 int，JavaScript 用 BigInt 或字符串。 | 1736214097381000000 |
| exSeq | 源端序号/时间载荷。不同市场可能采用不同口径；本样例中 0 或 19 位数均会出现。不要直接把它当作统一的事件时间。 | 0 |
| binance@1inch_usdt*bp | 买一价格. 星号前为市场@品种，数量单位依市场与合约。 | 0.4337 |
| binance@1inch_usdt*bq | 买一挂单数量. 星号前为市场@品种，数量单位依市场与合约。 | 3367 |
| binance@1inch_usdt*ap | 卖一价格. 星号前为市场@品种，数量单位依市场与合约。 | 0.4338 |
| binance@1inch_usdt*aq | 卖一挂单数量. 星号前为市场@品种，数量单位依市场与合约。 | 2267 |

### 时间与数值解析

```python
from datetime import datetime, timezone
value_ns = 1754611351173000000  # lcTsNs, preserve as Python int
seconds, nanoseconds = divmod(value_ns, 1_000_000_000)
dt = datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=nanoseconds // 1000)
# datetime keeps microseconds; preserve value_ns for full nanosecond precision.
# Prices and quantities: use decimal.Decimal when exact decimal arithmetic matters.
```

Tardis 字段口径参考 [官方 CSV schema](https://docs.tardis.dev/downloadable-csv-files)。非 Tardis 文件以各数据集的采样与来源定义为准。

## Python · 查询研究环境

密钥仅从环境变量读取。此示例只查询权限与规格，不创建付费任务。

```python
import os
import requests

base = "https://datapanel.dev"
session = requests.Session()
session.headers["X-API-Key"] = os.environ["DATAPANEL_API_KEY"]
for path in ["/v1/me", "/v1/catalog", "/v1/compute/profiles"]:
    response = session.get(base + path, timeout=30)
    response.raise_for_status()
    print(path, response.json())
# Read the compute guide and actual API schemas before creating a job.
# Retrieve only your own research assets through /v1/compute/artifacts.
```

[量化算力服务](https://datapanel.dev#compute)

## 六档套餐，围绕量化研究计算

一个订阅，连接研究数据、CPU/GPU 计算与私有产物。算力积分每周五 16:00（UTC+8）重置。

| 档位 | 价格 · USDT / 月 | 研究环境 | 每周算力积分 |
| --- | --- | --- | --- |
| 新用户免费体验 | 0 | 授权数据就近计算 | 50 |
| 教育 | 59.94 | 授权数据就近计算 | 1,450 |
| 标准 | 99.9 | 授权数据就近计算 | 2,400 |
| 专业 | 299.9 | 授权数据就近计算 | 7,200 |
| 企业 | 999.9 | 授权数据就近计算 | 25,000 |
| 无限 | 9999.9 | 授权数据就近计算 | 无累计积分上限 |

1 积分 = 1 个分配 CPU 单位小时，包含每单位 2 GiB 内存；超额内存为 0.05 积分 / GiB·小时。GPU 按型号计价，提交前可查看报价。

积分按周发放，不结转；任务按实际分配资源与可信运行时长结算，排队不计费。具体规格、权限与预算以账户及报价为准。

体验一次性 30 天，首次使用绑定单一 IP；教育资格需审核。

无限套餐仍受单任务资源、时限、并发、公平排队和防滥用规则约束。集群总规模不代表单个账户独占资源。

每次私有代码或结果导出须小于 1 GB。请求权重按套餐为 30 / 120 / 120 / 300 / 600 / 1200 每分钟，响应头返回剩余权重和重置时间。GB/TB 均为十进制。

支付方式与账户权益以账户页面为准。

[免费体验 / 查看账户](https://datapanel.dev/account?lang=zh)

任务并发与 GPU 额度取决于当前套餐、账户权限及可用容量。报价前读取实时账户与能力响应；CPU 和 GPU 任务共同受账户任务数上限约束。

## 量化算力服务

从预测值、特征与模型，到可复现的验证结果，以统一 API 组织研究流程。

### 预测值驱动搜参

上传标准预测值文件，指定品种与时间范围，创建参数搜索和回测方案。策略生成逻辑可以保留在本地。

### 自定义特征与模型

用脚本定义特征、标签和模型，绑定版本明确的数据快照、资源规格和预算，让每次实验都有可追踪的输入与结果。

### 可复用的私有产物

代码、预测和封存结果归属于你的账户；通过 API key 获取私有资产，下载时重新验证权限。单次导出小于 1 GB。

提交前查询规格、权限和预算，预留积分后进入队列；通过 API 查询状态，完成后取回结果。额度、并发和时限共同约束资源使用。

### 严谨回测与交叉验证

底层 C++ 引擎具备 tick 事件回放和延迟撮合实现。双引擎回测对拍建设中，面向独立参考实现交叉核对成交假设与结果差异。

结合时序切分、样本外验证、预测可用时间检查与数据版本追踪，降低回测失真、过拟合和未来数据泄漏风险。双引擎结果一致不等于策略有效，也不保证实盘收益。

已完成分钟级合成数据的多输入回测接入与记账一致性验证；真实 tick 撮合精度与双引擎对拍须分别验收。

### 标准预测文件

预测文件包含品种、UTC 毫秒时间、预测可用时间和预测值；必须明确预测语义，并与实际数据快照绑定。

```
symbol,timestamp_ms,available_at_ms,prediction
BTCUSDT,1767225600000,1767225600000,0.25
```

样例采用 target_fraction：0.25 表示目标仓位比例 25%；return_bps 则表示预测收益基点，两种语义不能混用。回测验证不等于策略盈利或实盘资格。

### 你的研究资产，只为你的研究服务

账户所有权检查、源码加密保存、私有下载鉴权与管理审计保护研究资产；公开行情目录不包含用户代码、预测或模型。

### 通过 Claude 或 Codex 接入

让编程助手阅读 SDK 和接口说明，将 API key 保存在本机环境变量中。先查询数据与服务权限，再核对预算、提交请求并校验结果。

示例提示词：阅读 Datapanel SDK，从环境变量读取 API key。查询可用数据、服务权限和剩余额度，展示范围与预算，保存任务 ID，轮询状态并校验下载结果。不要输出密钥。

## 按套餐分档限频

每次私有代码或结果导出须小于 1 GB。请求权重按套餐为 30 / 120 / 120 / 300 / 600 / 1200 每分钟，响应头返回剩余权重和重置时间。GB/TB 均为十进制。

通过 API 查询计算规格与预算，提交任务并取回自己的研究结果。

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 119
X-RateLimit-Reset: 1790294460
X-RateLimit-Window: 60
X-RateLimit-Scope: key
X-Request-Weight: 1
```

Reset: Unix timestamp (UTC seconds). Scope: key / account / downloads / compute. Retry-After: seconds until a rejected request may retry. Windows start on first request; this is separate from Friday 16:00 UTC+8 weekly quota resets.

## Swagger · 在线接口调试

通过 API 查询计算规格与预算，提交任务并取回自己的研究结果。

在线调试会使用你的账户权限并消耗对应额度。请先阅读接口说明，妥善保管 API key；刷新页面会清除输入的密钥。

## AI 量化工作台

登录后描述研究目标。AI 可读取官方文档、SDK、训练 Demo、当前账户的数据目录、算力规格和积分；也可搜索公开互联网并提供来源。对话和账户研究上下文由 Datapanel 私有 AI 处理，不自动转发给云端模型；公开搜索仅将检索词发送给独立搜索服务，请勿输入密钥或未经授权的策略。

先让 AI 阅读 Demo，检查特征、行情字段和训练验证边界；将完整 Python 代码填入任务编辑器，选择已有数据与可用规格，查看报价后确认提交。报价不会运行代码，提交后预留积分；使用任务 ID 查询状态，在成功后准备私有结果导出并校验 SHA256。浏览器下载上限为 128 MiB，更大结果请使用 SDK。

[打开 AI 工作台](https://datapanel.dev/workbench.html) · [文档与 SDK 示例索引](https://datapanel.dev/ai-resources.json) · [下载研究 Skill](https://datapanel.dev/datapanel-research-skill.md)
