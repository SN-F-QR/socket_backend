import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pytesseract
from PDFReader import execute_agent
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import asyncio

import sockettest
from sockettest import send_message_once

class ContinuousPDFViewer(tk.Frame):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.master = master

        # --------------- 原本的属性 ---------------
        self.agent_results_cache = {}  # 缓存每页的 LLM 结果
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
        threading.Thread(target=self._start_event_loop, daemon=True).start()
        self.current_agent_task = None

        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

        # ============ Canvas + Scrollbar (外层) ============
        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 在 Canvas 内部放一个 Frame，承载所有页面
        self.pages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor="nw")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.pages_frame.bind("<Configure>", self._on_frame_configure)

        # --------------- 用于缓存页面图像 / Canvas ---------------
        self.page_images = []     # 每页的 PIL.Image (放大或原始)
        self.page_tk_images = []  # 每页的 ImageTk.PhotoImage
        self.page_canvases = []   # 每页的 Canvas

        # --------------- 已有的翻页检测 ---------------
        self.last_page_idx = None
        self.scroll_stop_timer = None
        self.scroll_stop_delay = 1000  # 停止滚动后等1秒执行

        # --------------- 一次性渲染全部页面 ---------------
        self.render_all_pages()

        # 底部显示当前页
        self.current_page_label = tk.Label(self, text="", bg="yellow")
        self.current_page_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_idletasks()
        self._adjust_window_size()

        # 初始化时，异步 OCR 第0页（可按需删除或修改）
        asyncio.run_coroutine_threadsafe(self._do_ocr_for_page_async(0), self.loop)

    # ============ 启动单独的 asyncio Loop 线程 ============
    def _start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # ============ 渲染所有页到 pages_frame 中 ============
    def render_all_pages(self):
        zoom_factor = 1.5
        mat = fitz.Matrix(zoom_factor, zoom_factor)

        for page_index in range(self.total_pages):
            page = self.doc[page_index]
            pix = page.get_pixmap(matrix=mat)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

            self.page_images.append(pil_img)

            tk_img = ImageTk.PhotoImage(pil_img)
            self.page_tk_images.append(tk_img)

            # 用 Canvas 放置图像，后续可在上面画矩形
            page_canvas = tk.Canvas(
                self.pages_frame,
                width=pil_img.width,
                height=pil_img.height,
                bg="white",
                highlightthickness=0
            )
            page_canvas.pack(pady=10)  # 每页间留点空隙
            page_canvas.create_image(0, 0, anchor="nw", image=tk_img)

            # 存储起来，后面要在 get_current_page() / 鼠标事件用
            self.page_canvases.append(page_canvas)

            # 绑定鼠标事件：绘制拖拽矩形
            page_canvas.bind("<Button-1>",
                             lambda e, idx=page_index: self.on_left_button_down(e, idx))
            page_canvas.bind("<B1-Motion>",
                             lambda e, idx=page_index: self.on_mouse_drag(e, idx))
            page_canvas.bind("<ButtonRelease-1>",
                             lambda e, idx=page_index: self.on_left_button_up(e, idx))

            # 初始化矩形信息
            page_canvas._start_x = None
            page_canvas._start_y = None
            page_canvas._rect_id = None

    # ============ 鼠标事件：可视化选区 + OCR ============
    def on_left_button_down(self, event, page_index):
        """
        鼠标左键按下：记录起点坐标，创建一个空矩形
        """
        c = self.page_canvases[page_index]
        c._start_x, c._start_y = event.x, event.y

        # 如果已有矩形，先删掉
        if c._rect_id is not None:
            c.delete(c._rect_id)
            c._rect_id = None

        # 创建一个新的矩形
        c._rect_id = c.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=2, dash=(2,2)
        )

    def on_mouse_drag(self, event, page_index):
        """
        鼠标拖动时，更新矩形坐标
        """
        c = self.page_canvases[page_index]
        if c._start_x is None or c._start_y is None:
            return
        # 动态更新可视化矩形的位置
        c.coords(c._rect_id, c._start_x, c._start_y, event.x, event.y)

    def on_left_button_up(self, event, page_index):
        """
        鼠标左键松开：获取最终选区，对选区进行 OCR
        """
        c = self.page_canvases[page_index]
        if c._rect_id is None:
            return

        x1, y1, x2, y2 = c.coords(c._rect_id)
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # 如果选区过小就忽略
        if (x2 - x1) < 5 or (y2 - y1) < 5:
            print("[Info] 选区太小，取消 OCR。")
            return

        # 防止越界
        pil_img = self.page_images[page_index]
        x2 = min(x2, pil_img.width)
        y2 = min(y2, pil_img.height)

        # 裁剪该区域
        cropped = pil_img.crop((x1, y1, x2, y2))
        # 这里可以走同步或异步 OCR，下面演示同步即可
        text = pytesseract.image_to_string(cropped, lang='eng')

        print(f"\n[Region OCR] 第{page_index+1}页选区内容：\n{text}\n")

        #若需要进一步 LLM 或 WebSocket，可在此处调用
        message = execute_agent({"content": text})
        asyncio.run_coroutine_threadsafe(
            send_message_once(message),
            loop_ws  # 你的 WS 循环
        )

        #看需求是否要清除矩形
        c.delete(c._rect_id)
        c._rect_id = None

    # ============ 原有滚动停止 + 当前页检测 + 整页 OCR 逻辑 ============
    def _on_frame_configure(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        if self.scroll_stop_timer is not None:
            self.after_cancel(self.scroll_stop_timer)
            self.scroll_stop_timer = None

        self.scroll_stop_timer = self.after(self.scroll_stop_delay, self._on_scroll_stopped)

    def _on_scroll_stopped(self):
        self.scroll_stop_timer = None
        page_idx = self.get_current_page()
        if page_idx is not None:
            self.current_page_label.config(
                text=f"当前页: {page_idx+1}/{self.total_pages}"
            )
            if page_idx != self.last_page_idx:
                self.last_page_idx = page_idx
                # 异步 OCR 整页
                asyncio.run_coroutine_threadsafe(
                    self._do_ocr_for_page_async(page_idx), self.loop
                )

    def get_current_page(self):
        """
        根据可视窗口中心位置，找距离最近的 Canvas 视为当前页
        """
        view_top = self.canvas.canvasy(0)
        view_bottom = view_top + self.canvas.winfo_height()
        view_center = (view_top + view_bottom) / 2

        closest_index = None
        min_dist = float("inf")

        for i, page_canvas in enumerate(self.page_canvases):
            top = page_canvas.winfo_y()
            bottom = top + page_canvas.winfo_height()
            center = (top + bottom) / 2
            dist = abs(center - view_center)
            if dist < min_dist:
                min_dist = dist
                closest_index = i

        return closest_index

    # ============ 异步整页 OCR + LLM + WebSocket ============
    async def _do_ocr_for_page_async(self, page_index):
        # 如果已经缓存了 LLM 结果，就直接用
        if page_index in self.agent_results_cache:
            print(f"[Cache] 第{page_index+1}页 LLM 结果：", self.agent_results_cache[page_index])
            message = self.agent_results_cache[page_index]
        else:
            # 取消前一个任务（如果需要）
            if (
                self.current_agent_task is not None
                and not self.current_agent_task.done()
            ):
                self.current_agent_task.cancel()

            # OCR (线程池)
            text = await self.loop.run_in_executor(self.executor, self._ocr_page, page_index)
            # 调 LLM
            message = await self.generate_links(text, page_index)

        # 可把结果发送到 WebSocket
        self.send_to_devices(message)

    async def generate_links(self, text, page_index):
        """ 调用 LLM Agent """
        message = await self.loop.run_in_executor(
            self.executor,
            execute_agent,
            {"content": '"""' + text + '"""'}
        )
        self.agent_results_cache[page_index] = message
        return message

    def send_to_devices(self, message):
        """ 发送到 WS (如有需要) """
        # 假设 loop_ws 是主程序那边创建的 event loop
        if loop_ws is not None:
            asyncio.run_coroutine_threadsafe(send_message_once(message), loop_ws)

    def _ocr_page(self, page_index):
        """同步整页OCR"""
        pil_img = self.page_images[page_index]
        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        return pytesseract.image_to_string(pil_img, lang="eng")

    # ============ 调整窗口大小 (可选) ============
    def _adjust_window_size(self):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        total_width = x2 - x1
        total_height = y2 - y1
        self.master.geometry(f"{total_width}x{total_height}")


if __name__ == "__main__":
    # 启动 WebSocket 线程 (若已有)
    loop_ws = asyncio.new_event_loop()
    threading.Thread(target=loop_ws.run_forever, daemon=True).start()
    asyncio.run_coroutine_threadsafe(sockettest.start(), loop_ws)

    # 启动 Tkinter 主循环
    root = tk.Tk()
    root.title("PDF Viewer with Region OCR")

    pdf_path = r"C:\Users\yysym\Downloads\s10270-020-00777-7.pdf"  # 你的PDF文件路径
    viewer = ContinuousPDFViewer(root, pdf_path)
    root.mainloop()
