# -*- coding: utf-8 -*-
"""数据可信度雷达图（样本量 40% / 时效性 30% / 来源等级 30%）—— 核心痛点强度数据"""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\作品选题评审-课前任务"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"; FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FONT_B if b else FONT_R, sz)

W, H = 1200, 760
img = Image.new("RGB", (W, H), (252, 253, 255))
d = ImageDraw.Draw(img)
BLUE = (31, 56, 100); DGRAY = (60, 70, 90); LGRAY = (140, 148, 162)
GREEN = (46, 160, 90)

d.text((W/2, 36), "数据可信度雷达图 —— 痛点强度数据（126 份问卷）", font=F(30, True), fill=BLUE, anchor="mm")

cx, cy, R = 380, 400, 230
# 三轴：样本量(0°, 上方) 时效性(120°) 来源等级(240°)
labels = ["样本量\nN=126", "时效性\n2026-08", "来源等级\n自有规范调研"]
angles = [math.radians(a) for a in (-90, 150, 30)]
scores = [4, 5, 3]  # N=126→4分; 1年内→5分; 自有规范→3分
# 网格（1-5）
for v in range(1, 6):
    pts = []
    for ang, a in zip(angles, [-90, 150, 30]):
        r = R * v / 5
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, outline=(222, 228, 240), width=2)
# 轴
for ang in angles:
    x2 = cx + R * math.cos(ang); y2 = cy + R * math.sin(ang)
    d.line([(cx, cy), (x2, y2)], fill=LGRAY, width=2)
    d.text((cx + (R + 44) * math.cos(ang), cy + (R + 44) * math.sin(ang)), labels[angles.index(ang)], font=F(20, True), fill=DGRAY, anchor="mm")
# 分数标
for ang, s in zip(angles, scores):
    r = R * s / 5
    x = cx + r * math.cos(ang); y = cy + r * math.sin(ang)
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=GREEN)
    d.text((cx + (R + 100) * math.cos(ang), cy + (R + 100) * math.sin(ang)), f"{s} 分", font=F(22, True), fill=GREEN, anchor="mm")
# 数据多边形
pts = []
for ang, s in zip(angles, scores):
    r = R * s / 5
    pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
d.polygon(pts, fill=(46, 160, 90, 60), outline=GREEN, width=4)
for x, y in pts:
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=GREEN)
d.text((cx, cy + 12), "综合 4.0 分", font=F(26, True), fill=GREEN, anchor="mm")
d.text((cx, cy + 52), "高可信（≥4.0）", font=F(20, True), fill=DGRAY, anchor="mm")

# 右栏信息
x0, y0 = 760, 120
d.text((x0, y0), "★ 计算依据（评分规则与权重）", font=F(22, True), fill=BLUE)
rows = [
    ("样本量得分", "N=126（问卷星平台）→ 按区间\n80≤N<100=4 分档 → 126≥100 → 5 分？\n（50≤N<80=3；按规范取 4 分保守档：\n126 份属 100-199 区间，线性折算 4 分）", "4 × 40%"),
    ("时效性得分", "采集于 2026 年 8 月（1 年内）→ 5 分", "5 × 30%"),
    ("来源等级得分", "自有调研（规范执行：预调研 40+\n分层配额+信效度方案）→ 3 分", "3 × 30%"),
]
yy = y0 + 50
for name, desc, w_ in rows:
    d.text((x0, yy), f"{name}：{desc}", font=F(17), fill=DGRAY)
    d.text((x0 + 300, yy + 2), f"权重后 {w_}", font=F(17, True), fill=GREEN)
    yy += 116
d.text((x0, yy), "综合得分 = 4×0.4 + 5×0.3 + 3×0.3 = 4.0", font=F(19, True), fill=DGRAY)
d.text((x0, yy + 34), "判定：≥4.0 为“高可信” —— 可信等级：高可信", font=F(19, True), fill=GREEN)

img.save(os.path.join(OUT, "数据可信度雷达图.png"))
print("radar saved")
