# 双卡 DDP：条件示例与使用限制


当前固定 GPU 模板只支持单卡。`examples/training/multi_gpu_model.py` 是条件性 DDP 程序；只有平台明确发布兼容的双卡资源、启动方式与账户授权后才能使用。单卡报价或训练成功不能证明双卡可用。

## 需要平台确认的运行协议

此程序提出的目标协议是：**单节点、两张实际分配的 GPU、两个 spawn 子进程、NCCL、同一受控输出目录内的新 FileStore**。它不是当前已发布的 DataPanel 合同。平台明确支持的 GPU 运行环境与启动方式后，必须按实际协议适配，再提交小预算任务。

DDP 每进程绑定一张设备；输入分片由程序显式完成。NCCL 的文件会合方式不代表所有通信都不使用网络。平台仍需验证本地 collective transport、共享内存、进程限制和 CUDA 设备隔离。每次使用新临时文件目录，避免复用 rendezvous 状态。实现依据：[PyTorch DDP](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)、[分布式初始化与后端说明](https://docs.pytorch.org/docs/stable/distributed.html)。

## 程序准备检查什么

| 证据 | 通过条件 | 不能替代的外部证据 |
|---|---|---|
| 资源准入 | 实际公布的 profile 恰好两张 GPU；执行开关开启；账户允许该 profile 和 `train` | 平台实际分配了两张物理卡，而非共享同卡或未声明的 MIG 分区 |
| 进程和设备 | rank 0/1、不同 PID、不同 CUDA UUID、可见设备数为 2 | 平台实际分配与使用的资源信息 |
| 样本分片 | `rank, rank+2, …`，无补齐、无重复、总覆盖全部训练样本；保存每 rank 索引摘要 | 数据快照确实按声明范围物化 |
| 不等长分片 | local squared-error sum × world_size / N；DDP 平均后等于全局均值目标 | NCCL 实际执行成功 |
| 梯度同步 | 第一步归约后梯度与全量数学参考误差 ≤ `1e-9` | 通信超时、设备故障等异常处理 |
| 权重一致 | 两 rank 最终权重摘要一致，参数最大差 ≤ `1e-9` | 取消后 GPU 进程真正退出 |
| 独立数学对照 | DDP 参数与标准库全量批训练差 ≤ `1e-8` | 不构成两个独立回测引擎 |
| 模型导出 | 任务明确指向结果资产；字节哈希通过；权重摘要对应 rank 证据；重载预测一致 | 账单已结算、资源已释放 |

目前两个 rank 的样本索引、进程/设备及误差记录都属于**任务进程自报**。校验器能拒绝缺失、重复或互相矛盾的记录，但无法把自报升级为可信调度器证明。请结合平台返回的任务和资源信息判断，不能仅凭进程自报认定资源已正确分配或释放。

模型仍沿用 CPU 教程的小线性模型：训练段标准化、固定 200 步、时间切分与边界标签剔除。它用于核验分布式执行的正确性，不以两个进程数、训练完成或吞吐作为多卡成功证据，也不宣称有 GPU 加速收益。

## 平台就绪后的命令

先从真实目录准备 `work/selection.json`，并在父进程中设置 API key。以下 profile 是占位符，必须替换为真实已发布且当前账户允许的**两卡**规格：

```bash
python examples/training/multi_gpu_model.py --mode live \
  --selection work/selection.json --work-dir work/two-gpu-live \
  --profile ACTUAL_PUBLISHED_TWO_GPU_PROFILE --allow-writes \
  --wall-seconds 120 --max-credits 1
```

先只报价；用户已授权该次测试且平台合同匹配时增加 `--submit`。无法在 1 积分内报价就停止，不自动扩大预算。不会用 CPU、单 GPU 或四卡 profile 代替请求的两卡。默认离线运行返回 `blocked`，不会制造两卡成功结果。

续接时使用同一运行目录和幂等键；不得通过删除 `run.json` 重复提交。创建作业前保存完整请求；`enabled_profiles` / `enabled_kinds` 存在时严格按列表准入，空列表不表示全部允许。旧 API 未提供这些字段时仍检查执行开关与资源规格；服务端是最终准入依据。

## 使用范围

使用前确认账户允许相应双卡规格和 `train` 类型，且平台明确支持这份程序需要的启动协议。固定 GPU 模板的输入与报价见 [中文说明](gpu-template.zh-CN.md)，它只支持单卡。

完成计算不代表模型有样本外预测能力；此示例不评估样本外投资表现或实盘适用性。
