# Datapanel · ユーザーガイド

[Live documentation](https://datapanel.dev/developers.html?lang=ja)

## GitHub

[datapaneldev/datapanel.dev](https://github.com/datapaneldev/datapanel.dev)

```
git clone git@github.com:datapaneldev/datapanel.dev.git
```

## よく使う研究プロンプト

キーワード入力後 Tab で補完、または一覧から選択。自動送信・実行はしません。

7:3 は時系列の学習・検証分割です。独立 OOS を別途確保し、5分ラベルに合わせ分割境界を purge/embargo。一覧はデータ利用可能性の保証ではありません。実データ、エンジン、費用、予算を確認し、不足は明記させてください。見積後に実行を確認。

### プラットフォーム入門

datapanel.dev の記事を読み、機能を教えてください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=start)

### 株式データ一覧

datapanel.dev の株式データ一覧を調べてください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=stocks)

### 暗号資産の価格・出来高特徴量

datapanel.dev の暗号資産1分足から価格・出来高の特徴量を作成してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=features)

### MOVR モデルと二重バックテスト

MOVR/USDT で orderbook imbalance と LightGBM の時系列モデルを学習してください。ラベルは5分先リターン、学習と検証は7:3です。Python と C++ バックテストを照合し、OOS 損益曲線を示してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=movr)

### 利用可能データと項目

私のアカウントで利用できるデータ、銘柄、期間、項目を確認し、公開済みと予定を区別してください。実データの最小読み込み例と特徴量を書く場所を示し、不足を明記してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=schema)

### 並列パラメータ探索

利用可能な暗号資産1分足で LightGBM の期間、パラメータ、seed を並列探索してください。時系列の学習・検証と独立 OOS を用意し、OOS 前にパラメータを固定。実験数、資源、見積を示し、確認後に送信してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=search)

### 三つのバックテスト照合

自作、プラットフォーム Python、C++ 回放のバックテストを、信号時刻、遅延、ポジション、費用、スリッページ、資金調達費を統一して照合。約定、PnL、Sharpe、回転率、回撤の差を説明し、使えないエンジンを明記してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=compare)

### 頑健性と未来情報漏洩

時刻、特徴量、ラベル、約定時序を確認し未来情報漏洩を検査。年度、相場状態、費用、パラメータの頑健性を調べ、失敗も残してください。検証と独立 OOS を区別し、結果を捏造しないでください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=robustness)

### タスク状況と結果

自分の待機・実行タスク、クレジット、結果を確認してください。失敗時は原因と再試行方法を示し、自動再送信しないでください。実際の IC、Sharpe、回転率、回撤、OOS と再現手順を説明してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=jobs)

### 株式クロスセクション因子

利用できる株式データ、項目、期間を確認し、モメンタム、反転、価格・出来高因子を設計してください。価格調整、取引停止、上場廃止の扱いを明記。時系列で学習・検証・独立 OOS を分け、IC、分位収益、回転率、費用控除後を比較。不足を明記し、見積後に実行確認を待ってください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=stock_factors)

### 複数モデルの学習比較

同じ公開データ、特徴量、ラベル、時系列分割で LightGBM、XGBoost、CatBoost、PyTorch を比較してください。実行環境と CPU/GPU を確認し、seed とバージョンを記録。検証で選択後、独立 OOS、学習時間、費用を比較。計画と見積を示し、確認後に実行してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=model_compare)

### 取引コストと容量分析

実際の信号と利用可能データで、手数料、スリッページ、約定遅延、資金調達費の影響と、ポジション規模・出来高参加率ごとの容量を分析。足データ近似と回放を区別し、板深度や約定不足を明記。損益分岐費用、比較、検証計画を示し、実行前に資源と見積を提示してください。

[作業室で使用](https://datapanel.dev/workbench.html?lang=ja&preset=cost_sensitivity)

# 定量リサーチの一貫したワークフロー

市場データ → 特徴量 → CPU/GPU 学習 → 予測・バックテスト → アウトオブサンプル検証 → 結果比較。

許諾済み市場データはプラットフォーム内で特徴量・学習・検証に利用します。実際のバージョンと収録範囲はカタログをご確認ください。

登録とメール確認後、APIキーで仕様・権限・予算を確認してから計算ジョブを投入してください。クレジット消費前に計算ガイドをお読みください。

[クオンツ計算サービス](https://datapanel.dev#compute)

現在の公開状況： メール登録 有効 · USDT 決済 有効

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

## Datapanel 検証済みデータセット

### 全市場データサービス

米国株 · 香港株 · オプション · 先物 · 外国為替 · 中国A株 · 暗号資産

暗号資産の検証済みサンプルを掲載しています。米国株・香港株・オプション・先物・外国為替・中国A株は導入中です。銘柄、項目、申請可能な日付はカタログで確認してください。

更新カタログには市場横断の代表サンプルを掲載。日付は検証済み区画を示し、全銘柄の連続網羅を意味しません。申請範囲はリアルタイムAPIに従います。

市場を選択して種別・サンプル日付・銘柄・項目を確認。公開カタログにはデータ属性のみを表示し、配置場所や保存パスは含めません。

2026-09-24T21:25:02.824039+00:00 · 検証済みサンプル 38 件 · 代表サンプル・完全網羅ではありません

| 市場 | データ種別 | 形式 / サンプル数 | 検証済みサンプル日付 | 銘柄の例 | Demo |
| --- | --- | --- | --- | --- | --- |
| binance 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| binance_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| binance_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-17 → 2025-09-17 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| bit_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-08-28 → 2025-08-28 観測日 1 件。連続性は未確認 | ada_usdt カタログ銘柄 1 件 | サンプルを見る |
| bit_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-08-28 → 2025-08-28 観測日 1 件。連続性は未確認 | ada_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitget 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitget_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-17 → 2025-09-17 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitget_spot.um 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-27 → 2025-09-27 観測日 1 件。連続性は未確認 | pepe_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitget_usdt_swap.um 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-27 → 2025-09-27 観測日 1 件。連続性は未確認 | pepe_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitmart 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitmart_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-05-21 → 2025-05-21 観測日 1 件。連続性は未確認 | launchcoin_usdt カタログ銘柄 1 件 | サンプルを見る |
| bitmart_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| bybit 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| bybit_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-15 → 2025-06-15 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| bybit_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-17 → 2025-09-17 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| coinex 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| coinex_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-15 → 2025-06-15 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| coinex_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| gate 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| gate_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-15 → 2025-06-15 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| gate_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| hashkey_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-03 → 2025-06-03 観測日 1 件。連続性は未確認 | arb_usdt カタログ銘柄 1 件 | サンプルを見る |
| huobi 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| huobi_spot 検証済みサンプル | MBP-20 | csv.gz 1 ファイル | 2025-10-09 → 2025-10-09 観測日 1 件。連続性は未確認 | ada_usdt カタログ銘柄 1 件 | サンプルを見る |
| huobi_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| kucoin 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| kucoin_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-15 → 2025-06-15 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| kucoin_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| mexc_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-08-26 → 2025-08-26 観測日 1 件。連続性は未確認 | h_usdt カタログ銘柄 1 件 | サンプルを見る |
| okx 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| okx_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-06-15 → 2025-06-15 観測日 1 件。連続性は未確認 | a_usdt カタログ銘柄 1 件 | サンプルを見る |
| okx_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| phemex 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| phemex_usdt_swap 検証済みサンプル | MBP-20 | csv.gz 1 ファイル | 2025-09-05 → 2025-09-05 観測日 1 件。連続性は未確認 | ach_usdt カタログ銘柄 1 件 | サンプルを見る |
| phemex_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2024-07-22 → 2024-07-22 観測日 1 件。連続性は未確認 | ach_usdt カタログ銘柄 1 件 | サンプルを見る |
| upbit_spot 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-08-19 → 2025-08-19 観測日 1 件。連続性は未確認 | api3_usdt カタログ銘柄 1 件 | サンプルを見る |
| woo 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-01-07 → 2025-01-07 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |
| woo_usdt_swap 検証済みサンプル | bbo | csv.gz 1 ファイル | 2025-09-01 → 2025-09-01 観測日 1 件。連続性は未確認 | 1inch_usdt カタログ銘柄 1 件 | サンプルを見る |

## 実データのサンプルとフィールド定義

棚卸し済みデータの実ヘッダーとサンプル行を確認できます。列は元ファイル順です。未確認の意味は明示し、単位を推測しません。null は 0 ではありません。JavaScript では ID とマイクロ秒・ナノ秒時刻を文字列または BigInt で保持してください。

### binance / bbo

ファイル形式： `csv.gz` · サンプルファイル： `binance@1inch_usdt@1736214097381000000.csv.gz`

実ファイル冒頭の例であり、全データ品質の検収を示すものではありません。

### サンプルデータ

| lcTsNs | exSeq | binance@1inch_usdt*bp | binance@1inch_usdt*bq | binance@1inch_usdt*ap | binance@1inch_usdt*aq |
| --- | --- | --- | --- | --- | --- |
| 1736214097381000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |
| 1736214097393000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |

### フィールド別説明

| フィールド名 | 説明 / 単位 | サンプル値 |
| --- | --- | --- |
| lcTsNs | ローカル受信時刻。UTC Unix ナノ秒の19桁整数を Python int または JavaScript BigInt/文字列で保持します。 | 1736214097381000000 |
| exSeq | ソースの連番・時刻値。市場により意味が異なり、例には0や19桁値があります。共通のイベント時刻とみなさないでください。 | 0 |
| binance@1inch_usdt*bp | 最良買気配価格. * の前は市場@銘柄。数量単位は市場・契約に依存します。 | 0.4337 |
| binance@1inch_usdt*bq | 最良買気配数量. * の前は市場@銘柄。数量単位は市場・契約に依存します。 | 3367 |
| binance@1inch_usdt*ap | 最良売気配価格. * の前は市場@銘柄。数量単位は市場・契約に依存します。 | 0.4338 |
| binance@1inch_usdt*aq | 最良売気配数量. * の前は市場@銘柄。数量単位は市場・契約に依存します。 | 2267 |

### 時刻と数値の解析

```python
from datetime import datetime, timezone
value_ns = 1754611351173000000  # lcTsNs, preserve as Python int
seconds, nanoseconds = divmod(value_ns, 1_000_000_000)
dt = datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=nanoseconds // 1000)
# datetime keeps microseconds; preserve value_ns for full nanosecond precision.
# Prices and quantities: use decimal.Decimal when exact decimal arithmetic matters.
```

Tardis のフィールド定義は次を参照： [公式 CSV スキーマ](https://docs.tardis.dev/downloadable-csv-files)。その他のデータはサンプルと元データの定義に従います。

## Python · 研究環境の照会

キーは環境変数からのみ取得します。この例は権限と仕様の照会のみで、有料ジョブは作成しません。

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

[クオンツ計算サービス](https://datapanel.dev#compute)

## 定量リサーチ計算の6プラン

一つの契約で研究データ、CPU/GPU計算、非公開成果を接続。計算クレジットは毎週金曜16:00（UTC+8）にリセットされます。

| プラン | 料金 · USDT / 月 | 研究環境 | 週次計算クレジット |
| --- | --- | --- | --- |
| 新規ユーザー体験 | 0 | 利用許諾データの近くで計算 | 50 |
| 教育 | 59.94 | 利用許諾データの近くで計算 | 1,450 |
| 標準 | 99.9 | 利用許諾データの近くで計算 | 2,400 |
| プロ | 299.9 | 利用許諾データの近くで計算 | 7,200 |
| エンタープライズ | 999.9 | 利用許諾データの近くで計算 | 25,000 |
| 無制限 | 9999.9 | 利用許諾データの近くで計算 | 累計クレジット上限なし |

1クレジットは割り当てCPU 1単位を1時間利用する料金で、単位あたり2 GiBのメモリを含みます。追加メモリは0.05クレジット/GiB・時間。GPUは型番別料金を申請前に確認できます。

クレジットは週次付与で繰越なし。割り当て資源と検証済み実行時間で精算し、待機時間は無料です。仕様・権限・予算はアカウントと見積もりを確認してください。

初回利用IPに紐づく一度限りの30日体験。教育資格は審査が必要です。

無制限プランにもジョブ資源・時間・同時実行・公平な待機列・不正利用防止の制限が適用されます。クラスタ全体を1アカウントが専有するものではありません。

非公開コード・結果の各エクスポートは 1 GB 未満です。毎分のウェイトはプラン別に 30 / 120 / 120 / 300 / 600 / 1200。残量とリセット時刻はレスポンスヘッダーに表示します。GB/TB は十進単位です。

支払い方法と利用権限はアカウントページをご確認ください。

[無料体験 / アカウント](https://datapanel.dev/account?lang=ja)

プロモーション上限：体験 1 タスク / GPU 1 枚、教育 4 / 1、標準 8 / 2、専門 16 / 3、企業・無制限 16 / 4。CPU・GPU タスクは合算し、GPU 上限は内数です。実行は許可された仕様、共有容量、Slurm の待ち行列に従います。

## クオンツ計算サービス

予測値・特徴量・モデルから再現可能な検証結果まで、統一APIで研究を整理します。

### 予測値によるパラメータ探索

標準予測ファイルをアップロードし、銘柄・期間を指定して探索とバックテストを計画。シグナル生成ロジックは手元に保持できます。

### 独自の特徴量とモデル

コードで特徴量・ラベル・モデルを定義し、版管理されたデータ、資源、予算を紐付け、実験の入出力を追跡可能にします。

### 再利用可能な非公開成果物

コード・予測・確定結果は自分のアカウントに帰属します。API keyで取得し、ダウンロード時に権限を再確認します。1回のエクスポートは1 GB未満です。

申請前に仕様・権限・予算を確認。クレジットを予約して待機列に入り、APIで状態と結果を取得します。枠・同時実行・制限時間で資源を管理します。

### 厳密なバックテストと相互検証

基盤C++エンジンにtickイベント再生と遅延を考慮した約定処理があります。独立した参照実装と約定仮定・結果を照合する二重エンジン検証は開発中です。

時系列分割・アウトオブサンプル評価・予測利用可能時刻・データ版管理で歪み、過学習、未来情報漏洩のリスクを抑えます。エンジン一致は戦略の有効性や実収益を保証しません。

合成分足データで複数入力の接続と会計整合性を検証済みです。実tickの約定精度と二重エンジン照合は別途検証が必要です。

### 標準予測ファイル

予測ファイルには銘柄、UTCミリ秒時刻、利用可能時刻、値を含めます。予測の意味を明示し、実データスナップショットに紐付けてください。

```
symbol,timestamp_ms,available_at_ms,prediction
BTCUSDT,1767225600000,1767225600000,0.25
```

例は target_fraction で、0.25 は目標ポジション25%を意味します。return_bps は予測収益のベーシスポイントで、混同できません。バックテスト検証は収益性や実運用資格を保証しません。

### 研究資産はあなたの研究のために

所有権確認、ソース暗号化保存、私有ダウンロード認証、管理監査で研究資産を保護。公開カタログにユーザーのコード・予測・モデルは含みません。

### Claude・Codex から利用

コーディング支援にSDKとAPI文書を読ませ、キーをローカル環境変数に保存。データ・権限・予算を確認して申請し、結果を検証してください。

プロンプト例：Datapanel SDKを読み、環境変数からAPI keyを取得。データ・権限・残枠を確認し、範囲と予算を示し、タスクIDを保存。状態を照会してダウンロードを検証。キーは出力しない。

## プラン別レート制限

非公開コード・結果の各エクスポートは 1 GB 未満です。毎分のウェイトはプラン別に 30 / 120 / 120 / 300 / 600 / 1200。残量とリセット時刻はレスポンスヘッダーに表示します。GB/TB は十進単位です。

APIで計算仕様と予算を確認し、ジョブを投入して自分の研究結果を取得します。

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 119
X-RateLimit-Reset: 1790294460
X-RateLimit-Window: 60
X-RateLimit-Scope: key
X-Request-Weight: 1
```

Reset: Unix timestamp (UTC seconds). Scope: key / account / downloads / compute. Retry-After: seconds until a rejected request may retry. Windows start on first request; this is separate from Friday 16:00 UTC+8 weekly quota resets.

## Swagger · API オンラインテスト

APIで計算仕様と予算を確認し、ジョブを投入して自分の研究結果を取得します。

対話リクエストはアカウント権限と該当枠を使用します。説明を読みキーを保護してください。再読み込みで入力キーは消去されます。

## AI クオンツ作業室

ログイン後に研究目標を説明してください。AI は公式ドキュメント、SDK、例、データ一覧、仕様、残高を取得し公開情報を検索できます。対話と研究情報は Datapanel のプライベート AI で処理します。クラウドモデルに自動転送せず、公開検索では検索語のみ外部検索サービスに送信します。認証情報や許可のない戦略を入力しないでください。

例と列・時間分割を確認し、Python コードを編集、データと仕様を選択、見積確認後に送信してください。見積は実行せず、送信でクレジットを予約します。タスク ID で状態を確認し、成功後に非公開結果を取得します。SHA256 検証付きブラウザ取得は 128 MiB までです。

[AI 作業室を開く](https://datapanel.dev/workbench.html) · [文档与 SDK 示例索引](https://datapanel.dev/ai-resources.json) · [下载研究 Skill](https://datapanel.dev/datapanel-research-skill.md)
