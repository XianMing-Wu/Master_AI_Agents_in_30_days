import asyncio
import sys
from typing import AsyncGenerator

from task0 import configure_closeai_client
from task4 import plan_searches, WebSearchPlan
from task5 import perform_searches
from task6 import write_report, ReportData
from task7 import send_card

# ============================================================
# CloseAI 中转配置
# ============================================================
configure_closeai_client()

# ============================================================
# 封装深度调研全流程
# ============================================================
class ResearchManager:
    """封装深度调研的端到端流程，并提供状态流输出"""

    async def run(self, query: str) -> AsyncGenerator[str, None]:
        """执行调研流程，并按阶段产出状态/结果"""
        print("Starting research...")

        # 1. 调研规划
        yield "📋 正在规划检索策略..."
        search_plan = await self._plan(query)
        yield f"✅ 已生成搜索计划（{len(search_plan.searches)} 项）"

        # 2. 并发检索
        yield "🔍 正在执行搜索..."
        search_results = await self._search(search_plan)
        yield f"✅ 完成搜索任务（获取 {len(search_results)} 条摘要）"

        # 3. 写作报告
        yield "📝 正在撰写研究报告..."
        report = await self._write(query, search_results)
        yield "✅ 报告撰写完成"

        # 4. 发送飞书卡片
        yield "📨 正在发送飞书卡片..."
        await send_card(report)
        yield "✅ 飞书卡片发送完成"

        # 5. 输出最终 Markdown 报告（便于 CLI 预览）
        yield report.markdown_report

    async def _plan(self, query: str) -> WebSearchPlan:
        return await plan_searches(query)

    async def _search(self, search_plan: WebSearchPlan) -> list[str]:
        return await perform_searches(search_plan)

    async def _write(self, query: str, search_results: list[str]) -> ReportData:
        return await write_report(query, search_results)


async def main() -> None:
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("请提供调研主题！")
        return

    manager = ResearchManager()

    try:
        async for status in manager.run(query):
            print(status)
    except Exception as exc:
        print(f"❌ 调研流程出错: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
