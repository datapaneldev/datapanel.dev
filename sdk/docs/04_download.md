# 04 · 平台内数据访问

历史行情文件导出已停用。你仍可查询目录、选择数据快照，并在平台内运行特征、训练与回测；自己的代码和研究结果可通过私有产物接口取回。

```bash
python examples/04_data_access.py
datapanel-demo data-access --mode live
```

第一条命令使用离线模拟；第二条使用环境变量 `DATAPANEL_API_KEY` 查询实际规格。输出包含 `market_data_export=retired`、平台内数据用途与可用规格，不创建作业、不下载行情。

继续使用 [数据快照](07_snapshot.md) 和 [报价](08_quote.md)。任务完成后，参照 [私有产物导出](11_private_export.md) 下载自己的结果。

旧的 `datapanel-demo download` 命令已移除，旧 Python 下载调用返回明确的迁移错误。不要将目录可见误认为允许导出原始行情。更多变更见 [版本适配指南](migration.md)。
