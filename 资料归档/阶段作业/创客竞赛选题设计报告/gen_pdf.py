# -*- coding: utf-8 -*-
import win32com.client, os, fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\创客竞赛选题设计报告')
word = win32com.client.Dispatch("Word.Application"); word.Visible = False
try:
    src = os.path.abspath('磁吸焊接辅助手电-选题设计报告.docx')
    dst = os.path.abspath('1班C组—仿真跑不队—创客竞赛选题设计报告.pdf')
    if os.path.exists(dst): os.remove(dst)
    doc = word.Documents.Open(src, ReadOnly=True)
    doc.SaveAs2(dst, FileFormat=17); doc.Close(False)
    print('PDF saved')
finally:
    word.Quit()
d = fitz.open(dst)
full = ''.join(p.get_text() for p in d)
print('页数:', len(d), '| KB:', os.path.getsize(dst)//1024)
checks = ['CW32L010F8P6', 'SY7200AABC', 'IP5306', 'YHNR3015', 'GW JTLPS1', 'ME6211C', 'DW01',
          'TS24CA', 'BH1750', 'SSD1306', '34 行 56 个位号', 'BOM ≤50 元', '6 颗红色 LED']
ok = True
for k in checks:
    hit = k in full
    ok = ok and hit
    print(('OK  ' if hit else 'MISS'), k)
print('全部通过' if ok else '有缺失')
