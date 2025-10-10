from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
import os
load_dotenv()
@CrewBase
class Debate():
    """Debate crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def debater(self) -> Agent:
        return Agent(
            config=self.agents_config['debater'], 
            verbose=True,
            llm = LLM(
                        model="dashscope/qwen-plus",  
                        api_key=os.getenv("DASHSCOPE_API_KEY"),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config['judge'], 
            verbose=True,
            llm = LLM(
                        model="deepseek/deepseek-chat",  
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1")
        )

    @task
    def propose(self) -> Task:
        return Task(config=self.tasks_config['propose'])

    @task
    def oppose(self) -> Task:
        return Task(config=self.tasks_config['oppose'])

    @task
    def decide(self) -> Task:
        return Task(config=self.tasks_config['decide'])

    

    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
