from openai import OpenAI
from dotenv import load_dotenv
from PDFReader import Recommender
import json
import re
import os


class VideoHandler:
    def __init__(self, recommender):
        self.auto_recommend = {}
        self.cur_time = 0
        self.recommender = recommender
        self.load_auto_recommend()

    def load_auto_recommend(self):
        """
        Request auto recommendation results from llm
        """
        sections = self.recommender.execute_search_agent("Divide video").split(",")
        # sections = '[{"title":"a", "span":"1-2"}, {"title":"b", "span":"2-2"}, {"title":"c", "span":"3-2"}]'
        sections = json.loads(sections)
        for section in sections:
            self.auto_recommend[section["span"].split("-")[0]] = ""

    def handle_time_change(self, current_time):
        """
        Judge if the current video progress should trigger auto recommendation
        """
        self.cur_time = current_time
        recommend = self.auto_recommend[current_time]
        return recommend if recommend else None

    # def handle_user_event(self, event):
    #     """
    #     Handle user events
    #     """
    #     pass


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = Recommender(os.getenv("ASSISTANT_ID"))
    handler = VideoHandler(recommender)
    handler.load_auto_recommend()
    print(handler.auto_recommend)
