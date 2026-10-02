# 08 · 有预算上限的算力报价

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 为这份源码和数据申请 cpu-small、60 秒、最多 1 积分的特征计算报价；到报价为止，不启动任务。

## 本地运行

```bash
python examples/08_quote.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/quote/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

先读取资源 profile，上传源码、冻结快照，再 POST quotes。核对 maximum_charged_credits 不超过明确预算，返回可审查的 job_request。

## 输入与前提

需 --selection 和 --allow-writes。用户 API key 需要算力控制面访问权限。

## 预期交付

源码/快照 ID、不可变报价、费率版本、到期时间、计费上限和任务请求体。

## 状态变化与失败处理

创建源码、快照和报价，不运行计算。报价会过期；重新报价不能沿用旧报价 ID。不要把工程 smoke 或 mock 输出当作策略 OOS。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
