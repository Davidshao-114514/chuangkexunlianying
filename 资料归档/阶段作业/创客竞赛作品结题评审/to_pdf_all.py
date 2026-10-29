# -*- coding: utf-8 -*-
import os, glob, time
import win32com.client

OUT = os.path.dirname(os.path.abspath(__file__))
word = win32com.client.Dispatch("Word.Application"); word.Visible = False
try:
    for src in glob.glob(os.path.join(OUT, "*.docx")):
        if os.path.basename(src).startswith("~$"):
            continue
        dst = src[:-5] + ".pdf"
        if os.path.exists(dst): os.remove(dst)
        d = word.Documents.Open(os.path.abspath(src), ReadOnly=True)
        d.SaveAs2(os.path.abspath(dst), FileFormat=17)
        d.Close(False)
        print("PDF:", os.path.basename(dst), os.path.getsize(dst))
finally:
    word.Quit(); time.sleep(1)

app = win32com.client.Dispatch("PowerPoint.Application")
try:
    for src in sorted(glob.glob(os.path.join(OUT, "*结题汇报PPT*.pptx"))):
        dst = src[:-5] + ".pdf"
        if os.path.exists(dst): os.remove(dst)
        prs = app.Presentations.Open(src, WithWindow=False); prs.SaveAs(dst, 32); prs.Close()
        print("PDF:", os.path.basename(dst), os.path.getsize(dst))
finally:
    app.Quit(); time.sleep(1)

import fitz
for f in sorted(glob.glob(os.path.join(OUT, "*.pdf"))):
    d = fitz.open(f)
    bad = 0
    for i, p in enumerate(d, 1):
        W, H = p.rect.width, p.rect.height
        for b in p.get_text("blocks"):
            if b[4].strip() and (b[2] > W - 5 or b[3] > H - 5):
                bad += 1
    print(f"{os.path.basename(f):<58} {d.page_count:>3} 页  越界 {bad}")
print("done")
