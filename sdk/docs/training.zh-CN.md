# 从行情字段到可下载模型

[English](training.md) · [场景导航](scenario-index.md)

这组示例把模型训练拆成可检查、可恢复的步骤。CPU 模型只依赖 Python 标准库；单 GPU 分支使用平台预装的 PyTorch/CUDA，同样输出可读的 JSON 权重。它们共享数据、特征、标准化和评估口径。


先审查 [用户特征编辑入口](custom-features.zh-CN.md) 和 [实际 82 列字段表](market-fields.md)。默认是三特征，`--features examples/training/custom_features.py` 会显式读取第二档字段并训练四维模型。

```mermaid
flowchart LR
  A[用户选择的行情快照] --> B[字段与时间检查]
  B --> C[因果特征与下一观察标签]
  C --> D[时间切分及边界剔除]
  D --> E[只在训练段拟合标准化]
  E --> F[CPU 或真实单 GPU 训练]
  F --> G[验证与样本外预测误差]
  G --> H[result.json 私有导出]
  H --> I[哈希检查与权重重载]
```

## 先在本机理解流程

完成主 README 的安装后运行：

```bash
python examples/training/cpu_model.py --work-dir work/cpu-fixture
```

这是一个 600 行合成盘口的微型工程 fixture，无网络、无 API key、无积分消费。执行的是仓库生成的单文件源码；下载的用户源码不会被执行。输出在 `work/cpu-fixture/outputs/result.json`，验证摘要在 `verification.json`。

你可以直接阅读权重、偏置、标准化参数、三个时间段的误差以及三个重载探针。改善预测误差只说明模型学到了合成数据规律，不代表市场收益。

## 模型做了什么

| 环节 | 明确口径 |
|---|---|
| 输入 | 一次只选一个市场、品种、时间段；递归读取平台只读目录下的 CSV / CSV.GZ |
| 必需字段 | `lcTsNs`（UTC 纳秒）、`Bp1`、`Ap1`、`Bq1`、`Aq1` |
| 校验 | 有限数、正价格、不交叉盘口、非负数量、严格递增时间；再次筛选 `[start,end)` |
| 特征 | 上一观察到当前的中价变化 bps、当前点差 bps、第一档数量不平衡 |
| 标签 | 当前中价到下一观察中价的变化 bps；这是不等间隔事件预测，不能解释成固定秒数收益 |
| 切分 | 按时间顺序 60% 训练、20% 验证、20% OOS；丢弃 label_end 触及下一区段的边界样本 |
| 标准化 | 均值/标准差及目标缩放只拟合训练段；零方差下限 `1e-8`，标准化特征截断到 ±10 |
| 模型 | 3 输入、1 输出的线性回归；CPU 为标准库批量梯度下降，GPU 为 `torch.nn.Linear` + SGD |
| 固定训练配置 | 200 步、学习率 0.03、L2 系数 0.001；不按 OOS 指标调参或选择模型 |
| 评估 | 每段样本数、时间范围、MSE（bps²）与零预测基线；保留差于基线的结果 |
| 导出 | JSON 权重、特征顺序、scaler、配置、输入哈希、指标和有限重载探针；不使用 pickle |

至少需要 120 行观察。所选行最多 5,000，扫描最多 500,000 行；超过上限直接报错，请缩小选择。不得默默截断数据后仍声称覆盖整个请求范围。重复时间戳也会拒绝，需要明确的聚合规则后再另行扩展。

## 通过公开 API 运行 CPU 训练

先用 `datapanel-demo catalog --mode live` 获取当前可用分区。将一个真实的短区间保存成 `work/selection.json`：

```json
{
  "market": "从真实目录选择",
  "data_type": "MBP-20",
  "symbol": "从真实目录选择",
  "start": "2025-01-01T00:00:00Z",
  "end": "2025-01-01T00:01:00Z"
}
```

以上不是可直接提交的真实选择。日期也必须替换为目录实际覆盖的一段；不要复制示意内容发起作业。密钥通过父进程环境变量 `DATAPANEL_API_KEY` 提供，不写进命令参数、源码或 Git。

先只上传源码、冻结快照和报价：

```bash
python examples/training/cpu_model.py --mode live \
  --selection work/selection.json --work-dir work/cpu-live \
  --allow-writes --profile cpu-small --wall-seconds 120 --max-credits 1
```

确认报价后，增加 `--submit`：

```bash
python examples/training/cpu_model.py --mode live \
  --selection work/selection.json --work-dir work/cpu-live \
  --allow-writes --submit --profile cpu-small --wall-seconds 120 --max-credits 1
```

已获当前任务执行授权时无需重复询问。`--max-credits` 是本次任务报价上限，不是账户全部可用积分。平台按实际资源分配结算；排队与完成状态不能代替最终账单。现有授权不意味着可以无限重试或扩大训练规模。

平台启动 Python 时提供 `DP_INPUT_DIR` / `DP_OUTPUT_DIR`，唯一结果文件为 `result.json`。源码不安装包、不访问网络、只使用文档约定的输入输出目录。平台负责排队执行。

## 恢复和模型下载

`run.json` 会逐步保存源码、快照、报价，以及**在提交之前**落盘的作业请求和幂等键。API origin、账户摘要、配置和源码哈希都绑定到同一运行目录。

- 输出 `RUNNING` / `QUEUED` 等状态时，重复同一命令和目录继续轮询；不会重新提交已知任务。
- POST 响应丢失时保留相同请求和幂等键；不要删除目录或换新键再试。
- 报价过期又无法确认提交是否成功时，先核对原任务状态，不自动刷新报价重新申请预算。
- `FAILED` / `CANCELLED` / `TIMED_OUT` / `EXPIRED` 保留终态，不伪装为完成。
- `SUCCEEDED` 后只使用该任务返回的 `result_artifact_id`，并检查其属于 `output_artifact_ids`。映射缺失即停止，绝不选“资产列表最新一项”。
- 通过现有私有导出接口下载、核验大小和 SHA256，再按 JSON 权重重算探针。过程不会执行下载的 Python 或 pickle。

每次默认最多轮询 12 次、间隔 5 秒。轮询结束不是取消；任务仍可能在运行，应保留目录继续查询。需要取消时使用 [任务管理](10_job_lifecycle.md)，直到终态、资源释放和计费对账完成。

## GPU 入口：条件执行，不回退

```bash
python examples/training/gpu_model.py --mode live \
  --selection work/selection.json --work-dir work/gpu-live \
  --profile 实际发布的单GPU规格 --allow-writes --submit \
  --wall-seconds 120 --max-credits 1
```

必须先确认平台公开了真正包含一张 GPU 的 profile，且运行镜像预装兼容的 PyTorch/CUDA。`cpu-small` 不可充当 GPU profile；没有 CUDA、可见 GPU 数不符或未开放执行都会明确失败，不回退到 CPU。这个三参数模型适合验证运行链路，不用于展示 GPU 性能优势。

输出记录 PyTorch/CUDA 版本、设备名称、可见 GPU 数与 `device=cuda:0`。它们属于进程自报，最终验收仍须结合平台的实际 GPU 分配与释放证据。**当前尚未运行 GPU 数值与硬件验收；离线测试只验证缺少 GPU 时会拒绝执行。** 多卡另有 [双卡 DDP 条件程序与验收清单](multi-gpu.md)，仍待平台资源和运行合同，不把单卡示例当多卡。

## 给 Codex 的提示词

> 使用本仓库 CPU 训练入口，先读取账户、profiles 和数据目录。只选择具有明确 level-one book 字段的小区间，冻结选择与 1 积分预算，硬时限 120 秒。用户已授权本次执行时提交一次，保留幂等键和所有失败状态。检查真实任务输出映射，下载 JSON 模型并核验哈希与重载预测。报告样本外误差和基线、账单状态及限制。执行尚未开放就停止提交并反馈给平台，不替换为本机训练宣称远端成功。

现有 12 个 MCP 工具仍不提供作业提交能力；Codex 可调用上述明确的 CLI。原路线图中的 OOS NPY/索引、独立双回测对拍、真实多卡和平台隔离 OOS 尚未完成。所有结果保持 `RESEARCH_UNQUALIFIED`。
