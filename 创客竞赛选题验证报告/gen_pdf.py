# -*- coding: utf-8 -*-
import win32com.client, os, fitz
os.chdir(r'C:\Users\35464\Desktop\创客训练营\创客竞赛选题验证报告')
word = win32com.client.Dispatch("Word.Application"); word.Visible = False
try:
    src = os.path.abspath('创客竞赛选题验证报告.docx')
    dst = os.path.abspath('1班C组—仿真跑不队—创客竞赛选题验证报告.pdf')
    if os.path.exists(dst): os.remove(dst)
    doc = word.Documents.Open(src, ReadOnly=True)
    doc.SaveAs2(dst, FileFormat=17); doc.Close(False)
finally:
    word.Quit()
d = fitz.open(dst)
full = ''.join(p.get_text() for p in d)
print('页数:', len(d), '| KB:', os.path.getsize(dst)//1024)
checks = ['仿真跑不队', '邵子中', '李昊桐', '姜亚楷', '磁吸焊接辅助手电', '待验证假设',
          '蓝帽', '黑帽', '绿帽', '调整后推进', 'NTC', '6 颗红色 LED', '虚拟支付', '20 人',
          '5W2H', '300 元', '照妖镜']
ok = True
for k in checks:
    hit = k in full
    ok = ok and hit
    print(('OK  ' if hit else 'MISS'), k)
print('全部通过' if ok else '有缺失')
