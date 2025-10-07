import asyncio
import json
import sys
from typing import Dict, List
import os
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from pydantic import BaseModel, Field
from task0 import configure_closeai_client
from task2 import FeishuCardClient
from task5 import sales_manager_instructions,emailer_agent,manager_tools


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
# 引入审查功能
# ============================================================
class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str

guardrail_agent = Agent( 
    name="Name check",
    instructions="Check if the user is including someone's personal name in what they want you to do.",
    output_type=NameCheckOutput,
    model="gpt-4o-mini"
)
# 这是一个装饰器，用于将此异步函数注册为一个输入审查（Guardrail）函数。
# 它确保在主 Agent 处理用户消息之前调用此函数进行检查。
@input_guardrail           
async def guardrail_against_name(ctx, agent, message):
    # ctx (RunContextWrapper): 运行上下文对象，包含了当前运行的状态和可用的上下文数据。
    # ctx.context 提供了对当前会话或请求相关数据的访问。
    # agent (Agent): 当前正在运行的 Agent 实例（通常是主 Agent）。
    # message (str): 用户输入的消息，即需要进行审查的内容。
    
    # 1. 调用专门的 guardrail_agent 来对用户消息进行审查
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    
    # 2. 从审查 Agent 的结果中提取是否检测到人名的布尔值
    is_name_in_message = result.final_output.is_name_in_message
    
    # 3. 返回 GuardrailFunctionOutput 对象，表示审查的结果
    return GuardrailFunctionOutput(
        output_info={"found_name": result.final_output}, 
        # output_info：可选的额外信息，这里包含审查 Agent 的完整输出。
        tripwire_triggered=is_name_in_message             
        # tripwire_triggered (bool): 布尔值，表示审查是否“触发绊线”。  
        # 如果为 True，则意味着审查规则被违反（例如，检测到人名），
        # 系统将阻止主 Agent 继续处理此消息，并可能抛出异常。
        # 如果为 False，则主 Agent 将继续正常执行。
    )

# ============================================================
# 重新设置带有审查功能的管理agent
# ============================================================
careful_sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=manager_tools,
    handoffs=[emailer_agent],
    model="gpt-4o-mini",
    input_guardrails=[guardrail_against_name]
    )

# ============================================================
# 主程序
# ============================================================
async def main():
    message = "Send out a cold sales email addressed to Dear CEO"
    result = await Runner.run(careful_sales_manager, message)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())