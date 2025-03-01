import requests
import json
import os
from dotenv import load_dotenv
import asyncio


class SerperWrapper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        self.headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    async def post_all_questions(self, questions):
        """
        Post all questions to the serper api and return the responses.
        return: a list contains the first websites of each question.
        """
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, self.search_one, question)
            for question in questions
        ]
        responses = await asyncio.gather(*tasks)
        print("All questions are acquired:")
        for website in responses:
            print(website["title"])
        return responses

    def search_one(self, question):
        response = self.post_request(question)
        return self.extract_first_website(response)

    def post_request(self, query):
        payload = {
            "q": query,
            "num": 10,
        }
        response = requests.post(
            self.base_url, headers=self.headers, data=json.dumps(payload)
        )
        return response.json()

    def extract_first_website(self, response):
        first_website = response["organic"][0]
        info = {
            "title": first_website["title"],
            "link": first_website["link"],
            "snippet": first_website["snippet"],
        }
        return info
