import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

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
        self.page_labels = []    # 存放每页对应的 Label，用于计算位置

        # 绑定滚轮 (Windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)

        # 当 pages_frame 大小变化时, 更新 scrollregion
        self.pages_frame.bind("<Configure>", self._on_frame_configure)

        # 一次性渲染全部页面
        self.render_all_pages()

        # 也可以在用户滚动时, 动态显示当前第几页
        # 这里演示在每次鼠标滚动后, 打印当前所在页:
        # 你也可用 tk.Label 放在界面上实时显示
        self.current_page_label = tk.Label(self, text="", bg="yellow")
        self.current_page_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_idletasks()  # 刷新布局，确保 bbox 准确
        self._adjust_window_size()

        # ============ 页数变化回调 =============
        # 用户可以通过 set_on_page_changed(...) 来设置一个回调函数
        self._on_page_changed_callback = None
        self.last_page_idx = None  # 记录上次检测到的“当前页”

        # ============ 滚动停止检测 =============
        self.scroll_stop_timer = None        # 记录定时器的 ID
        self.scroll_stop_delay = 1000        # 停止滚动后等待的毫秒数 (1秒)

    def set_on_page_changed(self, callback):
        """设置当页数变化时要调用的回调函数"""
        self._on_page_changed_callback = callback

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
        """鼠标滚轮滚动(Windows)。"""
        # 1) 正常滚动
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # 滚动后, 计算当前页, 并显示
        self.update_current_page_label()
        
        # 2) 重置定时器
        if self.scroll_stop_timer is not None:
            # 如果之前有定时任务, 先取消
            self.after_cancel(self.scroll_stop_timer)
            self.scroll_stop_timer = None

        # 重新设置一个在1秒后调用的函数
        self.scroll_stop_timer = self.after(self.scroll_stop_delay, self._on_scroll_stopped)

        

    def _on_scroll_stopped(self):
        """
        当用户停止滚动超过1秒后会执行这里:
        在这里再去检测当前页是否变化，触发回调，
        并更新底部标签。
        """
        self.scroll_stop_timer = None  # 清空定时器
        self._check_page_changed()       # 触发回调

    def update_current_page_label(self):
        """计算并在底部标签显示当前页号。"""
        page_idx = self.get_current_page()
        if page_idx is not None:
            self.current_page_label.config(text=f"当前页: {page_idx+1}/{self.total_pages}")
        else:
            self.current_page_label.config(text="无法定位当前页")

    def _check_page_changed(self):
        """检测当前页面有没有变化，如变化则调用回调。"""
        current_idx = self.get_current_page()
        if current_idx is not None and current_idx != self.last_page_idx:
            self.last_page_idx = current_idx
            # 如果有回调函数, 调用它
            if self._on_page_changed_callback:
                self._on_page_changed_callback(current_idx)

    def get_current_page(self):
        """
        判断当前可视区域中, 离“视口中心”最近的那一页, 视为“当前页”。
        如果都不重叠, 可能返回 None, 但在正常布局中不会出现这种情况。
        """

        # 1) 可视区域顶端 & 底端 (在 pages_frame 坐标系下)
        view_top = self.canvas.canvasy(0)
        view_bottom = view_top + self.canvas.winfo_height()
        view_center = (view_top + view_bottom) / 2

        # 2) 遍历每个 Label, 计算它的(上, 下, 中心)位置
        closest_index = None
        min_dist = float("inf")

        for i, lbl in enumerate(self.page_labels):
            # lbl 在 pages_frame 坐标系中的 y 坐标
            lbl_top = lbl.winfo_y()
            lbl_bottom = lbl_top + lbl.winfo_height()
            lbl_center = (lbl_top + lbl_bottom) / 2

            # 计算此页中心和视口中心的距离
            dist = abs(lbl_center - view_center)
            if dist < min_dist:
                min_dist = dist
                closest_index = i

        return closest_index



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
    root.title("连续滚动 PDF 查看器 - 检测当前页")

    pdf_path = r"C:\Users\yysym\Downloads\s10270-020-00777-7.pdf"  # 替换为实际路径
    viewer = ContinuousPDFViewer(root, pdf_path)
    
    def on_page_changed(new_page_index):
        print(f"页面变化了，现在是第 {new_page_index+1} 页！")

    viewer.set_on_page_changed(on_page_changed)

    root.mainloop()
