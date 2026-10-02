# Train your first model with your own features

You will select a short order-book interval, calculate four features, train a CPU model and download its JSON parameters. You need Python 3.10+ and this example project. Live training also requires your own DataPanel API key, execution access and credits.

For a detailed walkthrough, see the [Chinese tutorial](custom-features.zh-CN.md).

## Install and try locally

From the project root, install the package in your Python environment:

```bash
python -m pip install -e ".[dev]"
python examples/training/cpu_model.py --features examples/training/custom_features.py --work-dir work/my-first-model
```

This uses synthetic data on your computer, without network access or platform charges. Open `work/my-first-model/outputs/result.json` to see four model weights, feature names and evaluation metrics.

## Write your features here

Edit [examples/training/custom_features.py](../examples/training/custom_features.py):

- `FEATURE_INPUT_FIELDS` lists the market columns you need.
- `FEATURE_NAMES` names your output features in order.
- `build_features(previous, current)` calculates one finite number per feature from the previous and current order-book observations.

The example calculates midpoint return, spread, level-one imbalance and level-two imbalance. Add a field declaration, feature name and return value together when adding a feature. This demo supports up to 32 features.

MBP-20 supplies `Bp1`–`Bp20` (bid prices), `Ap1`–`Ap20` (ask prices), `Bq1`–`Bq20` and `Aq1`–`Aq20` (corresponding sizes), plus `lcTsNs` for timestamp ordering. Native size units are unconfirmed. `exSeq` is not a supported feature input. There are no OHLC, trade volume or funding columns in this format. See the [field reference](market-fields.md).

The target is the next observation's midpoint return in bps, not a fixed one-second return. Do not include future observations or the target in your features. The model fits scaling on the training segment only.

## Select data and request a quote

Set `DATAPANEL_API_KEY` privately in your terminal environment; do not put it in source files. Check your account and catalog:

```bash
datapanel-demo account --mode live
datapanel-demo catalog --mode live
```

Edit [selection.mbp20.json](../examples/training/selection.mbp20.json) using available market, symbol and UTC dates. Choose 120–5,000 observations for this small example. Prepare inputs and a quote without starting training:

```bash
python examples/training/cpu_model.py --mode live --selection examples/training/selection.mbp20.json --features examples/training/custom_features.py --work-dir work/my-live-model --profile cpu-small --allow-writes --wall-seconds 120 --max-credits 1
```

This creates private planning assets. Review the quote, then run the same command with `--submit` appended to start training. The credit limit caps the quote you accept; the wall limit applies to this introductory job.

If polling ends while the job is pending, rerun the same command with the same directory to continue. Keep `run.json`; removing it may lose the ability to resume safely. Use a new directory when changing code or the data selection.

## Retrieve and use your model

On success, the downloaded model is `work/my-live-model/result.json`. The workflow checks file integrity automatically. To verify and calculate a saved example prediction:

```python
import json
from pathlib import Path
from datapanel_agent.training import verify_model
from datapanel_agent.training_program import predict

path = Path("work/my-live-model/result.json")
print(verify_model(path)["status"])
result = json.loads(path.read_text(encoding="utf-8"))
print(predict(result["model"], result["reload_probes"][0]["x"]))
```

For new observations, compute features with the same function and order used during training. `predict` applies the saved scaler; do not scale the inputs a second time. The output is a predicted return in bps, without fees or execution logic. Compare validation performance with the baseline before considering further research.
