import asyncio
import sys
from agents import Agent, Runner
from pydantic import BaseModel, Field
from task4 import plan_searches
from task5 import perform_searches
from task0 import configure_closeai_client
# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()
# ============================================================
# 配置写作agent
# ============================================================

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)

async def write_report(query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )
        return result.final_output_as(ReportData)

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
        # 执行搜索
        research_contents_list = await perform_searches(plan)
        # 执行写作
        report = await write_report(query, research_contents_list)
        # 显示结果
        print(report)

    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
