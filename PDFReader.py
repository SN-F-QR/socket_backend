from langchain_community.llms import OpenAI
from langchain_core.agents import AgentFinish
from langchain.agents import Tool, Agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
import os

md_uid_text = (
    "In the past, model-driven user interface development (MDUID) approaches were proposed "
    "to support the efficient development of UIs. Widely studied approaches like USiXML, MARIA, "
    "and IFML support the abstract modeling of user interfaces and their transformation to final user interfaces. "
    "However, in the aforementioned classical MDUID approaches, the modeling of context management and UI adaptation "
    "aspects introduce additional complexity as they characterize crosscutting concerns. "
    "This results in a tightly interwoven model landscape that is hard to understand and maintain. "
    "Therefore, an integrated model-driven development approach is needed where a classical model-driven development "
    "of UIs is coupled with a separate model-driven development of context-of-use and UI adaptation rules. "
    "Hence, in order to support the development of self-adaptive UIs in a systematic way, the following challenges "
    "have to be addressed to integrate context management and adaptation aspects into MDUID:\n\n"
    "Context Management Challenges:\n\n"
    "— C1: Specification of contextual parameters: A modeling language is required for specifying different contexts-of-"
    "\n\n© Springer"
)

os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "dfe5eb09d7f0996eef7a621f2f84fdf8ca290a77"
# _instructions = (
#     "1) You are going to read the OCR-generated text.\n"
#     "2) Abstract the key words and phrases from the text.\n"
#     "2) Search for related resources based on the key terms on Google.\n"
#     "3) Provide the direct link to the most relevant resource.\n"
#     "4) Do not include your internal reasoning in the final answer."
# )
# dir = "C:\\Users\\yysym\\Desktop\\ClientScripts"
#llm = OpenAI(temperature=0)

search = GoogleSerperAPIWrapper()
tools = [
    Tool(
        name="IntermediateAnswer",
        func=search.run,
        description="useful for when you need to ask with search"
    )
]
agent = OpenAIAssistantRunnable(
    assistant_id="asst_ibUwCT5Li3GLWH8UdHTPp0bT",
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

