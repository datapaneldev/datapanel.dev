# Datapanel · User guide

[Live documentation](https://datapanel.dev/developers.html?lang=en)

## GitHub

[datapaneldev/datapanel.dev](https://github.com/datapaneldev/datapanel.dev)

```
git clone git@github.com:datapaneldev/datapanel.dev.git
```

## Common research prompts

Type a keyword and press Tab to complete, or select a prompt. Nothing is sent or submitted automatically.

Split train/validation 7:3 chronologically, never randomly. Reserve independent OOS and purge/embargo boundaries for the 5-minute label horizon. Catalog entries do not guarantee stocks or orderbooks are available. Confirm actual data, engines, costs and budget; ask AI to report gaps. Confirm execution after a quote.

### Platform introduction

Read the articles on datapanel.dev and explain its features.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=start)

### Stock data catalog

Find the stock data catalog on datapanel.dev.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=stocks)

### Crypto price-volume features

Build a set of price-volume features using datapanel.dev crypto 1-minute bars.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=features)

### MOVR model and dual-engine backtest

Train a MOVR/USDT time-series model using orderbook imbalance and LightGBM, with 5-minute forward returns as the label. Split training and validation 7:3, compare Python and C++ backtest engines, and return an OOS equity curve.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=movr)

### Available data and fields

List datasets, symbols, date coverage and market fields available to my account. Distinguish published data from planned coverage. Show a minimal real-data reader and where I write features; report missing data honestly.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=schema)

### Parallel parameter search

Design parallel LightGBM experiments on available crypto 1-minute bars across label horizons, parameters and seeds. Use chronological train/validation and independent OOS. Freeze parameters before OOS. Show experiment count, resources and credit quote; wait for my confirmation before submitting.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=search)

### Compare three backtests

Compare my own backtest, the platform Python simple backtest and C++ precision replay. Align signal time, fill latency, positions, fees, slippage and funding. Compare fills, PnL, Sharpe, turnover and drawdown. Explain discrepancies and label unavailable engines.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=compare)

### Robustness and leakage

Check timestamps, features, labels and execution timing for look-ahead leakage. Test years, regimes, costs and parameter perturbations. Preserve failed experiments and distinguish validation from independent OOS. Never invent results.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=robustness)

### Task status and results

Check my own queue/running tasks, credit usage and results. Explain failures and retry options without automatically resubmitting. Interpret actual IC, Sharpe, turnover, drawdown and OOS curves, with reproducible steps.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=jobs)

### Stock cross-sectional factors

Check my available stock data, fields and dates, then design cross-sectional momentum, reversal and price-volume factors. Explain adjustment, suspensions and delisting treatment. Use chronological train, validation and independent OOS; compare IC, bucket returns, turnover and net-of-cost results. Report missing data. Quote first and wait for my execution confirmation.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=stock_factors)

### Compare model training

Compare LightGBM, XGBoost, CatBoost and PyTorch using identical published data, features, labels and chronological splits. Check the runtime and available CPU/GPU, freeze seeds and record versions. Select on validation before independent OOS; compare quality, training time and credit cost. Present the plan and quote, then wait for confirmation.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=model_compare)

### Trading costs and capacity

Use my actual signals and available data to study sensitivity to fees, slippage, fill latency and funding, plus capacity across position sizes and participation rates. Distinguish bar approximations from replay and state limitations when depth or trades are missing. Report break-even costs, comparisons and next validation steps; quote resources and credits before execution.

[Use in workbench](https://datapanel.dev/workbench.html?lang=en&preset=cost_sensitivity)

# End-to-end quantitative research pipeline

Market data → features → CPU/GPU training → prediction and backtesting → out-of-sample validation → comparison.

Licensed market data is used inside the platform for features, training and validation. Check the catalog for actual versions and coverage.

Register and verify your email. Use your API key to check profiles, permissions and budgets before submitting compute jobs. Read the compute guide before spending credits.

[Quantitative computing](https://datapanel.dev#compute)

Current availability: Email registration Enabled · USDT payments Enabled

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

## Verified Datapanel datasets

### Multi-asset market data

US equities · Hong Kong equities · Options · Futures · FX · A-shares · Crypto

Verified crypto samples are available. US and Hong Kong equities, options, futures, FX and A-shares are being onboarded. Consult the catalog for instruments, fields and requestable dates.

The refreshed catalog contains representative samples across markets. Dates identify the verified sample partition, not continuous coverage of every instrument. Requestable ranges follow the live API catalog.

Choose a market to inspect types, sample dates, instruments and fields. Public catalogs show data attributes, without deployment locations or storage paths.

2026-09-24T21:25:02.824039+00:00 · 38 verified samples · Representative samples, not complete coverage

| Market | Data type | Format / samples | Verified sample dates | Example instruments | Demo |
| --- | --- | --- | --- | --- | --- |
| binance Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| binance_spot Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| binance_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-17 → 2025-09-17 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| bit_spot Verified sample | bbo | csv.gz 1 files | 2025-08-28 → 2025-08-28 1 observed dates; continuity not verified | ada_usdt 1 catalog instruments | View demo |
| bit_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-08-28 → 2025-08-28 1 observed dates; continuity not verified | ada_usdt 1 catalog instruments | View demo |
| bitget Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| bitget_spot Verified sample | bbo | csv.gz 1 files | 2025-09-17 → 2025-09-17 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| bitget_spot.um Verified sample | bbo | csv.gz 1 files | 2025-09-27 → 2025-09-27 1 observed dates; continuity not verified | pepe_usdt 1 catalog instruments | View demo |
| bitget_usdt_swap.um Verified sample | bbo | csv.gz 1 files | 2025-09-27 → 2025-09-27 1 observed dates; continuity not verified | pepe_usdt 1 catalog instruments | View demo |
| bitmart Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| bitmart_spot Verified sample | bbo | csv.gz 1 files | 2025-05-21 → 2025-05-21 1 observed dates; continuity not verified | launchcoin_usdt 1 catalog instruments | View demo |
| bitmart_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| bybit Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| bybit_spot Verified sample | bbo | csv.gz 1 files | 2025-06-15 → 2025-06-15 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| bybit_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-17 → 2025-09-17 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| coinex Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| coinex_spot Verified sample | bbo | csv.gz 1 files | 2025-06-15 → 2025-06-15 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| coinex_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| gate Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| gate_spot Verified sample | bbo | csv.gz 1 files | 2025-06-15 → 2025-06-15 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| gate_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| hashkey_spot Verified sample | bbo | csv.gz 1 files | 2025-06-03 → 2025-06-03 1 observed dates; continuity not verified | arb_usdt 1 catalog instruments | View demo |
| huobi Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| huobi_spot Verified sample | MBP-20 | csv.gz 1 files | 2025-10-09 → 2025-10-09 1 observed dates; continuity not verified | ada_usdt 1 catalog instruments | View demo |
| huobi_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| kucoin Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| kucoin_spot Verified sample | bbo | csv.gz 1 files | 2025-06-15 → 2025-06-15 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| kucoin_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| mexc_spot Verified sample | bbo | csv.gz 1 files | 2025-08-26 → 2025-08-26 1 observed dates; continuity not verified | h_usdt 1 catalog instruments | View demo |
| okx Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| okx_spot Verified sample | bbo | csv.gz 1 files | 2025-06-15 → 2025-06-15 1 observed dates; continuity not verified | a_usdt 1 catalog instruments | View demo |
| okx_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| phemex Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| phemex_usdt_swap Verified sample | MBP-20 | csv.gz 1 files | 2025-09-05 → 2025-09-05 1 observed dates; continuity not verified | ach_usdt 1 catalog instruments | View demo |
| phemex_usdt_swap Verified sample | bbo | csv.gz 1 files | 2024-07-22 → 2024-07-22 1 observed dates; continuity not verified | ach_usdt 1 catalog instruments | View demo |
| upbit_spot Verified sample | bbo | csv.gz 1 files | 2025-08-19 → 2025-08-19 1 observed dates; continuity not verified | api3_usdt 1 catalog instruments | View demo |
| woo Verified sample | bbo | csv.gz 1 files | 2025-01-07 → 2025-01-07 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |
| woo_usdt_swap Verified sample | bbo | csv.gz 1 files | 2025-09-01 → 2025-09-01 1 observed dates; continuity not verified | 1inch_usdt 1 catalog instruments | View demo |

## Real examples and field definitions

Choose an inventoried dataset to inspect its real header and sample rows. Columns follow the source order. Unconfirmed semantics are marked; units are not inferred. Null is not zero. Preserve IDs and micro/nanosecond timestamps as strings or BigInt in JavaScript.

### binance / bbo

File format: `csv.gz` · Sample file: `binance@1inch_usdt@1736214097381000000.csv.gz`

Samples show the first rows of real files, not full data-quality acceptance.

### Demo data

| lcTsNs | exSeq | binance@1inch_usdt*bp | binance@1inch_usdt*bq | binance@1inch_usdt*ap | binance@1inch_usdt*aq |
| --- | --- | --- | --- | --- | --- |
| 1736214097381000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |
| 1736214097393000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |

### Field-by-field reference

| Field name | Description / units | Example value |
| --- | --- | --- |
| lcTsNs | Local capture/receive time in UTC Unix nanoseconds. Preserve the 19-digit integer; use Python int or JavaScript BigInt/string. | 1736214097381000000 |
| exSeq | Source sequence/time payload; semantics vary by market. Samples contain zero or 19-digit values. Do not treat it as a universal event timestamp. | 0 |
| binance@1inch_usdt*bp | Best bid price. Before *: market@instrument; quantity units depend on market and contract. | 0.4337 |
| binance@1inch_usdt*bq | Best bid quantity. Before *: market@instrument; quantity units depend on market and contract. | 3367 |
| binance@1inch_usdt*ap | Best ask price. Before *: market@instrument; quantity units depend on market and contract. | 0.4338 |
| binance@1inch_usdt*aq | Best ask quantity. Before *: market@instrument; quantity units depend on market and contract. | 2267 |

### Parsing times and numbers

```python
from datetime import datetime, timezone
value_ns = 1754611351173000000  # lcTsNs, preserve as Python int
seconds, nanoseconds = divmod(value_ns, 1_000_000_000)
dt = datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=nanoseconds // 1000)
# datetime keeps microseconds; preserve value_ns for full nanosecond precision.
# Prices and quantities: use decimal.Decimal when exact decimal arithmetic matters.
```

For Tardis fields, refer to the [official CSV schema](https://docs.tardis.dev/downloadable-csv-files). Other datasets follow their sampled source schemas.

## Python · Query your research environment

Read the key from an environment variable only. This example checks permissions and profiles without creating paid jobs.

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

[Quantitative computing](https://datapanel.dev#compute)

## Six plans for quantitative research compute

One subscription connects research data, CPU/GPU compute and private artifacts. Compute credits reset Friday at 16:00 (UTC+8).

| Plan | Price · USDT / month | Research environment | Weekly compute credits |
| --- | --- | --- | --- |
| New-user trial | 0 | Compute beside licensed research data | 50 |
| Education | 59.94 | Compute beside licensed research data | 1,450 |
| Standard | 99.9 | Compute beside licensed research data | 2,400 |
| Professional | 299.9 | Compute beside licensed research data | 7,200 |
| Enterprise | 999.9 | Compute beside licensed research data | 25,000 |
| Unlimited | 9999.9 | Compute beside licensed research data | No cumulative credit cap |

1 credit equals one allocated CPU unit-hour, including 2 GiB RAM per unit. Extra RAM costs 0.05 credits per GiB-hour. GPU rates vary by model; review the quote before submission.

Credits are issued weekly without rollover. Billing uses allocated resources and verified runtime; queuing is free. Check your account and quote for profiles, permissions and budgets.

One 30-day trial, bound to one IP on first use. Education eligibility requires review.

Unlimited plans still follow per-job resource, duration, concurrency, fair-queue and abuse-prevention rules. Cluster totals are not dedicated resources for one account.

Each private source or result export must be smaller than 1 GB. Plans allow 30 / 120 / 120 / 300 / 600 / 1200 request weight per minute. Response headers report remaining weight and reset time. GB/TB are decimal.

See your account for payment options and entitlements.

[Free trial / account](https://datapanel.dev/account?lang=en)

Promotion limits: trial 1 task / 1 GPU; education 4 / 1; standard 8 / 2; professional 16 / 3; enterprise and unlimited 16 / 4. Task counts include CPU and GPU jobs; GPU limits are included, not additional. Execution depends on authorized profiles, shared capacity and Slurm queueing.

## Quantitative computing

Organize predictions, features, models and reproducible validation through a unified API.

### Prediction-driven parameter search

Upload a standard prediction file, choose instruments and dates, and prepare parameter-search and backtest plans. Keep signal-generation logic locally.

### Custom features and models

Define features, labels and models in code, bind versioned data snapshots, resources and budgets, and keep experiment inputs and outputs traceable.

### Reusable private artifacts

Code, predictions and sealed results belong to your account. Retrieve private assets with your API key; every download checks authorization. Each export must be under 1 GB.

Check profiles, permissions and budgets before submission. Reserve credits, queue work, track status through the API and retrieve results. Quotas, concurrency and time limits bound resource use.

### Rigorous backtesting and cross-checks

The underlying C++ engine implements tick-event replay and latency-aware matching. Dual-engine parity checks are under development to compare execution assumptions and results against an independent reference.

Combine time-based splits, out-of-sample evaluation, prediction-availability checks and data versioning to reduce simulation error, overfitting and look-ahead risk. Engine agreement does not establish strategy validity or guarantee live returns.

Multi-input integration and accounting consistency have been checked on synthetic minute data. Real-tick execution fidelity and dual-engine parity require separate acceptance.

### Prediction-file format

Prediction files contain the instrument, UTC millisecond timestamp, availability time and value. Declare prediction semantics and bind the actual data snapshot.

```
symbol,timestamp_ms,available_at_ms,prediction
BTCUSDT,1767225600000,1767225600000,0.25
```

The sample uses target_fraction: 0.25 means a 25% target position. return_bps means predicted return in basis points; the two semantics are not interchangeable. Backtest validation does not establish profitability or live-trading qualification.

### Your research assets stay yours

Ownership checks, encrypted source storage, authenticated private downloads and administrative auditing protect research assets. Public catalogs contain no user code, predictions or models.

### Use with Claude or Codex

Have your coding assistant read the SDK and API docs. Keep the key in a local environment variable. Check data, permissions and budgets before submitting and verifying results.

Example prompt: Read the Datapanel SDK and load the API key from an environment variable. Check available data, permissions and quotas, show scope and budget, save the task ID, poll status and verify downloads. Never print the key.

## Rate limits by plan

Each private source or result export must be smaller than 1 GB. Plans allow 30 / 120 / 120 / 300 / 600 / 1200 request weight per minute. Response headers report remaining weight and reset time. GB/TB are decimal.

Use the API to check compute profiles and budgets, submit jobs and retrieve your own results.

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 119
X-RateLimit-Reset: 1790294460
X-RateLimit-Window: 60
X-RateLimit-Scope: key
X-Request-Weight: 1
```

Reset: Unix timestamp (UTC seconds). Scope: key / account / downloads / compute. Retry-After: seconds until a rejected request may retry. Windows start on first request; this is separate from Friday 16:00 UTC+8 weekly quota resets.

## Swagger · Interactive API explorer

Use the API to check compute profiles and budgets, submit jobs and retrieve your own results.

Interactive requests use your account permissions and consume applicable quotas. Read the API contract first and protect your key; refreshing clears the entered key.

## AI Quant Workbench

After signing in, describe your research goal. AI can read the official guide, SDK, demos, your data catalog, profiles and credits, and search public sources. Datapanel private AI processes conversations and research context without automatic cloud fallback; public search sends only search terms to a separate search provider; never include credentials or unauthorized strategies.

Ask AI to read the demo and verify fields and time splits. Review a complete Python script in the task editor, select available data and profile, then inspect the quote and confirm submission. Quotes do not execute code; submission reserves credits. Keep the job ID, check status and export private results after success. Browser downloads verify SHA256 and are limited to 128 MiB; use the SDK for larger results.

[Open AI Workbench](https://datapanel.dev/workbench.html) · [文档与 SDK 示例索引](https://datapanel.dev/ai-resources.json) · [下载研究 Skill](https://datapanel.dev/datapanel-research-skill.md)
