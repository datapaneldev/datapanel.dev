# 11 · 私有结果安全导出

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 导出我的一个已封存结果到本机，始终走鉴权网关，核验字节和 SHA256，不暴露链接。

## 本地运行

```bash
python examples/11_private_export.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/private-export/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

按资产 ID 查元数据，申请 export，轮询 ready，然后在同一 API origin 下构造固定 content 路径。拒绝重定向，API key 不发给对象存储。

## 输入与前提

live 需要 --artifact-id 和 --allow-writes；资产必须属于当前账户，kind 可为 source/result/model/report，严格小于十进制 1 GB。

## 预期交付

本地文件路径、SHA256、verified 状态。

## 状态变化与失败处理

每次被接纳的 content GET 消耗相应额度，断线重传可能再次计费。Mock 导出合成源码用于验证通路，不冒充训练模型产物。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
