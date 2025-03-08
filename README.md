## 环境

- OCR Engine: [tesseract](https://github.com/UB-Mannheim/tesseract/wiki)，下载安装后把路径加到环境里
- Python Package: PyMuPDF, pytesseract, tkinter, python Imaging Library
- langchain package 若干，按需安装

Conda 下安装环境:

`conda env create -f environment.yml`

更新现有 Conda 环境(myenv):

`conda env update --name myenv --file environment.yml --prune`

### Video 前端环境

Node.js 22

```shell
cd client
npm install

# 运行
npm run dev
```

## 本地 socket 连接测试

在[Postman](https://www.postman.com/)新建一个 socket 任务

### Test in Python

Run `main_video.py` as socket test server

Run `socket_client_test.py` to send test case to server and check results in all clients

## PDF in web

Currently change the file path in `PdfReader.tsx` to show your pdf.

```html
<Document
  file={"../../London Visitor Guide.pdf"}
  onLoadSuccess={onDocumentLoadSuccess}
  options={options}
>
  ...
</Document>
```
