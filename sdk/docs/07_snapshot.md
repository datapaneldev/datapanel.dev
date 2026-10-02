# 07 · 冻结数据选择

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 把选定市场、品种和时间范围冻结为我的研究数据快照，后续报价只引用这个快照 ID。

## 本地运行

```bash
python examples/07_snapshot.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/snapshot/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

从授权公开目录选择完整范围，调用 `/v1/compute/data-selections`。保存 dataset_snapshot 资产 ID 与哈希。

## 输入与前提

需 --selection 和 --allow-writes；目录范围有缺口时服务端会拒绝。

## 预期交付

sealed 数据选择快照元数据。

## 状态变化与失败处理

创建快照元数据，不拷贝行情到本机。快照哈希是服务端清单身份，不应当作单个下载文件的 SHA256。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
