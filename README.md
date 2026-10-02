# Datapanel — AI-native Quant Research

[官网 / Workbench](https://datapanel.dev/) · [在线文档 / Live docs](https://datapanel.dev/developers.html) · [API specification](https://datapanel.dev/openapi.json)

**让研究靠近数据与算力：从研究想法，到特征生成、CPU/GPU 模型训练、回测与结果比较。**

Datapanel 将授权历史行情与量化计算环境结合，减少单独租用算力时反复搬运数据和配置环境的工作。你可以在 AI 工作台描述研究目标、阅读使用示例、编写代码，再审查资源报价并提交计算任务。

支持的研究流程包括价量特征挖掘、模型训练、参数搜索、策略回测和样本外结果分析。实际可用数据、依赖、CPU/GPU 规格、任务类型、并发与额度，以你账户查询到的实时 API 和在线文档为准。不同回测方法的结果需要核对成交假设、费用与时间口径；不能把训练完成或一条模拟收益曲线直接当作策略已验证。

## 开始使用

1. 打开 [AI 量化工作台](https://datapanel.dev/)，注册并验证邮箱后登录。
2. 输入：**帮我阅读 datapanel.dev 文档，找到使用 demo，教我怎么用，告诉我它能做什么工作。**
3. 查询你的账户权限、数据目录、计算规格与积分；按示例编写自己的特征或训练代码。
4. 检查数据字段、时间划分、依赖和资源报价，确认预算后提交任务。
5. 查询运行状态，取回自己的研究结果；遇到问题，可点击对话页右下角的“错误报告”。

平台历史行情用于计算环境内的授权研究，**不提供原始历史行情文件下载服务**。用户自己的代码和结果，通过鉴权后的资产接口取回。API key 只保存在调用端的安全配置或环境变量中，不要放入代码、聊天、错误报告或 Git 仓库。

## 文档 / Documentation

| Language | User guide |
| --- | --- |
| 简体中文 | [用户指南](docs/guide.zh-CN.md) |
| English | [User guide](docs/guide.en.md) |
| 日本語 | [ユーザーガイド](docs/guide.ja.md) |
| 한국어 | [사용자 가이드](docs/guide.ko.md) |

- [AI 接入 Skill / Agent Skill](skills/datapanel-research/SKILL.md)
- [SDK、示例及训练合同 / SDK, examples and training contracts](https://datapanel.dev/ai-resources.json)
- [实时 API 定义 / Live OpenAPI](https://datapanel.dev/openapi.json)
- [平台介绍与套餐 / Platform and plans](https://datapanel.dev/platform.html)

本仓库提供公开介绍、用户指南和 AI 接入说明。指南是在线文档的可阅读快照；涉及套餐、额度、字段和权限时，请核对在线版本与实时 API。本仓库不包含平台服务端代码或生产部署配置。

## English overview

Datapanel connects authorized market data with CPU/GPU compute for quantitative research. Develop features, train models, explore parameters and evaluate backtests through the AI workbench and authenticated APIs. Keeping research near the data reduces repeated transfers and environment setup.

Start with the live documentation and examples, inspect your actual datasets and account resources, review code and a resource quote, then approve the budget before submitting a task. Retrieve your own results and compare models using appropriate chronological validation, execution assumptions and costs. Available resources and dataset coverage are determined by the live catalog and account APIs.

Raw historical market-data downloads are not offered. Keep credentials out of prompts, source code and feedback reports. The workbench's bottom-right **Report a problem** button lets signed-in users submit feedback.

## 完整教程与 AI 接入

- [用户文档与训练教程](docs/README.md)
- [AI 接入文档](docs/ai/README.md)
- [研究 Skill](skills/datapanel-research/SKILL.md) · [SDK 工作流 Skill](skills/datapanel-workflows/SKILL.md)
- [配套 SDK 与可运行示例](sdk/README.zh-CN.md)
