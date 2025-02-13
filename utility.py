import fitz  # PyMuPDF
from PIL import Image
import pytesseract


def ocr_page(page):
    """
    对指定页进行 OCR
    page: from fitz.open
    """
    zoom_factor = 1.5
    mat = fitz.Matrix(zoom_factor, zoom_factor)
    pix = page.get_pixmap(matrix=mat)
    mode = "RGBA" if pix.alpha else "RGB"
    pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

    # 如果 tesseract.exe 不在 PATH 中，需要指定路径:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    )

    # OCR 识别
    return pytesseract.image_to_string(pil_img, lang="eng")
