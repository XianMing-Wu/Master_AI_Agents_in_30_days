import sys
import asyncio

from agents import Agent, WebSearchTool, Runner, ModelSettings
from task0 import configure_closeai_client
from pydantic import BaseModel, Field

# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()

# ============================================================
# 配置简单的搜索agent
# ============================================================

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succintly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)


async def run_search(query: str) -> str:
    result = await Runner.run(
        search_agent,
        f"research: {query}"
    )
    return result.final_output


async def main():
    """主函数"""
    # 获取搜索关键词
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("请提供搜索关键词！")
        return

    try:
        # 执行搜索
        result = await run_search(query)

        # 显示结果
        print(result)

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
