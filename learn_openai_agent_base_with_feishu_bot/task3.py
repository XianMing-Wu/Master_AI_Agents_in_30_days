import asyncio
import sys
import json
from agents import Agent, function_tool, Runner
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel, Field
from typing import Dict
from task0 import configure_closeai_client

# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()

# ============================================================
# 配置三个销售agent
# ============================================================

instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini"
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini"
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini"
)

# ============================================================
# 配置邮件质量评估agent
# ============================================================

instructions4 = "You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only."

sales_picker = Agent(
    name="sales_picker",
    instructions=instructions4,
    model="gpt-4o-mini"
)

# ============================================================
# 主程序
# ============================================================

async def main():
    '''
    下面是流式输出示例:
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    '''
    # =========================================================
    # 并行输出示例
    # =========================================================
    message = "Write a cold sales email"
    results = await asyncio.gather(
        Runner.run(sales_agent1, message),
        Runner.run(sales_agent2, message),
        Runner.run(sales_agent3, message),
    )
    outputs = [result.final_output for result in results]
    # =========================================================
    # 评估流程
    # =========================================================
    emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)
    best = await Runner.run(sales_picker, emails)
    print(f"Best sales email:\n{best.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
