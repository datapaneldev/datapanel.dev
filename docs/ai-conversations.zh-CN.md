# 多轮量化研究对话 API

使用 `POST /v1/ai/chat` 与 Datapanel AI 助手对话。它使用与官网工作台相同的模型配置、官方文档工具和账户权限。先调用 `GET /v1/ai/status` 检查 `enabled`、`provider`、`private_inference` 和额度；此接口不会强制切换模型，也不会自动回退到云模型。

通过 `X-API-Key` 请求头认证，需要有效订阅或体验权限。不要把密钥写入消息正文。此入口与官网工作台共享请求额度和并发限制。

客户端保存历史，每轮传入此前的 user/assistant 消息，最后追加本轮 user 消息。最多 20 条消息，每条最多 16,000 字符，总计最多 32,000 字符。超限返回 422；请自行整理上下文，不会静默删除历史。平台不保存对话正文，但会记录请求计数及脱敏操作审计。模型提供方的数据处理方式取决于状态接口显示的实际提供方。

响应包含 `answer`、`model`、`sources`、`tool_activity` 和 `truncated`。只把 `answer` 作为 assistant 消息加入后续历史。`truncated=true` 时回答不完整。AI 回答不会自行执行训练或回测，计算任务仍通过任务 API 单独提交。

## Python：连续两轮

安装 `httpx`，把自己的 API key 放在 `DATAPANEL_API_KEY` 环境变量中：

```python
import os
import httpx

messages = []
with httpx.Client(
    base_url="https://datapanel.dev",
    headers={"X-API-Key": os.environ["DATAPANEL_API_KEY"]},
    timeout=httpx.Timeout(7380, connect=10),
) as client:
    status = client.get("/v1/ai/status")
    status.raise_for_status()
    if not status.json()["enabled"]:
        raise RuntimeError("AI 服务暂不可用")
    for question in [
        "阅读官方文档，介绍可用数据和 CPU 训练示例。",
        "在刚才的示例中指出特征函数，并解释如何按时间划分训练和验证集。",
    ]:
        messages.append({"role": "user", "content": question})
        response = client.post("/v1/ai/chat", json={"messages": messages})
        response.raise_for_status()
        result = response.json()
        print(result["answer"])
        messages.append({"role": "assistant", "content": result["answer"]})
```

同一账户最多一条在途请求。429 时遵守 `Retry-After`，不要立即循环重试。401 表示认证失败，402 表示需要有效使用权限，422 表示消息不符合要求，503 表示模型未配置或不可用，502 表示模型调用失败。单次请求可能持续较长时间；对话请求超时不等于计算任务超时。网络断开后不要假定请求被取消或盲目重发，应先等待原请求结束。

## 案例：分析用户提供的加密行业新闻

将新闻正文直接作为消息内容提交。请明确来源和发布时间；没有来源的内容应当作为待核实材料。以下新闻是模拟材料，不代表真实市场事件。

```python
import os
import httpx

news = """模拟新闻：某加密交易平台宣布下月提高永续合约保证金要求，
并对流动性较低的代币降低杠杆上限。公告未披露受影响持仓规模。"""
messages = [{
    "role": "user",
    "content": (
        "仅基于下面的模拟新闻分析，不搜索、不执行任务。请用中文列出："
        "事件摘要、对BTC与小币种的可能影响、利多利空因素、缺失信息、"
        "可验证的量化假设。不要编造价格或确定收益。\n" + news
    ),
}]
with httpx.Client(
    base_url="https://datapanel.dev",
    headers={"X-API-Key": os.environ["DATAPANEL_API_KEY"]},
    timeout=httpx.Timeout(7380, connect=10),
) as client:
    response = client.post("/v1/ai/chat", json={"messages": messages})
    response.raise_for_status()
    result = response.json()
    print(result["answer"])
    messages.append({"role": "assistant", "content": result["answer"]})
    messages.append({"role": "user", "content": (
        "把刚才的量化假设整理为事件研究方案，说明观察窗口、对照组、"
        "所需字段和避免未来信息泄漏的方法。不要提交计算任务。"
    )})
    followup = client.post("/v1/ai/chat", json={"messages": messages})
    followup.raise_for_status()
    print(followup.json()["answer"])
```

分析应区分新闻中明确给出的事实和可能的传导机制。例如保证金提高可能促使去杠杆，但实际影响仍取决于持仓、调整幅度及实施时间。模型输出是研究辅助材料；需要结合原始公告和实际行情验证，不能把分析文本当作已执行回测或交易信号。
