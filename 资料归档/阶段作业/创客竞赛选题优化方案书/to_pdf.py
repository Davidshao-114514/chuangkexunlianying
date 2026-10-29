# -*- coding: utf-8 -*-
import os, sys, time
import win32com.client

OUT = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛选题优化方案书.docx")
dst = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛选题优化方案书.pdf")
if os.path.exists(dst):
    os.remove(dst)
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
try:
    d = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
    d.SaveAs2(os.path.abspath(dst), FileFormat=17)  # wdFormatPDF
    d.Close(False)
finally:
    word.Quit()
    time.sleep(1)
print("PDF:", dst, os.path.exists(dst), os.path.getsize(dst) if os.path.exists(dst) else 0)
