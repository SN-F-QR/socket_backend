import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import pytesseract
from PDFReader import execute_agent
from dotenv import load_dotenv

thread_id = os.getenv("THREAD_ID")
class ContinuousPDFViewer(tk.Frame):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.master = master

        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

        # ============ Canvas + Scrollbar ============
        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 在 Canvas 内创建一个 frame, 用来放置所有页面
        self.pages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor="nw")

        self.photo_images = []   # 存放 PhotoImage 引用，防止被回收
        self.page_labels = []    # 每页的 Label，用于计算位置

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
        self._do_ocr_for_page(0)

        # ============ "当前页"记录 =============
        self.last_page_idx = None  # 记录上次检测到的“当前页”

        # ============ 滚动停止检测 =============
        self.scroll_stop_timer = None        # 记录定时器的 ID
        self.scroll_stop_delay = 1000        # 停止滚动后等待的毫秒数 (1秒)

    def render_all_pages(self):
        """一次性渲染所有页到 pages_frame 中。"""
        zoom_factor = 1.5  # 放大倍数(可调节)
        mat = fitz.Matrix(zoom_factor, zoom_factor)

        for page_index in range(self.total_pages):
            page = self.doc[page_index]
            pix = page.get_pixmap(matrix=mat)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

            tk_img = ImageTk.PhotoImage(pil_img)
            self.photo_images.append(tk_img)

            # 创建 Label 展示
            lbl = tk.Label(self.pages_frame, image=tk_img, bg="white")
            lbl.pack(pady=10)
            self.page_labels.append(lbl)

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
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # 2) 重置定时器
        if self.scroll_stop_timer is not None:
            self.after_cancel(self.scroll_stop_timer)
            self.scroll_stop_timer = None

        # 重新设置一个在1秒后调用的函数
        self.scroll_stop_timer = self.after(self.scroll_stop_delay, self._on_scroll_stopped)

    def _on_scroll_stopped(self):
        """
        当用户停止滚动超过1秒后会执行这里:
        在这里再去计算当前页, 更新底部标签, 然后对该页做 OCR.
        """
        self.scroll_stop_timer = None  # 清空定时器
        page_idx = self.get_current_page()
        if page_idx is not None:
            # 更新底部标签
            self.current_page_label.config(text=f"当前页: {page_idx+1}/{self.total_pages}")

            # 如果和上次不同，则做OCR
            if page_idx != self.last_page_idx:
                self.last_page_idx = page_idx
                self._do_ocr_for_page(page_idx)

    def get_current_page(self):
        """
        判断当前可视区域中, 离“视口中心”最近的那一页, 视为“当前页”。
        """
        view_top = self.canvas.canvasy(0)
        view_bottom = view_top + self.canvas.winfo_height()
        view_center = (view_top + view_bottom) / 2

        closest_index = None
        min_dist = float("inf")

        for i, lbl in enumerate(self.page_labels):
            lbl_top = lbl.winfo_y()
            lbl_bottom = lbl_top + lbl.winfo_height()
            lbl_center = (lbl_top + lbl_bottom) / 2

            dist = abs(lbl_center - view_center)
            if dist < min_dist:
                min_dist = dist
                closest_index = i

        return closest_index

    def _do_ocr_for_page(self, page_index):
        """
        对指定页做 OCR，并打印识别到的文字。
        你也可以把结果显示到文本框、保存到文件等。
        """
        print(f"\n[OCR] 开始识别第 {page_index+1} 页...")

        zoom_factor = 1.5
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        page = self.doc[page_index]
        pix = page.get_pixmap(matrix=mat)
        mode = "RGBA" if pix.alpha else "RGB"
        pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # 如果 tesseract.exe 不在 PATH 中，需要指定路径:
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        # OCR 识别
        text = pytesseract.image_to_string(pil_img, lang='eng')  
        # 如果 PDF 是中文，可以换 lang='chi_sim' (需安装中文语言包)
        message = execute_agent({"content":text[:]},thread_id)
        #print(f"[OCR] 第 {page_index+1} 页识别结果(前300字符):\n{text[:]}")
        print(message)
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
    root = tk.Tk()
    root.title("连续滚动 PDF + OCR 示例")

    pdf_path = r"C:\Users\yysym\Downloads\s10270-020-00777-7.pdf"  # 替换为实际路径
    viewer = ContinuousPDFViewer(root, pdf_path)
    
    root.mainloop()
