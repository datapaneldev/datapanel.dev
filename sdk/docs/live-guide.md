# 从离线演示切换到真实 API

## 1. 配置自己的账户

通过 [DataPanel](https://datapanel.dev/) 获取自己的 API key。客户端使用 `X-API-Key`，不要把 key 作为 URL 参数、命令行参数或聊天内容。`.env.example` 是变量清单，程序不会自动读取 `.env`。

在终端中可以交互输入密钥，避免将值写入 shell 历史：

```bash
read -rsp 'DataPanel API key: ' DATAPANEL_API_KEY
export DATAPANEL_API_KEY
```

PowerShell 7 可用 `$env:DATAPANEL_API_KEY = Read-Host -MaskInput 'DataPanel API key'`。环境变量仍对同一进程的代码可见，不是一个隔离的密钥保险箱。结束后清除不再需要的环境变量。

默认 API origin 为 `https://datapanel.dev`。若使用其他合法部署，通过 `DATAPANEL_BASE_URL` 指定 HTTPS origin，不能附加路径、用户名、密码或 query。

## 2. 先读账户与目录

```bash
datapanel-demo account --mode live
datapanel-demo catalog --mode live
datapanel-demo coverage --mode live
```

完整分页上限会体现在 `truncated`。如果为 true，只能报告“已观察部分”。账户输出保留服务端字段和单位；微积分账本单位 `microcredit` 的 1,000,000 才等于 1 credit。不要将“套餐赠送积分”误当“可用余额”。

从结果中选一个真实分区，仅复制以下五个字段到 `work/selection.json`：

```json
{
  "market": "COPY_FROM_YOUR_CATALOG",
  "data_type": "COPY_FROM_YOUR_CATALOG",
  "symbol": "COPY_FROM_YOUR_CATALOG",
  "start": "2026-01-01T00:00:00Z",
  "end": "2026-01-02T00:00:00Z"
}
```

这是输入结构，不是可用性承诺。日期也必须替换为实际目录覆盖。区间为 `[start,end)`，时间必须带时区且精确到整秒。对于不可切片的格式，选择完整分区边界。

## 3. 在平台内选取数据

```bash
datapanel-demo data-access --mode live
datapanel-demo snapshot --mode live --selection work/selection.json --allow-writes
```

行情文件不提供本机导出。快照冻结平台内计算所用的数据选择；目录可见不保证该时间区间和格式适用于你的训练程序。检查覆盖、字段与格式后再提交。

私有代码与研究结果通过 `private-export` 取回。文件下载会校验大小和 SHA256；中断的 `.part` 文件保留供你检查，不能将未完整接收的文件当作成功结果。

## 4. 报价不等于运行

```bash
datapanel-demo quote --mode live --selection work/selection.json --allow-writes
datapanel-demo execution-gate --mode live
```

报价示例使用一个小型纯函数源码、`kind=features`、`cpu-small`、60 秒和 1 积分上限。它创建私有源码、数据快照及短期报价，保存可审查请求体，不 POST 作业。

用户可在 Python 中调用 `prepare_quote` 并传入自己的源码、profile、kind、时限和积分上限。服务契约定义 `features/train/predict/backtest/build/export` 六种规划类型；这不证明对应 runtime 或 GPU 已开放。最小源码函数不是正式 guest dispatcher 协议。

Python 的显式 `submit_job` 先检查执行开关，再使用调用方提供的稳定幂等键。启动前应持久化该键和原始请求，并核对报价未过期。MCP 当前不暴露任务提交，避免把“帮我报价”解释成“启动计算”。

## 5. 私有结果与任务管理

```bash
datapanel-demo private-export --mode live --artifact-id YOUR_OWN_ASSET_ID --allow-writes
datapanel-demo job-lifecycle --mode live --job-id YOUR_SELECTED_JOB_ID --allow-writes
```

私有导出只接受自己的 sealed source/result/model/report，文件大小和逻辑大小都必须严格小于十进制 1 GB。下载构造同源网关路径，拒绝重定向，核验元数据；源码导出不代表模型训练通过。

取消场景会真正请求取消你指定的任务。返回 `CANCEL_REQUESTED`、`STOPPING` 或 `RECONCILING` 时，结果中 `cancelled=false`。`SUCCEEDED` 也不等于取消成功。不要因为一次 API 调用返回成功就声称资源释放或账单已结算。

## 6. 保存证据

在本机私有记录中保留任务/资产标识、版本、文件大小和哈希；不要把实际账户记录放进公开教程。不要提交 `work/`、账户邮箱、密钥、带签名链接或真实私有源码。`result.json` 是机器可读记录；研究简报另有 Markdown。一个工作目录只交给一个写入进程使用；需要并发时使用不同目录。
