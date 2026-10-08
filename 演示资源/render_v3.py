# -*- coding: utf-8 -*-
import win32com.client, os, glob
import fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\演示资源')
app = win32com.client.Dispatch("PowerPoint.Application")
try:
    p = os.path.abspath('磁吸焊接辅助手电_可复制的创业逻辑_汇报PPT.pptx')
    dst = os.path.abspath('磁吸焊接辅助手电_可复制的创业逻辑_汇报PPT.pdf')
    prs = app.Presentations.Open(p, ReadOnly=True)
    n = prs.Slides.Count
    prs.SaveAs(dst, 32)
    prs.Close()
    print('PDF saved, PowerPoint 内页数:', n)
finally:
    app.Quit()
for f in glob.glob('_v3_*.png'):
    os.remove(f)
d = fitz.open('磁吸焊接辅助手电_可复制的创业逻辑_汇报PPT.pdf')
print('PDF 页数:', len(d))
for i in range(len(d)):
    d[i].get_pixmap(dpi=80).save(f'_v3_{i+1:02d}.png')
print('rendered all')
