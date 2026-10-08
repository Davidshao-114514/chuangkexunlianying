# -*- coding: utf-8 -*-
import win32com.client, os
import fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\演示资源')
app = win32com.client.Dispatch("PowerPoint.Application")
try:
    p = os.path.abspath('磁吸焊接辅助手电_开源学习包_演示PPT.pptx')
    dst = os.path.abspath('磁吸焊接辅助手电_开源学习包_演示PPT.pdf')
    prs = app.Presentations.Open(p, ReadOnly=True)
    prs.SaveAs(dst, 32)
    prs.Close()
    print('PDF saved')
finally:
    app.Quit()
d = fitz.open('磁吸焊接辅助手电_开源学习包_演示PPT.pdf')
print('页数:', len(d))
for i in [1, 3, 5, 7]:
    d[i].get_pixmap(dpi=85).save(f'_p{i+1}.png')
print('rendered')
