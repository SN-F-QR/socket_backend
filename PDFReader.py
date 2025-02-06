from langchain_community.llms import OpenAI
from langchain_core.agents import AgentFinish
from langchain.agents import Tool, Agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
from dotenv import load_dotenv

import os
load_dotenv("key.env")
openai_key = os.getenv("OPENAI_API_KEY")
serper_key = os.getenv("SERPER_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

os.environ["OPENAI_API_KEY"] = openai_key
os.environ["SERPER_API_KEY"] = serper_key
# _instructions = (
#     "1) You are going to read the OCR-generated text.\n"
#     "2) Abstract the key words and phrases from the text.\n"
#     "2) Search for related resources based on the key terms on Google.\n"
#     "3) Provide the direct link to the most relevant resource.\n"
#     "4) Do not include your internal reasoning in the final answer."
# )

search = GoogleSerperAPIWrapper()
tools = [
    Tool(
        name="IntermediateAnswer",
        func=search.run,
        description="useful for when you need to ask with search"
    )
]
agent = OpenAIAssistantRunnable(
    assistant_id=assistant_id,
    as_agent=True,
)


def execute_agent(input, thread_id):
    input["thread_id"] = thread_id
    tool_map = {tool.name: tool for tool in tools}
    response = agent.invoke(input)
    while not isinstance(response, AgentFinish):
        tool_outputs = []
        for action in response:
            tool_output = tool_map[action.tool].invoke(action.tool_input)
            print(action.tool, action.tool_input, tool_output, end="\n\n")
            tool_outputs.append(
                {"output": tool_output, "tool_call_id": action.tool_call_id}
            )
        response = agent.invoke(
            {
                "tool_outputs": tool_outputs,
                "run_id": action.run_id,
                "thread_id": thread_id
            }
        )
    return response
# agent_executor = AgentExecutor(agent=agent, tools=tools)
# message = agent_executor.invoke({"content": md_uid_text})

