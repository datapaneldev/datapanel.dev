# 当前 API 与旧版迁移

以 [官网 OpenAPI](https://datapanel.dev/openapi.json) 和你的账户实际响应为准。官网仍使用 `0.3.0` 标识；不要只靠版本号判断能力。

| 旧入口或假设 | 现在怎么用 |
|---|---|
| 行情分区下载、`/v1/downloads` | 已停用；使用目录 → 数据快照 → 平台内计算 |
| MCP `download_partition` / `download_status` | 改用 `data_access_policy` / `compute_profiles`；结果用私有产物导出 |
| GPU 没有公开接口 | 固定模板具有独立 inputs / quotes / jobs 接口，权限由该服务判断 |
| 通用 profiles 无 GPU，所以所有 GPU 入口关闭 | 通用 CPU 与固定 GPU 模板入口分别查询；不推断或绕过准入 |
| 固定单卡模板等于任意 Python / 多卡训练 | 不等价；自定义分布式训练需要相应公开合同和授权 |
| 自动接入官网所有新功能 | 当前示例不封装研究会话、长训练 campaign 或 AI chat；请参照其独立 schema |

从 [真实模式指南](live-guide.md) 开始检查账户、目录、快照与报价。CPU 模型见 [自定义特征教程](custom-features.zh-CN.md)，GPU 输入与报价见 [固定模板指南](gpu-template.zh-CN.md)。所有默认示例仍为离线模拟；线上报价与作业执行需要明确选择。

## 下次官网更新时快速核对

```bash
python -m datapanel_agent.compatibility
```

这个只读命令获取公开 OpenAPI，无需密钥，检查示例使用的 21 个接口和请求字段。`compatible=true` 只代表路由与字段匹配；账户权限、数值约束、训练运行和结果质量仍需分别检查。也可用 `--schema path/to/openapi.json` 离线核对已保存的文档。
