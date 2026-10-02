# 06 · 私有源码上传

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 把这个最小特征函数作为私有源码资产保存，并核对服务端返回的 SHA256，不执行它。

## 本地运行

```bash
python examples/06_source.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/source/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

使用小型 feature.py 演示 `/v1/compute/sources`。比较上传 UTF-8 字节与服务端 SHA256，记录不可变资产 ID。

## 输入与前提

需 --allow-writes；真实源码替换时确认用户授权上传。每模块最多 524,288 字符、UTF-8 不超过 1 MiB。

## 预期交付

id、kind=source、sealed 状态及哈希。

## 状态变化与失败处理

每次调用创建资产；该接口没有已确认的幂等键语义，因此传输失败不自动重试。示例函数不代表已有生产 guest dispatcher 合同。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
