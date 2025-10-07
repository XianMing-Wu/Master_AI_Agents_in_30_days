import asyncio
import sys
import json
from agents import Agent, function_tool, Runner
from pydantic import BaseModel, Field
from typing import Dict
from task0 import configure_closeai_client
from task1 import FeishuClient
from task3 import sales_agent1,sales_agent2,sales_agent3
# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()
# ============================================================
# 飞书机器人初始化
# ============================================================
# 1. 初始化客户端
feishu_client = FeishuClient()
# 2. 获取 token
token, err = feishu_client.get_tenant_access_token()

# ============================================================
# 创建发送飞书消息函数
# ============================================================
@function_tool
def send_feishu_message(message: str) -> Dict[str, str]:
    try:
        feishu_client.send_text_message(token, message.strip())
        return {"status": "success"}
    except Exception as e:
        return {"status": "false", "error": str(e)}

# ============================================================
# 定义agent工具
# ============================================================
description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

tools = [tool1, tool2, tool3, send_feishu_message]


# ============================================================
# 定义管理者agent
# ============================================================
instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use the send_email tool to send the best email (and only the best email) to the user.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must send ONE email using the send_email tool — never more than one.
"""


sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model="gpt-4o-mini")

# ============================================================
# 主程序
# ============================================================
async def main():
    message = "Send a cold sales email addressed to 'Dear CEO'"
    result = await Runner.run(sales_manager, message)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())