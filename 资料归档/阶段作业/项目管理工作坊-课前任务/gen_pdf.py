# -*- coding: utf-8 -*-
import win32com.client, os, fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\项目管理工作坊-课前任务')
word = win32com.client.Dispatch("Word.Application"); word.Visible = False
try:
    src = os.path.abspath('《创客训练营》2026年项目管理工作坊-课前任务.docx')
    dst = os.path.abspath('《创客训练营》2026年项目管理工作坊-课前任务.pdf')
    if os.path.exists(dst): os.remove(dst)
    doc = word.Documents.Open(src, ReadOnly=True)
    doc.SaveAs2(dst, FileFormat=17); doc.Close(False)
    print('PDF saved')
finally:
    word.Quit()
d = fitz.open(dst)
full = ''.join(p.get_text() for p in d)
print('页数:', len(d), '| KB:', os.path.getsize(dst)//1024)
checks = ['邵子中', '范围蔓延', '关键路径', 'WBS', 'RACI', '先听后决', 'NTC', '六个顶' ,'仿真跑不队',
          '把模糊的愿望', '19 字', '里程碑', '磁吸焊接辅助手电', '泡茶', '外', '阶段 3 固件与功能调校']
ok = True
for k in checks:
    hit = k in full
    ok = ok and hit
    print(('OK  ' if hit else 'MISS'), k)
print('全部通过' if ok else '有缺失')
