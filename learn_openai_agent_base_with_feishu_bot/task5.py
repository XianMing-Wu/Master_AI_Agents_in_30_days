import asyncio
import json
import sys
from typing import Dict, List

from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field

from task0 import configure_closeai_client
from task2 import FeishuCardClient
from task4 import tool1, tool2, tool3

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
# 创建发送飞书卡片工具
# ============================================================
@function_tool
def send_feishu_email(subject: str, markdown_body: str) -> Dict[str, str]:
    """
    Send email as a Feishu card.

    Args:
        subject: Email subject line
        markdown_body: Email body in Feishu-compatible Markdown format

    Returns:
        Dict with status: "success" or "false" with error message
    """
    try:
        # 复用 Task 2 的卡片生成逻辑
        card = feishu_client.create_email_card(
            subject=subject,
            markdown_body=markdown_body
        )
        # 使用初始化时获取的 token 发送卡片
        feishu_client.send_card(token, card)
        return {"status": "success"}
    except Exception as e:
        return {"status": "false", "error": str(e)}


# ============================================================
# 工具配置
# ============================================================
subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

markdown_instructions = """You are a Feishu card Markdown formatter. Convert email text to Feishu-compatible Markdown format.

IMPORTANT - Use ONLY these formatting options:
1. Headings: # ## ### (for titles and sections)
2. Bold: **text** (for emphasis)
3. Italic: *text* (for subtle emphasis)
4. Lists: - item or 1. item (for bullet points)
5. Line breaks: Use \\n\\n for paragraphs
6. Colors: <font color='red'>text</font> (available colors: red, blue, green, orange, grey)
7. Links: [text](url) for hyperlinks

DO NOT use: <html>, <head>, <body>, <style>, <div>, <p>, <h1>, <meta>, or any standard HTML tags.
DO NOT add CSS or styling blocks.

Focus on clear structure with headers, bold text, and proper spacing using Markdown syntax."""

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

markdown_converter = Agent(name="Feishu Markdown formatter", instructions=markdown_instructions, model="gpt-4o-mini")
markdown_tool = markdown_converter.as_tool(tool_name="markdown_formatter", tool_description="Convert text email to Feishu-compatible Markdown format")

tools = [subject_tool, markdown_tool, send_feishu_email]

instructions = """You are an email formatter and sender for Feishu cards. You receive the body of an email to be sent.

Follow these steps:
1. Use the subject_writer tool to write a compelling subject for the email
2. Use the markdown_formatter tool to convert the email body to Feishu-compatible Markdown format
3. Use the send_feishu_email tool to send the Feishu card with the subject and formatted Markdown body

Remember: The markdown_formatter will create Feishu-compatible Markdown, NOT HTML."""

# ============================================================
# 配置发送邮件agent
# ============================================================
emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it")

# ============================================================
# 配置新的管理者agent
# ============================================================
manager_tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
You can use the tools multiple times if you're not satisfied with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""


sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=manager_tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

# ============================================================
# 主程序
# ============================================================
async def main():
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    result = await Runner.run(sales_manager, message)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())