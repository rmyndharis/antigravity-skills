---
name: context-meter
description: 实时查看 Antigravity 当前会话上下文 Token 用量、各模块占比拆解、Top 5 消耗操作溯源与健康度预警。当用户输入 /context、/context-meter、上下文用量、token用量、查看上下文 时触发。
---

# Antigravity 上下文计量器技能 (Context Meter Skill)

当用户输入 `/context` 或询问上下文用量时，请执行以下操作：

1. 运行本地实时解析脚本获取当前会话精准用量：
   `node /Users/rita/Desktop/上下文用量/out/test-runner.js`

2. 根据输出的真实数据，在回复中输出结构化、清晰、高颜值的用量卡片：
   - **当前模型与基准容量**（如 `Gemini 3.7 Flash High (1M Tokens)`）
   - **已用 Token 总量与百分比**（如 `53K / 1M (5.1%)`）
   - **四级健康度状态**（🟢 Optimal / 🟡 Moderate / 🟠 Warning / 🔴 Critical）
   - **细分模块拆解**（System Rules、Skills/MCP、Messages、Tool Outputs）
   - **Top 消耗操作溯源**（排名前 3~5 的大文件读取或终端命令输出）
   - **智能建议**（若 > 75% 给出开启新会话并提炼摘要的建议）
