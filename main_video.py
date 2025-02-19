import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from dotenv import load_dotenv

import sockettest
from PDFReader import Recommender
from VideoHandler import VideoHandler


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = Recommender(os.getenv("VIDEO_ASSISTANT_ID"))
    video_section = [
        "00:00:00",
        "00:00:57",
        "00:02:34",
    ]  # start time of each section
    handler = VideoHandler(recommender, "Short_Test_Video.en.vtt", video_section)
    sockettest.time_callback = handler.handle_time_change
    asyncio.run(sockettest.start())
