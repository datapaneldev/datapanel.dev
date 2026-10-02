# Datapanel · 사용자 가이드

[Live documentation](https://datapanel.dev/developers.html?lang=ko)

## GitHub

[datapaneldev/datapanel.dev](https://github.com/datapaneldev/datapanel.dev)

```
git clone git@github.com:datapaneldev/datapanel.dev.git
```

## 자주 쓰는 연구 프롬프트

키워드를 입력하고 Tab으로 완성하거나 목록에서 선택하세요. 자동 전송이나 실행은 하지 않습니다.

7:3은 시간순 학습/검증 분할입니다. 독립 OOS를 별도로 남기고 5분 라벨에 맞게 경계 purge/embargo를 적용하세요. 목록이 주식이나 주문장 가용성을 보장하지 않습니다. 실제 데이터, 엔진, 비용, 예산과 누락을 확인하고 견적 후 실행을 승인하세요.

### 플랫폼 시작

datapanel.dev의 글을 읽고 기능을 설명해 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=start)

### 주식 데이터 목록

datapanel.dev의 주식 데이터 목록을 확인해 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=stocks)

### 암호화폐 가격·거래량 특성

datapanel.dev의 암호화폐 1분봉으로 가격·거래량 특성을 만들어 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=features)

### MOVR 모델과 이중 백테스트

MOVR/USDT에서 orderbook imbalance와 LightGBM 시계열 모델을 학습해 주세요. 라벨은 5분 미래 수익률, 학습과 검증은 7:3입니다. Python과 C++ 백테스트를 대조하고 OOS 곡선을 보여 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=movr)

### 데이터와 필드 확인

내 계정의 데이터, 종목, 기간, 필드를 확인하고 공개 데이터와 예정 데이터를 구분해 주세요. 실제 데이터 읽기 예제와 특성을 작성할 위치를 보여 주고 누락을 알려 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=schema)

### 병렬 파라미터 탐색

암호화폐 1분봉으로 LightGBM 라벨 주기, 파라미터, seed 병렬 탐색을 설계해 주세요. 시간순 학습/검증과 독립 OOS를 분리하고 OOS 전에 파라미터를 고정하세요. 실험 수, 자원, 견적을 보여 주고 확인 후 제출하세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=search)

### 세 가지 백테스트 대조

자체 백테스트, 플랫폼 Python, C++ 정밀 재생을 대조해 주세요. 신호 시간, 체결 지연, 포지션, 비용, 슬리피지, 펀딩을 통일하고 체결, PnL, Sharpe, 회전율, 낙폭 차이를 설명하세요. 이용 불가 엔진을 표시하세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=compare)

### 안정성과 미래 정보 검사

시간, 특성, 라벨, 체결 순서를 검사해 미래 정보 누출을 찾으세요. 연도, 시장 상태, 비용, 파라미터 변동을 검증하고 실패 실험도 보존하세요. 검증과 독립 OOS를 구분하고 결과를 꾸며내지 마세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=robustness)

### 작업과 결과 추적

내 작업의 대기/실행 상태, 크레딧, 결과를 확인하세요. 실패 원인과 재시도 방법을 설명하고 자동 재제출하지 마세요. 실제 IC, Sharpe, 회전율, 낙폭, OOS와 재현 절차를 설명해 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=jobs)

### 주식 횡단면 팩터 연구

사용 가능한 주식 데이터, 필드, 기간을 확인하고 모멘텀, 반전, 가격·거래량 팩터를 설계하세요. 가격 조정, 거래 정지, 상장 폐지 처리를 설명하세요. 시간순 학습·검증·독립 OOS로 나누고 IC, 그룹 수익, 회전율, 비용 차감 결과를 비교하세요. 누락을 명시하고 견적 후 실행 승인을 기다리세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=stock_factors)

### 여러 모델 학습 비교

동일한 공개 데이터, 특성, 라벨, 시간순 분할로 LightGBM, XGBoost, CatBoost, PyTorch를 비교하세요. 환경과 CPU/GPU를 확인하고 seed와 버전을 기록하세요. 검증에서 선택한 뒤 독립 OOS, 학습 시간, 크레딧 비용을 비교하세요. 계획과 견적을 제시하고 확인 후 실행하세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=model_compare)

### 거래 비용과 용량 분석

실제 신호와 데이터로 수수료, 슬리피지, 체결 지연, 펀딩 변화 및 포지션 규모·거래 참여율별 용량을 분석하세요. 봉 근사와 재생을 구분하고 호가 깊이·체결 데이터 누락의 한계를 명시하세요. 손익분기 비용, 비교, 후속 검증 계획을 제시하고 실행 전에 자원과 견적을 알려 주세요.

[작업실에서 사용](https://datapanel.dev/workbench.html?lang=ko&preset=cost_sensitivity)

# 엔드투엔드 퀀트 리서치 파이프라인

시장 데이터 → 특성 생성 → CPU/GPU 학습 → 예측·백테스트 → 표본 외 검증 → 결과 비교.

허가된 시장 데이터는 플랫폼 안에서 특성 생성·학습·검증에 사용합니다. 실제 버전과 범위는 카탈로그를 확인하세요.

가입 및 이메일 확인 후 API 키로 사양·권한·예산을 확인하고 계산 작업을 제출하세요. 크레딧을 사용하는 요청 전에 계산 가이드를 읽으세요.

[퀀트 컴퓨팅 서비스](https://datapanel.dev#compute)

현재 이용 가능 상태: 이메일 가입 활성화 · USDT 결제 활성화

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

## 검증된 Datapanel 데이터셋

### 전 시장 데이터 서비스

미국 주식 · 홍콩 주식 · 옵션 · 선물 · 외환 · 중국 A주 · 암호화폐

암호화폐 검증 샘플을 제공합니다. 미국·홍콩 주식, 옵션, 선물, 외환, 중국 A주는 도입 중입니다. 종목, 필드 및 신청 가능한 기간은 카탈로그를 확인하세요.

갱신된 카탈로그에는 시장별 대표 샘플이 포함됩니다. 날짜는 검증된 샘플 구간이며 모든 종목의 연속 범위를 뜻하지 않습니다. 신청 가능 범위는 실시간 API를 확인하세요.

시장을 선택해 유형, 샘플 날짜, 종목과 필드를 확인하세요. 공개 카탈로그는 데이터 속성만 표시하며 배포 위치나 저장 경로는 노출하지 않습니다.

2026-09-24T21:25:02.824039+00:00 · 검증 샘플 38개 · 대표 샘플이며 전체 범위가 아닙니다

| 시장 | 데이터 유형 | 형식 / 샘플 수 | 검증 샘플 날짜 | 종목 예시 | Demo |
| --- | --- | --- | --- | --- | --- |
| binance 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| binance_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| binance_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-17 → 2025-09-17 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| bit_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-08-28 → 2025-08-28 관측 날짜 1개, 연속성 미확인 | ada_usdt 목록 종목 1개 | 예제 보기 |
| bit_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-08-28 → 2025-08-28 관측 날짜 1개, 연속성 미확인 | ada_usdt 목록 종목 1개 | 예제 보기 |
| bitget 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| bitget_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-17 → 2025-09-17 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| bitget_spot.um 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-27 → 2025-09-27 관측 날짜 1개, 연속성 미확인 | pepe_usdt 목록 종목 1개 | 예제 보기 |
| bitget_usdt_swap.um 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-27 → 2025-09-27 관측 날짜 1개, 연속성 미확인 | pepe_usdt 목록 종목 1개 | 예제 보기 |
| bitmart 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| bitmart_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-05-21 → 2025-05-21 관측 날짜 1개, 연속성 미확인 | launchcoin_usdt 목록 종목 1개 | 예제 보기 |
| bitmart_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| bybit 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| bybit_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-15 → 2025-06-15 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| bybit_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-17 → 2025-09-17 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| coinex 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| coinex_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-15 → 2025-06-15 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| coinex_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| gate 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| gate_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-15 → 2025-06-15 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| gate_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| hashkey_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-03 → 2025-06-03 관측 날짜 1개, 연속성 미확인 | arb_usdt 목록 종목 1개 | 예제 보기 |
| huobi 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| huobi_spot 검증 샘플 | MBP-20 | csv.gz 파일 1개 | 2025-10-09 → 2025-10-09 관측 날짜 1개, 연속성 미확인 | ada_usdt 목록 종목 1개 | 예제 보기 |
| huobi_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| kucoin 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| kucoin_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-15 → 2025-06-15 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| kucoin_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| mexc_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-08-26 → 2025-08-26 관측 날짜 1개, 연속성 미확인 | h_usdt 목록 종목 1개 | 예제 보기 |
| okx 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| okx_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-06-15 → 2025-06-15 관측 날짜 1개, 연속성 미확인 | a_usdt 목록 종목 1개 | 예제 보기 |
| okx_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| phemex 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| phemex_usdt_swap 검증 샘플 | MBP-20 | csv.gz 파일 1개 | 2025-09-05 → 2025-09-05 관측 날짜 1개, 연속성 미확인 | ach_usdt 목록 종목 1개 | 예제 보기 |
| phemex_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2024-07-22 → 2024-07-22 관측 날짜 1개, 연속성 미확인 | ach_usdt 목록 종목 1개 | 예제 보기 |
| upbit_spot 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-08-19 → 2025-08-19 관측 날짜 1개, 연속성 미확인 | api3_usdt 목록 종목 1개 | 예제 보기 |
| woo 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-01-07 → 2025-01-07 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |
| woo_usdt_swap 검증 샘플 | bbo | csv.gz 파일 1개 | 2025-09-01 → 2025-09-01 관측 날짜 1개, 연속성 미확인 | 1inch_usdt 목록 종목 1개 | 예제 보기 |

## 실제 예제 및 필드 정의

목록에서 데이터셋을 선택하여 실제 헤더와 샘플 행을 확인하세요. 열은 원본 순서이며 미확인 의미는 표시하고 단위를 추정하지 않습니다. null은 0이 아닙니다. JavaScript에서는 ID와 마이크로초·나노초 시각을 문자열 또는 BigInt로 유지하세요.

### binance / bbo

파일 형식: `csv.gz` · 예제 파일: `binance@1inch_usdt@1736214097381000000.csv.gz`

실제 파일의 첫 행 예제이며 전체 데이터 품질 검수를 의미하지 않습니다.

### 예제 데이터

| lcTsNs | exSeq | binance@1inch_usdt*bp | binance@1inch_usdt*bq | binance@1inch_usdt*ap | binance@1inch_usdt*aq |
| --- | --- | --- | --- | --- | --- |
| 1736214097381000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |
| 1736214097393000000 | 0 | 0.4337 | 3367 | 0.4338 | 2267 |

### 필드별 설명

| 필드 이름 | 설명 / 단위 | 예제 값 |
| --- | --- | --- |
| lcTsNs | 로컬 수집/수신 시각, UTC Unix 나노초입니다. 19자리 정수는 Python int 또는 JavaScript BigInt/문자열로 유지하세요. | 1736214097381000000 |
| exSeq | 원본 순번/시간 값이며 시장마다 의미가 다릅니다. 예제에 0이나 19자리 값이 있습니다. 통일된 이벤트 시각으로 취급하지 마세요. | 0 |
| binance@1inch_usdt*bp | 최우선 매수 가격. * 앞은 시장@종목입니다. 수량 단위는 시장 및 계약을 따릅니다. | 0.4337 |
| binance@1inch_usdt*bq | 최우선 매수 잔량. * 앞은 시장@종목입니다. 수량 단위는 시장 및 계약을 따릅니다. | 3367 |
| binance@1inch_usdt*ap | 최우선 매도 가격. * 앞은 시장@종목입니다. 수량 단위는 시장 및 계약을 따릅니다. | 0.4338 |
| binance@1inch_usdt*aq | 최우선 매도 잔량. * 앞은 시장@종목입니다. 수량 단위는 시장 및 계약을 따릅니다. | 2267 |

### 시각 및 숫자 해석

```python
from datetime import datetime, timezone
value_ns = 1754611351173000000  # lcTsNs, preserve as Python int
seconds, nanoseconds = divmod(value_ns, 1_000_000_000)
dt = datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=nanoseconds // 1000)
# datetime keeps microseconds; preserve value_ns for full nanosecond precision.
# Prices and quantities: use decimal.Decimal when exact decimal arithmetic matters.
```

Tardis 필드 정의는 다음을 참조하세요: [공식 CSV 스키마](https://docs.tardis.dev/downloadable-csv-files). 다른 데이터셋은 해당 원본 및 샘플의 정의를 따릅니다.

## Python · 연구 환경 조회

키는 환경 변수에서만 읽습니다. 이 예제는 권한과 사양만 조회하며 유료 작업을 생성하지 않습니다.

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

[퀀트 컴퓨팅 서비스](https://datapanel.dev#compute)

## 퀀트 리서치 연산을 위한 6개 요금제

하나의 구독으로 연구 데이터·CPU/GPU 연산·비공개 결과물을 연결합니다. 계산 크레딧은 금요일 16:00(UTC+8)에 초기화됩니다.

| 요금제 | 가격 · USDT / 월 | 연구 환경 | 주간 연산 크레딧 |
| --- | --- | --- | --- |
| 신규 사용자 체험 | 0 | 허가된 연구 데이터 가까이에서 연산 | 50 |
| 교육 | 59.94 | 허가된 연구 데이터 가까이에서 연산 | 1,450 |
| 표준 | 99.9 | 허가된 연구 데이터 가까이에서 연산 | 2,400 |
| 프로페셔널 | 299.9 | 허가된 연구 데이터 가까이에서 연산 | 7,200 |
| 기업 | 999.9 | 허가된 연구 데이터 가까이에서 연산 | 25,000 |
| 무제한 | 9999.9 | 허가된 연구 데이터 가까이에서 연산 | 누적 크레딧 제한 없음 |

1크레딧은 할당된 CPU 1단위·시간이며 단위당 2 GiB 메모리를 포함합니다. 추가 메모리는 GiB·시간당 0.05크레딧입니다. GPU는 모델별 요금을 제출 전 견적으로 확인하세요.

크레딧은 매주 지급되며 이월되지 않습니다. 할당 자원과 검증된 실행 시간으로 정산하고 대기는 무료입니다. 사양, 권한과 예산은 계정 및 견적을 확인하세요.

최초 사용 IP에 연결되는 1회 30일 체험. 교육 자격은 심사가 필요합니다.

무제한 요금제에도 작업별 자원, 시간, 동시 실행, 공정 대기열 및 오남용 방지 규칙이 적용됩니다. 전체 클러스터를 한 계정이 독점하는 것은 아닙니다.

비공개 코드 또는 결과 내보내기는 건당 1 GB 미만입니다. 요금제별 분당 가중치는 30 / 120 / 120 / 300 / 600 / 1200이며 응답 헤더에 잔여량과 초기화 시간이 표시됩니다. GB/TB는 십진 단위입니다.

결제 방법과 이용 권한은 계정 페이지에서 확인하세요.

[무료 체험 / 계정](https://datapanel.dev/account?lang=ko)

작업 동시 실행 수와 GPU 한도는 현재 요금제, 계정 권한 및 가용 용량에 따라 달라집니다. 견적 전에 최신 계정과 기능 응답을 확인하세요. CPU와 GPU 작업은 계정 작업 한도를 공유합니다.

## 퀀트 컴퓨팅 서비스

예측값, 특성, 모델부터 재현 가능한 검증 결과까지 통합 API로 연구를 구성하세요.

### 예측값 기반 파라미터 탐색

표준 예측 파일을 업로드하고 종목·기간을 지정해 파라미터 탐색과 백테스트 계획을 만드세요. 신호 생성 로직은 로컬에 보관할 수 있습니다.

### 사용자 정의 특성과 모델

코드로 특성, 라벨과 모델을 정의하고 버전 관리된 데이터, 자원 및 예산을 연결해 실험 입력과 결과를 추적하세요.

### 재사용 가능한 비공개 산출물

코드, 예측 및 확정 결과는 본인 계정에 귀속됩니다. API key로 비공개 자산을 가져오며 다운로드마다 권한을 검증합니다. 건별 내보내기는 1 GB 미만입니다.

제출 전 사양, 권한과 예산을 확인하세요. 크레딧 예약 후 대기열에 들어가 API로 상태와 결과를 확인합니다. 한도, 동시 실행 및 시간 제한이 자원 사용을 관리합니다.

### 엄격한 백테스트와 교차 검증

기반 C++ 엔진은 tick 이벤트 재생과 지연을 반영한 체결을 구현합니다. 독립 참조 구현과 체결 가정 및 결과를 대조하는 이중 엔진 검증은 개발 중입니다.

시계열 분할, 표본 외 평가, 예측 이용 가능 시점 확인과 데이터 버전 관리로 왜곡, 과적합 및 미래 정보 누출 위험을 줄입니다. 엔진 결과 일치는 전략의 유효성이나 실거래 수익을 보장하지 않습니다.

합성 분봉 데이터로 다중 입력 연동과 회계 일관성을 검증했습니다. 실제 tick 체결 정확도와 이중 엔진 일치는 별도 검증이 필요합니다.

### 표준 예측 파일

예측 파일에는 종목, UTC 밀리초 시각, 이용 가능 시점과 값이 포함됩니다. 예측 의미를 명시하고 실제 데이터 스냅샷에 연결하세요.

```
symbol,timestamp_ms,available_at_ms,prediction
BTCUSDT,1767225600000,1767225600000,0.25
```

예제는 target_fraction을 사용하며 0.25는 목표 포지션 25%입니다. return_bps는 예상 수익률의 베이시스 포인트로 두 의미를 혼용할 수 없습니다. 백테스트 검증이 수익성이나 실거래 자격을 입증하지는 않습니다.

### 연구 자산은 당신의 연구를 위해

소유권 확인, 소스 암호화 저장, 비공개 다운로드 인증과 관리 감사로 연구 자산을 보호합니다. 공개 카탈로그에 사용자 코드, 예측 또는 모델은 포함되지 않습니다.

### Claude 또는 Codex로 이용

코딩 도우미가 SDK와 API 문서를 읽도록 하고 키는 로컬 환경 변수에 보관하세요. 데이터, 권한과 예산 확인 후 요청하고 결과를 검증하세요.

프롬프트 예: Datapanel SDK를 읽고 환경 변수에서 API key를 가져오세요. 데이터, 권한과 잔여 한도를 확인하고 범위와 예산을 제시한 뒤 작업 ID 저장, 상태 조회 및 다운로드 검증을 수행하세요. 키는 출력하지 마세요.

## 요금제별 요청 제한

비공개 코드 또는 결과 내보내기는 건당 1 GB 미만입니다. 요금제별 분당 가중치는 30 / 120 / 120 / 300 / 600 / 1200이며 응답 헤더에 잔여량과 초기화 시간이 표시됩니다. GB/TB는 십진 단위입니다.

API로 계산 사양과 예산을 확인하고 작업을 제출해 자신의 연구 결과를 받으세요.

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 119
X-RateLimit-Reset: 1790294460
X-RateLimit-Window: 60
X-RateLimit-Scope: key
X-Request-Weight: 1
```

Reset: Unix timestamp (UTC seconds). Scope: key / account / downloads / compute. Retry-After: seconds until a rejected request may retry. Windows start on first request; this is separate from Friday 16:00 UTC+8 weekly quota resets.

## Swagger · 온라인 API 테스트

API로 계산 사양과 예산을 확인하고 작업을 제출해 자신의 연구 결과를 받으세요.

대화형 요청은 계정 권한과 해당 한도를 사용합니다. API 설명을 먼저 읽고 키를 보호하세요. 새로고침하면 입력한 키가 삭제됩니다.

## AI 퀀트 작업실

로그인 후 연구 목표를 설명하세요. AI는 공식 문서, SDK, 예제, 데이터 목록, 사양과 잔액을 읽고 공개 정보를 검색합니다. 대화와 연구 정보는 Datapanel 프라이빗 AI로 처리하며 클라우드 모델로 자동 전송하지 않습니다. 공개 검색어만 외부 검색 서비스로 전송합니다. 인증 정보나 허가 없는 전략을 입력하지 마세요.

예제, 필드와 시간 분할을 확인하고 완전한 Python 코드를 편집하세요. 데이터와 사양을 선택하고 견적 확인 후 제출하세요. 견적은 실행하지 않으며 제출 시 크레딧을 예약합니다. 작업 ID로 상태와 비공개 결과를 확인하세요. 브라우저 다운로드는 SHA256을 검증하며 128 MiB까지 지원합니다.

[AI 작업실 열기](https://datapanel.dev/workbench.html) · [文档与 SDK 示例索引](https://datapanel.dev/ai-resources.json) · [下载研究 Skill](https://datapanel.dev/datapanel-research-skill.md)
