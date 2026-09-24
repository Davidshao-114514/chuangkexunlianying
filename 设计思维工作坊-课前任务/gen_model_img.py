# -*- coding: utf-8 -*-
"""设计思维五阶段模型图（原创绘制）v3 —— 卡片内逐行渲染，杜绝重叠"""
import os, math, re
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\设计思维工作坊-课前任务"
os.makedirs(OUT, exist_ok=True)
FONT_R = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"

def F(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)

def wrap(d, text, font, max_w):
    toks = [t for t in re.split(r'(?<=[，。；、：！？…—\s])', text) if t]
    if not toks: toks = [text]
    lines, cur = [], ""
    for t in toks:
        if d.textlength(cur + t, font=font) <= max_w: cur += t
        else:
            if cur: lines.append(cur); cur = ""
            if d.textlength(t, font=font) > max_w:
                for ch in t:
                    if d.textlength(cur + ch, font=font) <= max_w or not cur: cur += ch
                    else: lines.append(cur); cur = ch
            else: cur = t
    if cur: lines.append(cur)
    return lines

W, H = 1700, 1010
img = Image.new("RGB", (W, H), (250, 252, 255))
d = ImageDraw.Draw(img)
BLUE = (37, 74, 151); DGRAY = (60, 70, 90); LGRAY = (130, 140, 160)

d.text((W/2, 46), "斯坦福设计思维五阶段模型（原创绘制）", font=F(38, True), fill=BLUE, anchor="mm")
d.text((W/2, 94), "五阶段 · 核心目标 · 典型工具 · 阶段间输入→输出", font=F(22), fill=LGRAY, anchor="mm")

stages = [
    ("共情", "Empathize", "洞察用户的深层需求", "用户访谈 / 同理心地图", (74, 144, 226)),
    ("定义", "Define", "聚焦关键问题（机会）", "HMW 提问 / 用户画像", (124, 179, 66)),
    ("构思", "Ideate", "发散产生大量解决方案", "头脑风暴 / 思维导图", (232, 163, 61)),
    ("原型", "Prototype", "把想法做成可测试的雏形", "快速原型 / 纸面原型", (180, 120, 220)),
    ("测试", "Test", "用真实反馈验证并迭代", "可用性测试 / 访谈验证", (220, 100, 100)),
]
inputs = ["问题领域", "用户需求数据集", "聚焦的 HMW 问题", "候选方案集", "可测试的原型"]
outputs = ["用户需求数据集", "聚焦的 HMW 问题", "候选方案集", "可测试的原型", "验证结论 / 迭代方向"]
arrow_lbl = ["用户需求数据集", "聚焦的 HMW 问题", "候选方案集", "可测试的原型"]

bw, bh, gap = 250, 400, 110
bx0 = (W - 5*bw - 4*gap) // 2
y0 = 150

for i, (name, en, goal, tool, col) in enumerate(stages):
    x = bx0 + i * (bw + gap)
    d.rounded_rectangle([x, y0, x + bw, y0 + bh], radius=16, fill=(255, 255, 255), outline=col, width=3)
    d.rounded_rectangle([x, y0, x + bw, y0 + 64], radius=16, fill=col)
    d.rectangle([x, y0 + 32, x + bw, y0 + 64], fill=col)
    d.text((x + bw/2, y0 + 18), f"第{i+1}阶段", font=F(17, True), fill=(255,255,255), anchor="mm")
    d.text((x + bw/2, y0 + 45), f"{name}  {en}", font=F(24, True), fill=(255,255,255), anchor="mm")

    # ---- 逐行构建卡片内容（行高严格递增，不重叠）----
    lines = []
    lines.append(("核心目标：", F(17, True), DGRAY, 0))
    for ln in wrap(d, goal, F(17), bw - 32):
        lines.append((ln, F(17), DGRAY, 0))
    lines.append(("典型工具：", F(17, True), DGRAY, 0))
    for ln in wrap(d, tool, F(16), bw - 32):
        lines.append((ln, F(16), DGRAY, 0))
    lines.append((f"输入 ← {inputs[i]}", F(15), (110, 125, 150), 1))
    lines.append((f"输出 → {outputs[i]}", F(15), (110, 125, 150), 1))

    yy = y0 + 84
    for txt, font, colr, is_io in lines:
        d.text((x + 16, yy), txt, font=font, fill=colr)
        yy += 32 if is_io else 30

    if i < 4:
        ax1, ax2 = x + bw + 10, x + bw + gap - 10
        ay = y0 + bh // 2
        d.line([(ax1, ay), (ax2, ay)], fill=col, width=5)
        for da in (2.5, -2.5):
            hx = ax2 - 15 * math.cos(da)
            hy = ay - 15 * math.sin(da)
            d.line([(ax2, ay), (hx, hy)], fill=col, width=5)
        lbl = arrow_lbl[i]
        f_lbl = F(12, True)
        wl = d.textlength(lbl, font=f_lbl) + 12
        d.rounded_rectangle([ax1 + gap/2 - wl/2, ay - 52, ax1 + gap/2 + wl/2, ay - 26],
                            radius=7, fill=(245, 248, 255), outline=col, width=1)
        d.text((ax1 + gap/2, ay - 39), lbl, font=f_lbl, fill=col, anchor="mm")

# 迭代反馈箭头（测试 → 共情）
fy = y0 + bh + 56
d.line([(bx0 + 4*bw + 3*gap, y0 + bh), (bx0 + 4*bw + 3*gap, fy), (bx0 - 8, fy), (bx0 - 8, y0 + bh)],
       fill=(220, 100, 100), width=4)
d.polygon([(bx0 - 16, y0 + bh + 24), (bx0 - 8, y0 + bh), (bx0 - 0, y0 + bh + 24)], fill=(220, 100, 100))
d.text((W/2 + 60, fy + 24), "循环箭头：测试阶段的“验证结论 / 迭代方向”反馈回共情与定义，形成迭代（非一次性线性流程）",
       font=F(19, True), fill=(220, 100, 100), anchor="mm")

d.text((W/2, H - 40), "绘制说明：五阶段按“输入→输出”串联；阶段间箭头上方标注流程中的核心产出物；红色循环箭头表示测试结论回流，迭代深化对用户的理解。",
       font=F(18), fill=LGRAY, anchor="mm")

img.save(os.path.join(OUT, "设计思维五阶段模型图.png"))
print("saved v3")
