# -*- coding: utf-8 -*-
"""提取附件 PPT 全文，定位“劝学任务”相关页"""
import sys, os
from pptx import Presentation

path = sys.argv[1]
prs = Presentation(path)
print("幻灯片总数:", len(prs.slides))
for i, slide in enumerate(prs.slides, 1):
    texts = []
    for sh in slide.shapes:
        if getattr(sh, "has_table", False) and sh.has_table:
            for r in sh.table.rows:
                cells = [c.text.strip().replace("\n", " ") for c in r.cells]
                texts.append("[T] " + " | ".join(cells))
        if sh.has_text_frame and sh.text_frame.text.strip():
            texts.append(sh.text_frame.text)
        if sh.shape_type == 13 or getattr(sh, "has_text_frame", None) is None:
            pass
    body = "\n".join(texts)
    print("=" * 78)
    print(f"---- Slide {i} ----")
    print(body[:3000])
