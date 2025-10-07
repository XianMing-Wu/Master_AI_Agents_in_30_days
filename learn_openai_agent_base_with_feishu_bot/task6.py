import asyncio
import json
import sys
from typing import Dict, List
import os
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from task0 import configure_closeai_client
from task2 import FeishuCardClient
from task3 import instructions1,instructions2,instructions3
from task5 import emailer_agent,sales_manager_instructions

# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()

# ============================================================
# 飞书机器人初始化
# ============================================================
# 1. 初始化客户端
feishu_client = FeishuCardClient()
# 2. 获取 token
token, err = feishu_client.get_token()

# ============================================================
# 配置第三方llm
# ============================================================
deepseek_base_url = "https://api.deepseek.com/v1"
qwen_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
glm_base_url = "https://open.bigmodel.cn/api/paas/v4/"
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
glm_api_key = os.getenv("GLM_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")


deepseek_client = AsyncOpenAI(base_url=deepseek_base_url, api_key=deepseek_api_key)
qwen_client = AsyncOpenAI(base_url=qwen_base_url, api_key=qwen_api_key)
glm_client = AsyncOpenAI(base_url=glm_base_url, api_key=glm_api_key)

deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)
qwen_model = OpenAIChatCompletionsModel(model="qwen-plus", openai_client=qwen_client)
glm_model = OpenAIChatCompletionsModel(model="glm-4.6", openai_client=glm_client)

sales_agent1 = Agent(name="DeepSeek Sales Agent", instructions=instructions1, model=deepseek_model)
sales_agent2 =  Agent(name="Gemini Sales Agent", instructions=instructions2, model=qwen_model)
sales_agent3  = Agent(name="Llama3.3 Sales Agent",instructions=instructions3,model=glm_model)


# ============================================================
# 重新定义写邮件相关工具
# ============================================================
description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

# ============================================================
# 重新配置邮件管理agent
# ============================================================
tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

async def main():
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    result = await Runner.run(sales_manager, message)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())