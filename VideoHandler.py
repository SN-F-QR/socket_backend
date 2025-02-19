from openai import OpenAI
from dotenv import load_dotenv
from PDFReader import Recommender
import webvtt
from datetime import datetime, time
from functools import reduce
import json
import re
import os


class VideoHandler:
    def __init__(self, recommender, vtt_path, section_split=None):
        self.section_recommend = []  # list of TimeSpan for each section
        self.vtt = webvtt.read(vtt_path)
        self.transcripts = None  # list of TimeSpan for each transcript
        if section_split:
            self.section_recommend = self.read_sections(section_split)

        self.cur_time = 0
        self.next_rec_time = 0

        self.recommender = recommender

    def read_sections(self, split_time):
        """
        Split sections from vtt file and return a list of video sections
        Split_time: list of the precise start time (%H:%M:%S) of each section
        return: list of TimeSpan objects for each section
        """
        sections = []
        index = -1

        last_end_time = None
        for caption in self.vtt:
            start_time = caption.start.split(".")[0]
            if index + 1 < len(split_time) and split_time[index + 1] == start_time:
                sections.append(TimeSpan(start=start_time))
                if last_end_time:
                    sections[index].set_end(last_end_time)
                index += 1

            pure_text = reduce(
                lambda x, y: x.strip() + " " + y.strip(), caption.text.split("&nbsp;")
            )  # Clean &nbsp; in text
            sections[index].transcripts += pure_text
            last_end_time = caption.end.split(".")[0]
        sections[index].set_end(last_end_time)

        for section in sections:
            print(section)
            print(section.transcripts)

        return sections

    # def load_section_recommend(self):
    #     """
    #     Request section recommendation results from llm
    #     """
    #     # sections = '[{"title":"a", "span":"1-2"}, {"title":"b", "span":"2-3"}, {"title":"c", "span":"3-4"}]'
    #     sections = json.loads(sections)
    #     for section in sections:
    #         self.auto_recommend.append(
    #             TimeSpan(*map(int, re.findall(r"\d+", section["span"])))
    #         )

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


# TimeSpan represent a video section
class TimeSpan:
    def __init__(self, start, end=None):
        """
        start: Time string in format %H:%M:%S
        """
        self.start = self.set_time(start)
        self.end = None
        self.set_end(end) if end else None

        self.transcripts = ""
        self.links = []  # json title/url pairs
        self.rs_contents = []  # json title/keywords pairs

    def set_time(self, string_time):
        return datetime.strptime(string_time, "%H:%M:%S").time()

    def set_end(self, string_end):
        end_time = self.set_time(string_end)
        assert self.start < end_time
        self.end = end_time

    def __lt__(self, other):
        """
        Sort by start time
        """
        return self.start < other.start

    def __str__(self):
        return f"TimeSpan: {self.start} - {self.end}"


if __name__ == "__main__":
    load_dotenv("key.env")
    recommender = Recommender(os.getenv("ASSISTANT_ID"))
    video_section = ["00:00:00", "00:00:57", "00:02:34"]  # start time of each section
    handler = VideoHandler(recommender, "Short_Test_Video.en.vtt", video_section)
