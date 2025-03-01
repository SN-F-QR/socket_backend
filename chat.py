from openai import AsyncOpenAI
import os
import pandas as pd
from dotenv import load_dotenv
import json
import asyncio

from SerpapiWrapper import SerpapiWrapper
from SerperWrapper import SerperWrapper
from utility import extract_json_array


class ChatRecommender:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.prompts = {
            "normal": self.read_prompt("normal"),
            "serp": self.read_prompt("serp"),
            "serper": self.read_prompt("serper"),
        }
        self.serp_wrapper = SerpapiWrapper()
        self.serper = SerperWrapper()

    def read_prompt(self, name):
        with open(f"prompts/{name}.txt", "r") as file:
            return file.read()

    async def create_chat(self, ai_name, text_input):
        assert self.prompts.keys().__contains__(ai_name)
        format_input = self.format_text(text_input)
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": self.prompts[ai_name]},
                {"role": "user", "content": format_input},
            ],
        )
        print(
            f"{completion.choices[0].message.role}:\n{completion.choices[0].message.content}"
        )
        return completion

    async def request_widgets(self, text_input):
        response = await self.create_chat("normal", text_input)
        widgets = json.loads(extract_json_array(response.choices[0].message.content))
        try:
            assert widgets is not None and len(widgets) > 0
            return widgets
        except AssertionError:
            print("No widgets found in response.")

    async def request_serp(self, text_input):
        """
        Request serp api based on the response from LLM.
        """
        response = await self.create_chat("serp", text_input)
        args = json.loads(extract_json_array(response.choices[0].message.content))
        if args is None or len(args) == 0:
            print("There is no need to call serp api.")
            return None

        try:
            api_name = args[0]["tool"]
            assert api_name in ["SearchHotel", "SearchFlight", "SearchRestaurant"]
            api_args = list(
                map(lambda arg: arg.strip(), args[0]["keywords"].split(","))
            )

            print(f"API: {api_name}, Args: {api_args}")
            target_func = getattr(self.serp_wrapper, api_name)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, target_func, *api_args)
        except AssertionError:
            print("API not found, check LLM response if it is correct.")

    async def request_serper(self, text_input):
        response = await self.create_chat("serper", text_input)
        args = json.loads(extract_json_array(response.choices[0].message.content))
        list_args = list(map(lambda arg: arg["keyword"].strip(), args))
        print(f"Serper Args: {list_args}")
        links = await self.serper.post_all_questions(list_args)
        return links

    def format_text(self, text):
        return "<plan>" + text + "</plan>"


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = ChatRecommender()
    test_case = pd.read_csv("test_case.csv")

    async def test_normal():
        for case in test_case["content"]:
            print(f"User:\n{case}")
            normal_res, serper_res = await asyncio.gather(
                recommender.create_chat("normal", case),
                recommender.request_serper(case),
            )

    async def test_serp():
        case = test_case["content"][1]
        print(f"User:\n{case}")
        response = await recommender.request_serp(case)
        print(f"Response:\n{response}")

    async def test_serper():
        for case in test_case["content"]:
            print(f"User:\n{case}")
            response = await recommender.request_serper(case)
            print(f"Response:\n{response}")

    asyncio.run(test_serper())
    # asyncio.run(test_normal())
