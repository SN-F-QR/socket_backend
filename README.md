## 环境
- OCR Engine: [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)，下载安装后把路径加到环境里
- Python Package: PyMuPDF, pytesseract, tkinter, python Imaging Library
## 清单
- Http连接到OpenAI，将OCR内容传给OpenAI并接收返回
- 用socket把OpenAI的返回值传给HoloLens
