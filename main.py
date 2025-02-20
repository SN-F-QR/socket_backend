import os
import asyncio
import argparse
from concurrent.futures import ThreadPoolExecutor
import threading
import tkinter as tk
from dotenv import load_dotenv

import sockettest
from sockettest import send_message_once
import utility
from PDFViewer import ContinuousPDFViewer
from PDFReader import Recommender
from VideoHandler import VideoHandler


async def do_ocr_for_page_async(page_index, page):
    """
    异步执行 OCR 和 execute_agent 调用。
    page_index: >= 0 if a full page is passed, -1 if a cropped image is passed
    """
    # 检查缓存
    if page_index >= 0 and page_index in agent_results_cache:
        print(f"从缓存中获取第 {page_index + 1} 页的结果...")
        message = agent_results_cache[page_index]
    else:
        print("开始 OCR 和调用 execute_agent...")
        text = await loop.run_in_executor(executor, utility.ocr_page, page)

        # print(text)
        # 调用 execute_agent
        print("调用 execute_agent...")
        message = await generate_links(text, page_index)

    print(message)
    send_to_devices(message)


async def generate_links(text, page_index):
    """
    Call LLM API to generate links from text
    """
    message = await loop.run_in_executor(
        executor, recommender.execute_search_agent, '"""' + text + '"""'
    )
    # 缓存结果
    if page_index >= 0:
        agent_results_cache[page_index] = message
    return message


def send_to_devices(message):
    """
    Send suggestions from LLM to devices
    """
    if loop_ws is not None:
        print("发送消息到 WebSocket 服务器...")
        asyncio.run_coroutine_threadsafe(send_message_once(message), loop_ws)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", "-t", choices=["r", "v"], required=True, default="r")
    args = parser.parse_args()

    load_dotenv("key.env")

    if args.type == "r":
        # Init AI agent
        search_assistant_id = os.getenv("ASSISTANT_ID")
        recommender = Recommender(search_assistant_id)

        agent_results_cache = {}  # 用于缓存每页的 execute_agent 结果
        loop = asyncio.new_event_loop()  # event loop for OCR and AI Agent
        executor = ThreadPoolExecutor()  # executor for sync functions
        threading.Thread(target=loop.run_forever, daemon=True).start()

        # 启动 WebSocket 服务
        loop_ws = asyncio.new_event_loop()
        threading.Thread(target=loop_ws.run_forever, daemon=True).start()
        asyncio.run_coroutine_threadsafe(sockettest.start(), loop_ws)

        print("开始加载 PDF 文件...")
        # 启动 Tkinter 主循环
        root = tk.Tk()
        root.title("PDF Viewer")
        pdf_path = r"Reading Textbook.pdf"  # 替换为实际路径
        viewer = ContinuousPDFViewer(
            root,
            pdf_path,
            scroll_stop_callback=lambda index, page: asyncio.run_coroutine_threadsafe(
                (do_ocr_for_page_async(index, page)), loop
            ),
        )
        root.mainloop()
    elif args.type == "v":
        recommender = Recommender(os.getenv("VIDEO_ASSISTANT_ID"))
        video_section = [
            "00:00:00",
            "00:00:57",
            "00:02:34",
        ]  # start time of each section
        handler = VideoHandler(recommender, "Short_Test_Video.en.vtt", video_section)
        sockettest.time_callback = handler.handle_time_change
        asyncio.run(sockettest.start())
