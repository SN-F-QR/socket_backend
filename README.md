## 环境

- OCR Engine: [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)，下载安装后把路径加到环境里
- Python Package: PyMuPDF, pytesseract, tkinter, python Imaging Library
- langchain package 若干，按需安装

Conda 下安装环境:

`conda env create -f environment.yml`

更新现有 Conda 环境(myenv):

`conda env update --name myenv --file environment.yml --prune`
##本地socket连接测试
在[Postman](https://www.postman.com/)新建一个socket任务

## 清单

- Http 连接到 OpenAI，将 OCR 内容传给 OpenAI 并接收返回
- 完善跟 hololens 的 socket 通讯
- Scrollbar detect
