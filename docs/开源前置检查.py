# -*- coding: utf-8 -*-
"""开源前置检查：敏感信息扫描（凭据 / 学号 / 文档 ID / 私密路径）

用法：在仓库根目录执行
    python docs/开源前置检查.py
扫描对象：仓库根 *.md + docs/*.md
"""
import os, re, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = []
for f in os.listdir(ROOT):
    if f.endswith(".md"):
        SCAN.append(os.path.join(ROOT, f))
docdir = os.path.join(ROOT, "docs")
if os.path.isdir(docdir):
    for f in sorted(os.listdir(docdir)):
        if f.endswith(".md"):
            SCAN.append(os.path.join(docdir, f))

PATTERNS = [
    ("APIKey/Token", r"(sk-[A-Za-z0-9]{10,}|api[_-]?key\s*[:=]\s*\S+|token\s*[:=]\s*['\"]?\w{16,})"),
    ("在线文档ID", r"(DT0[A-Za-z0-9]{8,}|docs\.qq\.com/\w+/DT\w+)"),
    ("学号", r"U20\d{8}"),
    ("手机号", r"1[3-9]\d{9}"),
    ("邮箱", r"[\w.+-]+@[\w-]+\.[a-z]{2,}"),
    ("本机绝对路径", r"[A-Z]:\\+Users\\+\w+"),
    ("口令字段", r"(password|passwd|口令)\s*[:=]"),
]

total = 0
for path in SCAN:
    try:
        s = io.open(path, encoding="utf-8").read()
    except Exception as e:
        print("读取失败", path, e)
        continue
    hits = []
    for name, pat in PATTERNS:
        for m in re.finditer(pat, s, re.I):
            hits.append((name, m.group(0)[:40]))
    if hits:
        total += len(hits)
        print(f"[!] {os.path.relpath(path, ROOT)}")
        for n, v in hits[:8]:
            print(f"    - {n}: {v}")
    else:
        print(f"[OK] {os.path.relpath(path, ROOT)}")
print("\n命中合计:", total, "→", "需要处理" if total else "可安全公开")
