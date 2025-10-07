import asyncio
import sys
from agents import Runner
from task3 import search_agent
from task4 import WebSearchItem, WebSearchPlan, plan_searches
from task0 import configure_closeai_client
# ============================================================
# CloseAI 中转配置
# ============================================================

configure_closeai_client()

# ============================================================
# 配置多个query的搜索agent
# ============================================================
async def search(item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

async def perform_searches(search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

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
        # 显示结果
        print(research_contents_list)

    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
