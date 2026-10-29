# -*- coding: utf-8 -*-
"""提取 PDF 文本（RACI / 角色 / 资源相关页）"""
import sys, os
import fitz

for path in sys.argv[1:]:
    print("#" * 70)
    print("FILE:", os.path.basename(path))
    d = fitz.open(path)
    print("pages:", d.page_count)
    for i in range(d.page_count):
        t = d[i].get_text()
        if any(k in t for k in ("RACI", "角色", "资源", "分工", "职责")):
            print(f"---------- page {i+1} ----------")
            print(t[:2600])
