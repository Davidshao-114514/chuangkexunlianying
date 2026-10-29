# -*- coding: utf-8 -*-
"""定位并渲染关键页面为 PNG，便于目视检查排版"""
import os, re
import pymupdf

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛资源优化方案书.pdf")
PREV = os.path.join(OUT, "_probe", "pages")
os.makedirs(PREV, exist_ok=True)
d = pymupdf.open(PDF)
for i in range(d.page_count):
    t = d[i].get_text()
    hits = []
    for k in ["表 7　", "表 13　", "表 15　", "图 1　", "表 18　", "表 19　", "图 8　", "表 24　"]:
        if k in t:
            hits.append(k.strip())
    if hits:
        print(f"page {i+1}: {hits}")
d[0].get_pixmap(dpi=100).save(os.path.join(PREV, "p01.png"))
for n in (8, 18, 19, 20, 21, 22, 28):
    if n <= d.page_count:
        d[n - 1].get_pixmap(dpi=110).save(os.path.join(PREV, f"p{n:02d}.png"))
print("rendered:", sorted(os.listdir(PREV)))
