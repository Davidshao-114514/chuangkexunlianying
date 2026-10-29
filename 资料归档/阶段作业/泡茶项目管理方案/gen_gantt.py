# -*- coding: utf-8 -*-
"""泡茶项目甘特图 v8（课堂 WBS · 300s 压缩版）：时间标注移入左侧任务栏第二行，彻底消除相邻重叠"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\泡茶项目管理方案"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"

def F(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)

W, H = 2100, 1250
img = Image.new("RGB", (W, H), (252, 253, 255))
d = ImageDraw.Draw(img)
RED = (214, 48, 49); BLUE = (52, 108, 176); GRAY = (150, 158, 172)
DGRAY = (55, 65, 85); LGRAY = (120, 130, 150); GOLD = (222, 150, 32)
GREEN = (46, 160, 90)

d.text((W/2, 36), "泡茶项目甘特图（课堂 WBS 流程 · 300s 压缩版）—— 黄山毛峰·浸泡 105s·交付 299s ≤ 300s", font=F(31, True), fill=(31, 56, 100), anchor="mm")

X0, X1 = 700, 2040
t0, t1 = 0, 360
def px(s): return X0 + (s - t0) / (t1 - t0) * (X1 - X0)
Y0 = 200; ROW = 76
d.line([(X0, Y0), (X1, Y0)], fill=DGRAY, width=3)
for s in range(0, 361, 30):
    x = px(s)
    d.line([(x, Y0), (x, Y0 + 10)], fill=DGRAY, width=2)
    d.text((x, Y0 + 30), f"{s}s", font=F(22), fill=DGRAY, anchor="mm")
    if s % 60 == 0 and s:
        d.line([(x, Y0), (x, Y0 + 800)], fill=(228, 232, 242), width=2)
x300 = px(300)
d.line([(x300, Y0 - 20), (x300, Y0 + 820)], fill=RED, width=2)

ms = [("M1", 147, 1), ("M2", 182, 2), ("M3", 299, 1), ("M4", 314, 2)]
for tag, sec, row in ms:
    x = px(sec)
    d.polygon([(x, Y0 - 34), (x + 12, Y0 - 22), (x, Y0 - 10), (x - 12, Y0 - 22)], fill=GOLD)
    d.text((x, Y0 - 96 if row == 1 else Y0 - 56), f"◆{tag}", font=F(22, True), fill=GOLD, anchor="mm")

tasks = [
    ("1　接水——分 160/210ml 刻度线，160ml 入壶", "1.1", 0, 10, True, False),
    ("2　烧水——至壶断电（160ml → 99.6℃）", "1.2", 10, 137, True, False),
    ("3　取茶 2.5g+检视（与 2 并行）", "1.3", 25, 15, False, True),
    ("4　温杯——10ml 开水温壁，倒出", "2.1", 147, 10, True, False),
    ("5　注水 1——50ml 凉水入杯", "2.2", 157, 5, True, False),
    ("6　投茶——2.5g 茶叶入 50ml 凉水中", "2.3", 162, 8, True, False),
    ("7　注水至 8 分满——加剩余开水", "2.4", 170, 12, True, False),
    ("8　浸泡计时——105s（压缩项）", "2.5", 182, 105, True, False),
    ("9　敬茶——呈现到茶客面前", "3.1", 287, 12, True, False),
    ("10　品鉴确认——茶客品尝", "3.2", 299, 15, False, False),
]
BY = Y0 + 90
for i, (name, wbs, st, dur, crit, para) in enumerate(tasks):
    y = BY + i * ROW
    col = RED if crit else (GRAY if para else BLUE)
    x1, x2 = px(st), px(st + dur)
    d.rounded_rectangle([x1, y, x2, y + 46], radius=10, fill=col)
    # 左侧任务栏两行：任务名（上）+ 时间（下），右对齐——全部移出条块区
    namcol = (110, 120, 135) if para else DGRAY
    d.text((X0 - 18, y + 2), name, font=F(20 if not crit else 20), fill=namcol, anchor="rm")
    d.text((X0 - 18, y + 32), f"时间：{st}~{st + dur}s（{dur}s）", font=F(15), fill=(150, 40, 40) if crit else (135, 145, 158), anchor="rm")

seqs = [(1, 2), (2, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]
for a, b in seqs:
    ya = BY + (a - 1) * ROW + 23
    yb = BY + (b - 1) * ROW + 23
    xa = px(tasks[a - 1][2] + tasks[a - 1][3])
    xb = px(tasks[b - 1][2])
    d.line([(xa, ya), (xa + 16, ya), (xa + 16, yb), (xb, yb)], fill=RED, width=3)
    d.polygon([(xb, yb), (xb - 10, yb - 6), (xb - 10, yb + 6)], fill=RED)

ybar = BY + 10 * ROW + 16
d.rounded_rectangle([X0, ybar, X1, ybar + 176], radius=8, fill=(255, 243, 241), outline=RED, width=3)
d.text((X0 + 16, ybar + 34), "关键路径（红）：1→2→4→5→6→7→8→9 = 299s（敬茶＝交付，红线＝300s √ 留 1s）；+10 品鉴共 314s 收尾", font=F(23, True), fill=GREEN)
d.text((X0 + 16, ybar + 92), "唯一压缩项：浸泡 120s→105s（-15s：淡茶偏好，嫩芽香 90s 前释出）。温度链：50ml 凉水+140ml 沸水＝190ml@82℃ √；浸泡后约 75℃ √", font=F(19), fill=DGRAY)
d.text((X0 + 16, ybar + 144), "◆ 里程碑：M1 烧水 147s｜M2 冲泡完成 182s｜M3 交付验收 299s（＝300s 目标）｜M4 品鉴确认 314s", font=F(19), fill=GOLD)

img.save(os.path.join(OUT, "泡茶项目甘特图-课堂WBS300s版.png"))
print("v8 saved")
