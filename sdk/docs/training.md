# CPU and conditional GPU model training


The CPU demo is a standalone, standard-library training program. It reads a selected level-one order book, creates causal features, purges labels across chronological split boundaries, fits scaling on training data only, trains a linear model and exports readable JSON weights. The conditional single-GPU implementation uses the same data and optimization objective with a platform-provided PyTorch/CUDA runtime.


Start with [editable user features](custom-features.md). Input dimension follows the declared feature list; the default is three features and the supplied custom example uses four, including the second book level.

## Try it offline

```bash
python examples/training/cpu_model.py --work-dir work/cpu-fixture
```

This runs a small deterministic 600-row synthetic fixture in a subprocess. It needs no key, network, remote resources or paid credits. Read `outputs/result.json` for weights, scaler, time splits, MSE against a zero-prediction baseline and three reload probes. `verification.json` records the downloaded-format reload check. Synthetic prediction gains are not trading performance.

## Run through DataPanel

Use the authenticated catalog to write a real, small selection to `work/selection.json`; use the selection schema from the [live guide](live-guide.md). Set `DATAPANEL_API_KEY` securely in the parent environment. First plan:

```bash
python examples/training/cpu_model.py --mode live \
  --selection work/selection.json --work-dir work/cpu-live \
  --profile cpu-small --allow-writes --wall-seconds 120 --max-credits 1
```

Add `--submit` when this job is authorized. Planning writes private source/snapshot/quote assets but does not submit a job. Execution checks the current service gate; it never bypasses it. Repeat the same command and work directory to resume. An unfinished polling response is not a cancellation or successful training result.

The persisted manifest binds the API origin, account fingerprint, selection, source hash, resources and budget. The submission body and idempotency key are saved before POST. Ambiguous responses reuse that key; changed configuration/account is rejected. Do not delete the manifest to retry. Expired quotes require reconciliation before preparing another task.

The platform supplies read-only `DP_INPUT_DIR` and writable `DP_OUTPUT_DIR`, runs your Python source in an isolated environment, and seals `result.json`. A successful task must explicitly map `result_artifact_id` into `output_artifact_ids`. The demo exports that exact asset, verifies bytes/SHA256 and recomputes probes from JSON parameters without executing downloaded code. Job completion and model integrity are reported separately from billing settlement.

## Data and model contract

- Required CSV/CSV.GZ columns: `lcTsNs` (UTC nanoseconds), `Bp1`, `Ap1`, `Bq1`, `Aq1`. Reject non-finite/crossed/invalid books and repeated timestamps; reapply `[start,end)` after platform staging.
- At least 120 observations; at most 5,000 selected rows and 500,000 scanned rows. Oversize inputs fail, never silently truncate.
- Features: previous-to-current midpoint return in bps, spread in bps and current level-one quantity imbalance. Label: next-observation midpoint return in bps, not a fixed-duration return.
- Chronological 60/20/20 split; remove labels touching the next segment. All feature/target scaling uses only training samples. Features are clipped to ±10 standardized units; zero-variance floor is `1e-8`.
- Linear 3→1 model, 200 full-batch gradient steps, learning rate 0.03, L2 coefficient 0.001. Hyperparameters are fixed before OOS evaluation. Preserve negative results.
- Export JSON contains model/scaler, schema, bounded reload probes, configuration, input hash and segment metrics. No pickle; no full prediction export or backtest claim. The same process can see all inputs, so this is not platform-isolated OOS qualification.

## Conditional single-GPU entry

```bash
python examples/training/gpu_model.py --mode live \
  --selection work/selection.json --work-dir work/gpu-live \
  --profile ACTUAL_PUBLISHED_SINGLE_GPU_PROFILE --allow-writes --submit \
  --wall-seconds 120 --max-credits 1
```

The profile must advertise one real GPU and the platform must provide compatible PyTorch/CUDA. No package installation or CPU fallback occurs. Missing CUDA or an allocation mismatch fails. Running the GPU entry in its default offline mode exits with a documented blocked status; that verifies the guard, not GPU training. This tiny model validates execution plumbing, not GPU speed.

Runtime JSON reports device/library versions. Hardware acceptance additionally needs independent platform allocation and release evidence. Multi-GPU/DDP is deliberately outside this single-device implementation. Existing MCP tools still do not submit jobs; Codex can use the explicit training CLI.

The [conditional two-GPU DDP extension](multi-gpu.md) adds disjoint sample shards, unequal-shard gradient weighting, device/rank reports, synchronization checks and a CPU mathematical reference. Production remains BLOCKED: no GPU profile or runtime contract is available. Offline validator tests do not execute PyTorch/NCCL or establish hardware support.
