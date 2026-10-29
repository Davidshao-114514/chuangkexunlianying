# -*- coding: utf-8 -*-
"""docx → PDF（Word COM），并做关键字符串核验"""
import os
import win32com.client

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛资源优化方案书.docx")
DST = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛资源优化方案书.pdf")
if os.path.exists(DST):
    os.remove(DST)
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
try:
    doc = word.Documents.Open(SRC, ReadOnly=True)
    doc.SaveAs2(DST, FileFormat=17)  # wdFormatPDF
    doc.Close(False)
finally:
    word.Quit()
print("PDF saved:", DST, os.path.getsize(DST), "bytes")

import fitz
d = fitz.open(DST)
full = "".join(d[i].get_text() for i in range(d.page_count))
print("页数:", d.page_count)
KEYS = ["创客竞赛资源优化方案书", "关键缺陷清单", "P0（致命缺陷）", "336 人时", "¥8,400", "¥10,680", "78.7%",
        "迭代验证结果汇总表", "基准 → 调整 → 当前", "精益画布 V4.0", "RACI-V", "角色动态调整记录",
        "能力发展雷达图", "200 字以内", "图 1", "图 8", "资源北极星", "协同系数 2.0", "1,604 台",
        "提交清单", "三可追溯", "2.0", "9 处实质性修订", "个人反思报告"]
miss = [k for k in KEYS if k not in full]
print("关键字符串缺失:", miss if miss else "无（全部命中）")
