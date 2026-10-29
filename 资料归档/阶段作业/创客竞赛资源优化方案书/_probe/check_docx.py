# -*- coding: utf-8 -*-
"""校验：docx 中表号/图号的生成顺序与正文引用是否一致"""
import re
from docx import Document

p = r"C:\Users\35464\Desktop\创客训练营\创客竞赛资源优化方案书\1班C组—仿真跑不队—创客竞赛资源优化方案书.docx"
d = Document(p)
texts = [x.text.strip() for x in d.paragraphs]
caps = [(i, t) for i, t in enumerate(texts) if re.match(r"^表 \d+　", t)]
refs = [(i, t) for i, t in enumerate(texts) if re.search(r"表 \d+", t) and not re.match(r"^表 \d+　", t)]
print("=== 表标题（生成顺序） ===")
for t in [c[1] for c in caps]:
    print("  ", t[:80])
print("\n=== 正文中的表号引用 ===")
for i, t in refs:
    for m in re.finditer(r"表 \d+(?=[^\d]|$)", t):
        print(f"  [{m.group(0)}] …{t[max(0,m.start()-42):m.start()+14]}…")
print("\n=== 图号引用 ===")
figs = sorted(set(re.findall(r"图 \d", " ".join(texts))))
print("  ", figs)
print("\n表标题总数:", len(caps))
