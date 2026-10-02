# 05 · 增量补齐计划

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 根据已完成研究输入的分区 ID，只规划待处理数据，不自动提交计算，也不要把失败的分区标记完成。

## 本地运行

```bash
python examples/05_incremental.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/incremental/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

读取当前场景工作目录 completed.json（已校验 ID 的列表），与分页目录做集合差；没有检查点时全部列为待处理。

## 输入与前提

只有对应快照的研究处理已完成且结果可核验后，才将分区 ID 写入 completed.json；目录可见不等于处理完成。

## 预期交付

pending 分区和目录 truncated 状态。

## 状态变化与失败处理

规划阶段无外部写入。此示例不注册定时任务，不推进水位；实际调度由调用者决定。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
