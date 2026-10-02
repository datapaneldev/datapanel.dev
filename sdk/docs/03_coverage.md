# 03 · 覆盖率与缺口审计

[场景总览](../README.zh-CN.md#场景导航) · [完整契约](api-contract.md)

> 在下载前检查这份数据目录的时间缺口、重复覆盖和格式限制；缺数据时不要自动补齐。

## 本地运行

```bash
python examples/03_coverage.py
```

默认完全离线，使用内存 HTTP 模拟器，不需要 DataPanel 或 OpenAI 凭据。结果保存在 `work/mock/coverage/result.json`。合成内容不代表真实市场数据。

## 运行结果如何生成

按市场、数据类型和品种分组，排序后计算相邻区间缺口与重叠。合成目录刻意缺少 1 月 3 日，让负结果可见。

## 输入与前提

目录有时区的 ISO 时间；[start,end) 为左闭右开。

## 预期交付

每组 partitions、gaps、overlaps、catalog_bytes，以及目录截断标志。

## 状态变化与失败处理

无外部写入。目录连续不证明文件内部每条 tick 都完整；时间覆盖审计与数据质量审计是两件事。

通用规则：401/403 检查账户权限；409 检查覆盖/任务冲突；429 遵守 Retry-After；503 记录服务不可用。不要为了得到“通过”更换身份、绕过网关或把 mock 结果标成 live。

## 切换到真实服务

参照 [真实模式指南](live-guide.md)。将命令追加 `--mode live`，按本场景要求提供输入。目录发现与只读场景可先验证；需要状态变化的场景显式使用 `--allow-writes`。生产执行仍取决于服务端实时状态。

## 对应实现

- [统一工作流](../src/datapanel_agent/workflows.py)
- [HTTP 客户端](../src/datapanel_agent/client.py)
- [逐场景测试](../tests/test_scenarios.py)
