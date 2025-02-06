import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class ContinuousPDFViewer(tk.Frame):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)

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

    def render_all_pages(self):
        for page_index in range(self.total_pages):
            page = self.doc[page_index]
            zoom_factor = 2.0  # 放大倍数可自行调整
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

            # 转为可在 tkinter 中显示的 PhotoImage
            tk_img = ImageTk.PhotoImage(pil_img)
            self.photo_images.append(tk_img)  # 保留引用

            # 用一个 Label 显示当前页
            label = tk.Label(self.pages_frame, image=tk_img, bg="white")
            label.pack(pady=10)  # 页面与页面之间留点空隙

    def _on_mousewheel_windows(self, event):
        """
        鼠标滚轮事件 (Windows).
        在 macOS/Linux 下需要分别使用 <Button-4>/<Button-5>。
        """
        # event.delta 在 Windows 通常是 ±120 的倍数
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_frame_configure(self, event):
        """当内部 frame 大小变化时，更新 Canvas 的滚动区域。"""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("连续滚动 PDF 查看器")

    # 在此替换为你的 PDF 文件路径
    pdf_path = "C:\\Users\\yysym\\Downloads\\s10270-020-00777-7.pdf"

    viewer = ContinuousPDFViewer(root, pdf_path)
    root.mainloop()




#C:\\Users\\yysym\\Downloads\\s10270-020-00777-7.pdf