import sys
import asyncio

from agents import Agent, Runner
from pydantic import BaseModel, Field

from task0 import configure_closeai_client

# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()

# ============================================================
# 配置计划agent
# ============================================================

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)


async def plan_searches(query: str) -> WebSearchPlan:
    """Plan the searches to perform for the query."""

    print("Planning searches...")
    result = await Runner.run(
        planner_agent,
        f"Query: {query}",
    )
    print(f"Will perform {len(result.final_output.searches)} searches")
    return result.final_output_as(WebSearchPlan)



async def main():
    # 获取查询
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("请提供查询内容！")
        return

    try:
        # 创建规划
        plan = await plan_searches(query)

        # 显示规划
        print(plan)

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
