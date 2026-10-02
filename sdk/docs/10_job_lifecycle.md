# 10 · 任务跟踪与取消回读

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 取消我明确指定的任务，并重新查询状态；只有服务端确认 CANCELLED 才报告取消完成。

## 本地运行

```bash
python examples/10_job_lifecycle.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/job-lifecycle/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

读取已有 job_id，POST cancel，再独立 GET。CANCEL_REQUESTED、STOPPING、RECONCILING 都不能当作完成。

## 输入与前提

live 需要 --job-id 和 --allow-writes，且执行 API 开放。离线演示预置一个合成任务。

## 预期交付

before、cancel_response、readback、cancelled 布尔值。

## 状态变化与失败处理

取消可能影响正在执行的工作；只处理用户指定 ID。实际是否可取消取决于任务状态和账户权限。遇到 503 请检查服务可用性，保留原任务 ID。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
