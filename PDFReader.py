# from langchain_community.llms import OpenAI
from langchain_core.agents import AgentFinish
from langchain.agents import Tool, Agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
from openai import OpenAI

import json
import os
import re


class Recommender:
    def __init__(self, search_assistant_id=None, normal_assistant_id=None):
        self.client = OpenAI()
        self.search_assistant_id = search_assistant_id
        self.normal_assistant_id = normal_assistant_id

        if self.search_assistant_id:
            self.search_agent, self.search_thread_id = self.create_assistant(
                self.search_assistant_id
            )

        if self.normal_assistant_id:
            self.normal_agent, self.normal_thread_id = self.create_assistant(
                self.normal_assistant_id
            )

        # init tools for LLM functions
        self.tools = []
        self.search = self.init_search_tool()

    def create_thread(self):
        empty_thread = self.client.beta.threads.create()
        thread_id = empty_thread.id
        print(f"Empty thread created: {thread_id}")
        return thread_id

    def create_assistant(self, assistant_id):
        return (
            OpenAIAssistantRunnable(
                assistant_id=assistant_id,
                as_agent=True,
            ),
            self.create_thread(),
        )

    def init_search_tool(self):
        search = GoogleSerperAPIWrapper()
        self.tools.append(
            Tool(
                name="IntermediateAnswer",
                func=search.results,  # directly return API result
                description="useful for when you need to ask with search",  # may not work
            )
        )
        return search

    def execute_normal_agent(self, text_input):
        if not self.normal_assistant_id:
            raise AttributeError("Normal Assistant not found")
        response = self.normal_agent.invoke(
            {"content": text_input, "thread_id": self.normal_thread_id}
        )
        print(response.return_values["output"])

        json = re.search(
            r"\[\s*\{[\s\S]*?\}\s*\]", response.return_values["output"]
        ).group()

        return json

    def execute_search_agent(self, text_input):
        """
        Send input to the search agent
        text_input: string contents for agent
        return: search results in string format "[{},{},{}]"
        """
        if not self.search_assistant_id:
            raise AttributeError("Search Agent not found")
        input = {}
        input["content"] = text_input
        input["thread_id"] = self.search_thread_id
        tool_map = {tool.name: tool for tool in self.tools}

        response = self.search_agent.invoke(input)
        while not isinstance(response, AgentFinish):
            tool_outputs = []
            for action in response:
                tool_output = tool_map[action.tool].invoke(action.tool_input)

                origin_webs = self.handle_search_result(tool_output)
                tool_outputs.append(
                    {"output": origin_webs, "tool_call_id": action.tool_call_id}
                )
            response = self.search_agent.invoke(
                {
                    "tool_outputs": tool_outputs,
                    "run_id": action.run_id,
                    "thread_id": self.search_thread_id,
                }
            )

        # Eliminate possible reasoning texts
        webs_json = re.search(
            r"\[\s*\{[\s\S]*?\}\s*\]", response.return_values["output"]
        ).group()

        return webs_json  # 注意这里不要把origin_webs返回, 返回最终结果
        # return response.return_values["output"]

    def handle_search_result(self, result):
        """
        Handle the search result from Google Serper API.
        TODO: improve the filter of results, also the prompt
        result: from SerperAPIWrapper.results()
        """
        webs = result["organic"]
        main_webs = list(
            map(
                lambda web: {
                    "title": web["title"],
                    "link": web["link"],
                    "snippet": web["snippet"],
                },
                webs,
            )
        )
        print("Search results:")
        for web in main_webs:
            print(f"{web['title']}, {web['link']}")
        json_result = json.dumps(main_webs)
        # Convert to JSON plain text
        # print("Origin JSON result:")
        # print(json_result)
        return json_result


# load_dotenv("key.env")
# assistant_id = os.getenv("ASSISTANT_ID")
# # thread_id = os.getenv("THREAD_ID")
# thread_id = ""
# if len(thread_id) == 0:
#     client = OpenAI()
#     empty_thread = client.beta.threads.create()
#     thread_id = empty_thread.id
#     print(f"Empty thread created: {thread_id}")

# os.environ["OPENAI_API_KEY"] = openai_key
# os.environ["SERPER_API_KEY"] = serper_key
# _instructions = (
#     "1) You are going to read the OCR-generated text.\n"
#     "2) Abstract the key words and phrases from the text.\n"
#     "2) Search for related resources based on the key terms on Google.\n"
#     "3) Provide the direct link to the most relevant resource.\n"
#     "4) Do not include your internal reasoning in the final answer."
# )

# search = GoogleSerperAPIWrapper()
# # function should be adjusted in dashboard manually, see assistant "SearchReaderHelper"
# tools = [
#     Tool(
#         name="IntermediateAnswer",
#         func=search.results,  # directly return API result
#         description="useful for when you need to ask with search",  # may not work
#     )
# ]
# agent = OpenAIAssistantRunnable(
#     assistant_id=assistant_id,
#     as_agent=True,
# )


# def execute_agent(input):
#     input["thread_id"] = thread_id
#     tool_map = {tool.name: tool for tool in tools}

#     response = agent.invoke(input)
#     while not isinstance(response, AgentFinish):
#         tool_outputs = []
#         for action in response:
#             tool_output = tool_map[action.tool].invoke(action.tool_input)

#             origin_webs = handle_search_result(tool_output)
#             tool_outputs.append(
#                 {"output": origin_webs, "tool_call_id": action.tool_call_id}
#             )
#         response = agent.invoke(
#             {
#                 "tool_outputs": tool_outputs,
#                 "run_id": action.run_id,
#                 "thread_id": thread_id,
#             }
#         )

#     # Eliminate possible reasoning texts
#     webs_json = re.search(
#         r"\[\s*\{[\s\S]*?\}\s*\]", response.return_values["output"]
#     ).group()

#     return webs_json  # 注意这里不要把origin_webs返回, 返回最终结果
#     # return response.return_values["output"]


# def handle_search_result(result):
#     """
#     Handle the search result from Google Serper API.
#     TODO: improve the filter of results, also the prompt
#     result: from SerperAPIWrapper.results()
#     """
#     webs = result["organic"]
#     main_webs = list(
#         map(
#             lambda web: {
#                 "title": web["title"],
#                 "link": web["link"],
#                 "snippet": web["snippet"],
#             },
#             webs,
#         )
#     )
#     print("Search results:")
#     for web in main_webs:
#         print(f"{web['title']}, {web['link']}")
#     json_result = json.dumps(main_webs)
#     # Convert to JSON plain text
#     # print("Origin JSON result:")
#     # print(json_result)
#     return json_result


# agent_executor = AgentExecutor(agent=agent, tools=tools)
# message = agent_executor.invoke({"content": md_uid_text})

if __name__ == "__main__":
    test_input = '"""Within-subjects and between-subjects are two fundamental experimental design approaches in research methodology. In a within-subjects design, all participants experience every experimental condition, serving as their own control group, which leads to higher statistical power and requires fewer participants. This design is particularly effective at controlling individual differences and detecting small but meaningful changes in responses. However, it can be vulnerable to fatigue and carryover effects when participants undergo multiple treatments. In contrast, between-subjects design involves dividing participants into separate groups, with each group experiencing only one condition. This approach is particularly useful when studying treatments that cannot be reversed or when researchers want to avoid practice effects1. While it requires more participants to achieve statistical significance and may be affected by individual differences between groups, it offers the advantage of shorter experimental duration per participant and eliminates concerns about carryover effects. The choice between these designs often depends on specific research needs, such as the nature of the treatment, available resources, and whether the potential for practice or fatigue effects could impact results. Between-subjects design is typically preferred when exposure to one condition might influence responses to others, while within-subjects design is more suitable when studying changes or differences within individual participants over time. Let\' think step by step,"""'

    load_dotenv("key.env")
    recommender = Recommender(
        # search_assistant_id=os.getenv("ASSISTANT_ID"),
        normal_assistant_id=os.getenv("NORMAL_ASSISTANT_ID"),
    )
    # message = recommender.execute_search_agent(test_input)
    message = recommender.execute_normal_agent(test_input)
    print(message)
    # links = json.loads(message)
    # print(links)
