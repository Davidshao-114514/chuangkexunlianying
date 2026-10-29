# -*- coding: utf-8 -*-
import win32com.client, os, fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\泡茶项目管理方案')
word = win32com.client.Dispatch("Word.Application"); word.Visible = False
try:
    src = os.path.abspath('《泡茶项目管理方案》投标文件-黄山毛峰300s版.docx')
    dst = os.path.abspath('第三组—黄山毛峰—泡茶项目管理方案300s版.pdf')
    if os.path.exists(dst): os.remove(dst)
    doc = word.Documents.Open(src, ReadOnly=True)
    doc.SaveAs2(dst, FileFormat=17); doc.Close(False)
    print('PDF saved')
finally:
    word.Quit()
d = fitz.open(dst)
full = ''.join(p.get_text() for p in d)
print('页数:', len(d), '| KB:', os.path.getsize(dst)//1024)
checks = ['300s', '105s', '300 秒', '零缓冲', '26.22', '52.4%', '105. 秒' ,'83℃', '中投法',
          '15.75', 'R05', '高优先级', '300s 严格版', '跟踪折质']
ok = True
for k in checks:
    hit = k in full
    ok = ok and hit
    print(('OK  ' if hit else 'MISS'), k)
print('全部通过' if ok else '有缺失')
