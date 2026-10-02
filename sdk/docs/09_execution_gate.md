# 09 · 执行开关与诚实降级

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 检查算力是否真的允许执行。如果未开放，就保留方案并说明阻塞，不重复提交或绕开 API。

## 本地运行

```bash
python examples/09_execution_gate.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/execution-gate/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

读取 `/v1/compute/profiles` 的 execution_enabled/execution_open；场景始终不 POST jobs。Python guarded_submit 额外演示调用前闸门。

## 输入与前提

无需作业 ID。

## 预期交付

execution_closed 或 execution_available、submitted=false。

## 状态变化与失败处理

无外部写入。此场景通过表示正确遵守开关，不表示执行能力已通过验收。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
