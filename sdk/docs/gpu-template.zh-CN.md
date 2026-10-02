# 固定 GPU 模板：离线准备输入

你可以离线生成并检查 `mlp-regression-v1` 输入，也可以使用自己的账户上传输入、获取固定模板报价。GPU 使用独立 API；通用 CPU 规格不代表此入口的权限。模板要求恰好一张 CUDA GPU，不支持多卡，不回退 CPU。

本示例的在线命令止于报价，不启动训练。收到 403/503 时检查账户授权或稍后重试，不修改资源名称绕过限制。

## 先运行可复现示例

在仓库根目录安装 `pip install -e '.[dev]'`，然后运行：

```bash
python examples/training/prepare_gpu_template.py --output work/gpu-template-first
```

选择新的输出目录。示例生成 64 行**合成数据**，没有训练任何模型。`input.json` 是严格模板输入；`audit.json` 单独记录特征顺序、时间边界、输入 SHA256 和资格状态，不属于 API 请求。

## 校验已有输入文件

对自己生成的文件运行只读校验：

```bash
python examples/training/prepare_gpu_template.py --validate work/gpu-template-first/input.json
```

成功时输出 `INPUT_VALID_OFFLINE_ONLY`、文件 SHA256、字节数、行数与列数，退出码为 `0`。校验不联网、不改写文件；它只验证输入格式与数值限制，不能单独验证时间边界或证明 GPU 已运行。时间边界检查由下方导出函数完成。

| 错误 | 如何处理 |
|---|---|
| 输出目录已存在 | 换一个尚不存在的目录；已有输出不会被覆盖 |
| 非法 JSON 或重复键 | 修正 JSON 编码与重复字段，然后重新校验 |
| 超过 2 MiB | 缩小明确选择的数据范围或特征数 |
| 标签跨越验证边界 | 按冻结的时间边界剔除重叠样本，重新检查 80/20 切分 |

失败时退出码为 `2`，不会将输入文件内容打印到终端。若写盘因磁盘空间或权限失败，可能保留不完整目录；排查后使用新的目录重新导出。

## 换成自己的 CPU 特征

在 [用户特征教程](custom-features.zh-CN.md) 指定的模块内实现因果特征。CPU 代码完成字段读取及特征计算后，将二维 Python 数值列表 `features`、一维 `labels` 交给 `datapanel_agent.gpu_template.export_features`。同时提供 `feature_names`、整数时间列表 `timestamps` 和每个标签的结束时间 `label_end`；时间必须使用同一时钟与单位。

导出器拒绝训练标签触及验证首行时间。它使用模板实际的 `floor(4N/5)` 切分点，**不会自动删行或截断**。需要 purge 时，由调用者按预先冻结的数据边界构造样本，再重新验证实际切分点。时间检查不能证明特征没有使用未来数据；用户仍须审查特征逻辑。不要先用全样本标准化，模板会仅用前 80% 拟合均值及样本标准差，标准差下限为 `1e-6`。

## 合同边界

| 项目 | 限制 |
|---|---|
| 编码大小 | UTF-8 JSON ≤ 2 MiB，实际编码后检查 |
| 数据矩阵 | 32..16384 行，1..128 列，每行等宽 |
| 特征与标签 | 有限数，范围 ±1,000,000；拒绝布尔值 |
| 模型 | 1..4 个隐藏层，每层 1..256，总参数 ≤ 32768 |
| 训练 | epochs 1..200，batch_size 8..1024 |
| 参数 | learning_rate 0.000001..0.1，seed 0..2147483647 |
| 时限 | wall_seconds 1..120 |

拒绝未知字段、重复 JSON 键、代码、路径或回调参数。最大行数与最大列数不意味着能同时满足 2 MiB 限制。输入大小超限时缩小明确的数据选择，不能静默裁剪。

固定网络为 Linear/ReLU 隐藏层及线性输出，使用 Adam 和 MSE；后 20% 仅是 validation，**没有独立 OOS、预测 NPY 或双回测验收**。计划输出 `model.json` 使用 `datapanel-mlp-json-v1` 格式，包含网络权重与标准化参数；这不是已有 CPU 线性模型格式，不应交给旧的 CPU 模型验证器。实际任务结果从专用任务状态查询，随后通过私有产物接口取回；报价本身不会产生模型。


## 上传并获取报价

先配置环境变量 `DATAPANEL_API_KEY`，再执行：

```bash
python examples/training/prepare_gpu_template.py --quote work/gpu-template-first/input.json --allow-writes --max-credits 1 --work-dir work/gpu-quote-first
```

此命令会上传数值特征与标签，创建私有输入资产与报价。请确认这些数据可以上传。它不会提交 GPU 训练；成功输出 `submitted=false`。`gpu-plan.json` 保存输入哈希和报价，重复运行复用已有记录；已有报价可能过期，不能直接当作可执行承诺。

若 POST 超时，流程保存未知状态并停止自动重传。先核查账户内资产与报价，避免重复上传。改变数据、账户或预算时使用新的目录。模型输入上限是合同最大值，实际账户可能有更短时限或更小资源范围。

需要自行集成任务提交时，请按 [公开合同](api-contract.md) 使用 `DataPanel.gpu_submit`、`gpu_status`、`gpu_cancel`；提交前保存请求体与稳定幂等键。通用 `submit_job` 不适用于固定 GPU 模板。
