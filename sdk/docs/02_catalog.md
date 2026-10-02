# 02 · 发现可用数据

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 帮我寻找 BTCUSDT 的逐笔成交数据，分页列出实际发布的时间分区，不假设其他市场已经可用。

## 本地运行

```bash
python examples/02_catalog.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/catalog/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

先用 `search_catalog` 查询一个小页面，再按 offset 续读；Python 场景演示有上限的分页。达到页数上限时标记 truncated，不能声称完整目录。

## 输入与前提

只使用真实目录返回的 market/data_type/symbol。

## 预期交付

items、页数和 truncated；每个分区包含市场、类型、品种、[start,end)、格式及字节数。

## 状态变化与失败处理

无外部写入。默认 mock 的 demo-exchange 和日期是合成值，不能照抄到 live。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
