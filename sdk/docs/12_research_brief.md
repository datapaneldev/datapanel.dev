# 12 · 生成可审查研究简报

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 整理一份研究数据简报：可用数据、缺口、算力能力、证据边界和下一步；没有 OOS 证据就明确未资格化。

## 本地运行

```bash
python examples/12_research_brief.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/research-brief/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

组合目录、覆盖审计和 profile 只读接口，生成 Markdown 简报及结构化证据。输出只包含观察结果与后续验证要求。

## 输入与前提

不需要真实策略；mock 仅包含合成目录。

## 预期交付

research-brief.md 和 qualification=RESEARCH_UNQUALIFIED 的结果。

## 状态变化与失败处理

无外部写入，只写本地报告。不生成虚构收益、夏普、训练完成或双引擎一致性结论。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
