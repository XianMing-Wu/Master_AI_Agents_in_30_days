import asyncio
import sys
import json

from typing import Dict

from agents import Agent, function_tool, Runner, ModelSettings
from task2 import FeishuCardClient
from task4 import plan_searches
from task5 import perform_searches
from task6 import ReportData, write_report
from task0 import configure_closeai_client

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
token, _ = feishu_client.get_token()

# ============================================================
# 创建发送飞书卡片工具
# ============================================================
@function_tool
def send_feishu_card(title: str, summary: str, content: str, follow_up_questions: list[str]) -> Dict[str, str]:
    try:
        # 复用 Task 2 的卡片生成逻辑
        card = feishu_client.create_research_card(
            title=title,
            summary=summary,
            content=content,
            follow_up_questions=follow_up_questions
        )
        # 使用初始化时获取的 token 发送卡片
        feishu_client.send_card(token, card)
        return {"status": "success"}
    except Exception as e:
        return {"status": "false", "error": str(e)}

# ============================================================
# 配置发送飞书agent
# ============================================================
INSTRUCTIONS = (
    "You are responsible for delivering the research findings as a Feishu interactive card."
    " Use the send_feishu_card tool exactly once. A JSON payload named card_data will be provided"
    " in the prompt; copy its fields directly into the tool call as: title -> card_data.title,"
    " summary -> card_data.short_summary, content -> card_data.markdown_report, follow_up_questions ->"
    " card_data.follow_up_questions. Invoke the tool like send_feishu_card(title=..., summary=...,"
    " content=..., follow_up_questions=...). Do not alter the Markdown content, add commentary, or"
    " fabricate new information."
)

feishu_agent = Agent(
    name="feishu agent",
    instructions=INSTRUCTIONS,
    tools=[send_feishu_card],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required")
)

async def send_card(report: ReportData) -> None:
    print("Writing feishu card...")

    # 准备好要传给工具函数的结构化数据
    card_data = {
        "title": report.title,
        "short_summary": report.short_summary,
        "markdown_report": report.markdown_report,
        "follow_up_questions": report.follow_up_questions
    }

    # 明确告诉 Agent 必须调用工具，并提供 json.dumps 结果
    input = (
        "You must call send_feishu_card with the provided data.\n"
        f"card_data = {json.dumps(card_data, ensure_ascii=False)}"
    )

    result = await Runner.run(
        feishu_agent,
        input
    )

    print("feishu card sent")
    return report


async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("请提供查询内容！")
        return

    try:
        # 创建规划
        plan = await plan_searches(query)
        # 执行搜索
        research_contents_list = await perform_searches(plan)
        # 执行写作
        report = await write_report(query, research_contents_list)
        # 执行发送
        await send_card(report)
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
