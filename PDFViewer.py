import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class ContinuousPDFViewer(tk.Frame):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.master = master  # 方便后面调用 geometry()

        # 打开 PDF
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

        # ============ 1. Canvas + Scrollbar ============
        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 在 Canvas 内创建一个装载所有页面的 frame
        self.pages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor="nw")

        # 用于保存每页的 PhotoImage 引用，避免被垃圾回收
        self.photo_images = []

        # 绑定滚轮 (Windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)

        # 当 pages_frame 大小变化时，更新滚动区域
        self.pages_frame.bind("<Configure>", self._on_frame_configure)

        # ============ 2. 一次性渲染全部页面 ============
        self.render_all_pages()

        # ============ 3. 渲染完后，自动调整窗口大小 ============
        self.update_idletasks()  # 刷新布局，确保 bbox 准确
        self._adjust_window_size()

    def render_all_pages(self):
        """一次性渲染 PDF 所有页面到 pages_frame 中。"""
        for page_index in range(self.total_pages):
            page = self.doc[page_index]
            
            # 放大倍数可自行调整
            zoom_factor = 2.0  
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            pix = page.get_pixmap(matrix=mat)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

            # 转为可在 tkinter 中显示的 PhotoImage
            tk_img = ImageTk.PhotoImage(pil_img)
            self.photo_images.append(tk_img)  # 保留引用，防止被回收

            # 用一个 Label 显示当前页
            label = tk.Label(self.pages_frame, image=tk_img, bg="white")
            label.pack(pady=10)  # 页面与页面之间留点空隙

    def _on_frame_configure(self, event):
        """当内部 frame 大小变化时，更新 Canvas 的滚动区域。"""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel_windows(self, event):
        """
        鼠标滚轮事件 (Windows).
        如果在 macOS/Linux 下，需要使用 <Button-4>/<Button-5>。
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _adjust_window_size(self):
        """
        计算当前 Canvas 内部所有内容的总 bounding box，
        并调整窗口大小。
        """
        # bbox("all") 返回 (x1, y1, x2, y2)
        x1, y1, x2, y2 = self.canvas.bbox("all")
        total_width = x2 - x1
        total_height = y2 - y1

        # 如果你真的想让窗口和所有内容一样大：
        # 可能会超出屏幕，这里只是示例：
        self.master.geometry(f"{total_width}x{total_height}")
        
        # ---------------------------
        # 如果你只想限制到比如屏幕高的一半：
        # screen_w = self.master.winfo_screenwidth()
        # screen_h = self.master.winfo_screenheight()
        # # 窗口最大不能超过屏幕
        # window_width = min(total_width, screen_w)
        # window_height = min(total_height, screen_h // 2)
        #
        # self.master.geometry(f"{window_width}x{window_height}")
        # ---------------------------


if __name__ == "__main__":
    root = tk.Tk()
    root.title("连续滚动 PDF 查看器 - 自动调整窗口大小")

    pdf_path = r"C:\Users\yysym\Downloads\s10270-020-00777-7.pdf"
    viewer = ContinuousPDFViewer(root, pdf_path)
    root.mainloop()