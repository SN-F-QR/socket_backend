from openai import OpenAI
from dotenv import load_dotenv
from PDFReader import Recommender
import webvtt
from datetime import datetime, time
from functools import reduce
import json
import re
import os


# TODO: add cache for transcript
class VideoHandler:
    def __init__(self, recommender, vtt_path, section_split=None):
        self.section_recommend = []  # list of TimeSpan for each section
        self.vtt = webvtt.read(vtt_path)
        self.transcripts = (
            self.read_transcripts()
        )  # list of TimeSpan for each transcript
        if section_split:
            self.section_recommend = self.read_sections(section_split)

        self.last_section = None  # used to compare if the section span has changed

        self.recommender = recommender

        # Generate auto recommendation contents
        for section in self.section_recommend:
            links = self.request_recommendation(section.content)
            section.links = json.loads(links)

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
            start_time = caption.start
            if (
                index + 1 < len(split_time)
                and split_time[index + 1] == start_time.split(".")[0]
            ):
                sections.append(TimeSpan(start=start_time))
                if last_end_time:
                    sections[index].set_end(last_end_time)
                index += 1

            sections[-1].add_transcript(caption.text)
            last_end_time = caption.end
        sections[index].set_end(last_end_time)

        # for section in sections:
        #     print(section)
        #     print(section.content)

        return sections

    def read_transcripts(self):
        """
        Read all transcripts from vtt file
        """
        transcripts = []
        for caption in self.vtt:
            transcripts.append(TimeSpan(start=caption.start, end=caption.end))
            transcripts[-1].add_transcript(caption.text)

        return transcripts

    def get_time_span(self, time, span_list):
        """
        Get the transcript at a certain time from the list
        """
        for span in span_list:
            if span.within_span(time):
                return span

    def request_recommendation(self, content):
        """
        Request section recommendation results from llm
        """
        wrapped_content = "<video transcript>" + content + "</video transcript>"
        result = self.recommender.execute_search_agent(wrapped_content)
        print(f"LLM outputs:\n {result}")
        return result

    async def handle_time_change(self, current_time):
        """
        Judge if the current video progress should trigger auto recommendation
        """
        time_value = int(current_time)
        format_time = f"{time_value // 3600:02d}:{(time_value % 3600) // 60:02d}:{time_value % 60:02d}"
        cur_section = self.get_time_span(format_time, self.section_recommend)
        if cur_section and cur_section != self.last_section:
            self.last_section = cur_section
            # return "test result"
            return cur_section.links  # TODO: return all things
        return None

    # def handle_user_event(self, event):
    #     """
    #     Handle user events
    #     """
    #     pass


# TimeSpan represent a video section or a transcript
class TimeSpan:
    def __init__(self, start, end=None):
        """
        start: Time string in format %H:%M:%S
        """
        self.start = self.set_time(start)
        self.end = None
        self.set_end(end) if end else None

        self.content = ""
        self.links = []  # json title/url pairs
        self.rs_contents = []  # json title/keywords pairs

    def set_time(self, string_time):
        return datetime.strptime(string_time.split(".")[0], "%H:%M:%S").time()

    def set_end(self, string_end):
        end_time = self.set_time(string_end)
        assert self.start < end_time
        self.end = end_time

    def add_transcript(self, text):
        pure_text = reduce(
            lambda x, y: x.strip() + " " + y.strip(), text.split("&nbsp;")
        )  # Clean &nbsp; in text
        self.content += pure_text

    def within_span(self, time):
        """
        Check if the time is within the span
        """
        return self.start <= self.set_time(time) <= self.end

    def __lt__(self, other):
        """
        Sort by start time
        """
        return self.start < other.start

    def __str__(self):
        return f"TimeSpan: {self.start} - {self.end} \nContent: {self.content}\n"


if __name__ == "__main__":
    # TODO: ensure the time accuracy
    load_dotenv("key.env")
    recommender = Recommender(os.getenv("VIDEO_ASSISTANT_ID"))
    video_section = ["00:00:00", "00:00:57", "00:02:34"]  # start time of each section
    handler = VideoHandler(recommender, "Short_Test_Video.en.vtt", video_section)
    # print("Testing read_transcripts:")
    # for transcript in handler.transcripts:
    #     print(transcript)
    # print("Testing get_transcript:")
    # print(handler.get_transcript("00:00:45"))
    # print(handler.get_transcript("00:01:45"))
