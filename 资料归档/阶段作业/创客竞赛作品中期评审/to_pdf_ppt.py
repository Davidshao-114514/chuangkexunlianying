# -*- coding: utf-8 -*-
import os, time, glob
import win32com.client

OUT = os.path.dirname(os.path.abspath(__file__))
app = win32com.client.Dispatch("PowerPoint.Application")
try:
    for src in sorted(glob.glob(os.path.join(OUT, "*中期汇报PPT_V*.pptx"))):
        dst = src[:-5] + ".pdf"
        if os.path.exists(dst):
            os.remove(dst)
        prs = app.Presentations.Open(src, WithWindow=False)
        prs.SaveAs(dst, 32)  # 32 = ppSaveAsPDF
        prs.Close()
        print("PDF:", os.path.basename(dst), os.path.getsize(dst))
finally:
    app.Quit()
    time.sleep(1)
print("done")
