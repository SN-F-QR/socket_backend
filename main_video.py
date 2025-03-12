import asyncio
import argparse
from dotenv import load_dotenv
import json

import sockettest
from VideoHandler import VideoHandler
from chat import ChatRecommender


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", "-t", type=int, default=0)
    args = parser.parse_args()

    study_number = args.task
    load_dotenv("key.env")
    with open("backend_study_setting.json", "r") as setting:
        study_setting = json.load(setting)[study_number]
    print(f"The current city is {study_setting['city']}")
    recommender = ChatRecommender()
    recommender.prompts["video"] = recommender.prompts["video"].replace(
        "<title>", study_setting["title"]
    )
    print(recommender.prompts["video"])
    handler = VideoHandler(recommender, study_setting["transcript"])

    sockettest.rec_callback = recommender.request_widgets
    sockettest.serp_callback = recommender.request_serp
    sockettest.serper_callback = recommender.request_serper
    sockettest.video_callback = handler.request_keywords

    asyncio.run(sockettest.start())
