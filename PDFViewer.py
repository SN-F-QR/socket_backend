import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pytesseract
from PDFReader import execute_agent
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, Future
import asyncio

import sockettest
from sockettest import send_message_once  # send_message 仍然可以单独导入


class ContinuousPDFViewer(tk.Frame):
    def __init__(self, master, pdf_path, scroll_stop_callback=None):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.master = master

        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

        # ============ Canvas + Scrollbar ============
        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 在 Canvas 内创建一个 frame, 用来放置所有页面
        self.pages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor="nw")

        self.page_images = []  # 每页的 PIL.Image (放大或原始)
        self.page_tk_images = []  # 每页的 ImageTk.PhotoImage
        self.page_canvases = []  # 每页的 Canvas

        # 绑定滚轮 (Windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)

        # 当 pages_frame 大小变化时, 更新 scrollregion
        self.pages_frame.bind("<Configure>", self._on_frame_configure)

        # 一次性渲染全部页面
        self.render_all_pages()

        # 底部用来显示当前页的 Label
        self.current_page_label = tk.Label(self, text="", bg="yellow")
        self.current_page_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_idletasks()  # 刷新布局，确保 bbox 准确
        self._adjust_window_size()

        # ============ "当前页"记录 =============
        self.last_page_idx = None  # 记录上次检测到的“当前页”

        # ============ 滚动停止检测 =============
        self.scroll_stop_timer = None  # 记录定时器的 ID
        self.scroll_stop_delay = 1000  # 停止滚动后等待的毫秒数 (1秒)

        self.scroll_stop_callback = scroll_stop_callback
        self.scroll_callback_status = None
        if scroll_stop_callback:
            self.scroll_callback_status = scroll_stop_callback(0, self.doc[0])

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
                highlightthickness=0,
            )
            page_canvas.pack(pady=10)  # 每页间留点空隙
            page_canvas.create_image(0, 0, anchor="nw", image=tk_img)

            # 存储起来，后面要在 get_current_page() / 鼠标事件用
            self.page_canvases.append(page_canvas)

            # 绑定鼠标事件：绘制拖拽矩形
            page_canvas.bind(
                "<Button-1>", lambda e, idx=page_index: self.on_left_button_down(e, idx)
            )
            page_canvas.bind(
                "<B1-Motion>", lambda e, idx=page_index: self.on_mouse_drag(e, idx)
            )
            page_canvas.bind(
                "<ButtonRelease-1>",
                lambda e, idx=page_index: self.on_left_button_up(e, idx),
            )

            # 初始化矩形信息
            page_canvas._start_x = None
            page_canvas._start_y = None
            page_canvas._rect_id = None

    def _on_frame_configure(self, event):
        """当 pages_frame 大小变化时，更新 Canvas 的滚动区域。"""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel_windows(self, event):
        """
        鼠标滚轮滚动(Windows)时触发:
        1) 进行正常滚动
        2) 重置一个"停止滚动"检测定时器
        """
        # 1) 正常滚动
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 2) 重置定时器
        if self.scroll_stop_timer is not None:
            self.after_cancel(self.scroll_stop_timer)
            self.scroll_stop_timer = None

        # 重新设置一个在1秒后调用的函数
        self.scroll_stop_timer = self.after(
            self.scroll_stop_delay, self._on_scroll_stopped
        )

    def _on_scroll_stopped(self):
        """
        当用户停止滚动超过1秒后会执行这里:
        在这里再去计算当前页, 更新底部标签, 然后对该页做 OCR.
        """
        self.scroll_stop_timer = None  # 清空定时器
        page_idx = self.get_current_page()
        if page_idx is not None:
            # 更新底部标签
            self.current_page_label.config(
                text=f"当前页: {page_idx+1}/{self.total_pages}"
            )

            # 如果和上次不同，则做OCR
            if page_idx != self.last_page_idx:
                self.last_page_idx = page_idx
                # Cancel the previous task if it is not done
                if (
                    self.scroll_callback_status
                    and not self.scroll_callback_status.done()
                ):
                    self.scroll_callback_status.cancel()
                    self.scroll_callback_status = None
                if self.scroll_stop_callback:
                    self.scroll_callback_status = self.scroll_stop_callback(
                        page_idx, self.doc[page_idx]
                    )

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
            event.x, event.y, event.x, event.y, outline="red", width=2, dash=(2, 2)
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
        if self.scroll_stop_callback:
            wait_result = self.scroll_stop_callback(-1, cropped)
            wait_result.result()

        # 看需求是否要清除矩形
        c.delete(c._rect_id)
        c._rect_id = None

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

    def _adjust_window_size(self):
        """
        (可选) 计算当前 Canvas 内部所有内容的总 bounding box，
        并调整窗口大小。(可能会超出屏幕, 可根据需要再做限制)
        """
        x1, y1, x2, y2 = self.canvas.bbox("all")
        total_width = x2 - x1
        total_height = y2 - y1

        self.master.geometry(f"{total_width}x{total_height}")


if __name__ == "__main__":
    print("开始加载 PDF 文件...")
    # 启动 Tkinter 主循环
    root = tk.Tk()
    root.title("PDF Viewer")
    pdf_path = r"Reading Textbook.pdf"  # 替换为实际路径
    viewer = ContinuousPDFViewer(root, pdf_path)
    root.mainloop()
