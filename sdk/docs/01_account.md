# 01 · 账户与额度

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 先查看我的 DataPanel 套餐、数据额度、积分余额和请求频率限制，不做任何扣费操作。

## 本地运行

```bash
python examples/01_account.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/account/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

只读 `/v1/me` 与 `/v1/compute/usage`。原样保留账本单位；microcredit 除以 1,000,000 才是 credit。套餐未配置值保留 null，不当作零。

## 输入与前提

有效 API key；算力用量要求相应访问权限。

## 预期交付

账户、订阅与算力余额的结构化摘要。

## 状态变化与失败处理

无外部写入。不要根据套餐宣传数推断当前可用余额。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
