from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv


class ChatRecommender:
    def __init__(self):
        self.client = OpenAI()
        self.prompts = {
            "normal": self.read_prompt("normal"),
            "serper": self.read_prompt("serper"),
        }

    def read_prompt(self, name):
        with open(f"prompts/{name}.txt", "r") as file:
            return file.read()

    def create_chat(self, ai_name, text_input):
        assert self.prompts.keys().__contains__(ai_name)
        format_input = self.format_text(text_input)
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": self.prompts[ai_name]},
                {"role": "user", "content": format_input},
            ],
        )
        return completion

    def format_text(self, text):
        return "<plan>" + text + "</plan>"


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = ChatRecommender()
    test_case = pd.read_csv("test_case.csv")
    for case in test_case["content"]:
        print(f"User:\n{case}")
        response = recommender.create_chat("normal", case)
        print(
            f"{response.choices[0].message.role}:{response.choices[0].message.content}"
        )
