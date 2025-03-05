import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from dotenv import load_dotenv

import sockettest
from VideoHandler import VideoHandler
from chat import ChatRecommender


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = ChatRecommender()
    # video_section = [
    #     "00:00:00",
    #     "00:00:57",
    #     "00:02:34",
    # ]  # start time of each section
    handler = VideoHandler(recommender, "Short_Test_Video.en.vtt")
    # sockettest.time_callback = handler.handle_time_change
    sockettest.rec_callback = recommender.request_widgets
    sockettest.serp_callback = recommender.request_serp
    sockettest.serper_callback = recommender.request_serper
    sockettest.video_callback = handler.request_keywords
    asyncio.run(sockettest.start())
