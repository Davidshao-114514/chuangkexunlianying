# -*- coding: utf-8 -*-
"""思维导图：创新方法 vs 设计思维 对比分析（原创绘制）"""
import os, re
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\创新方法工作坊-课前任务"
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

W, H = 1700, 1400
img = Image.new("RGB", (W, H), (250, 252, 255))
d = ImageDraw.Draw(img)
BLUE = (37, 74, 151); DGRAY = (60, 70, 90); LGRAY = (130, 140, 160)
GREEN = (46, 160, 90); ORANGE = (232, 163, 61); GOLD = (255, 201, 77)

d.text((W/2, 52), "创新方法 vs 设计思维：异同与互补关系（思维导图）", font=F(36, True), fill=BLUE, anchor="mm")
d.line([(W//2, 96), (W//2, H-60)], fill=(200, 208, 225), width=2)

# ---- 顶部共同点 ----
d.rounded_rectangle([300, 118, 1400, 208], radius=20, fill=(240, 247, 240), outline=GREEN, width=3)
d.text((W/2, 140), "共同点", font=F(26, True), fill=GREEN, anchor="mm")
d.text((W/2, 178), "① 都认为创新“可教、可学、有章法”（非天才灵感）　② 都提供结构化的思维路径与操作步骤", font=F(22), fill=DGRAY, anchor="mm")

# ---- 左侧：创新方法 ----
LX = 80
d.rounded_rectangle([LX, 240, 780, 330], radius=16, fill=(232, 163, 61))
d.text((430, 268), "创新方法", font=F(30, True), fill=(255, 255, 255), anchor="mm")
d.text((430, 304), "工具型：结构化提问清单，直接生成改进方案", font=F(20), fill=(255, 255, 255), anchor="mm")
left_items = [
    ("流程特征", "由若干“提问/检查”步骤构成，可单次执行（如检核表 9 问）"),
    ("导向侧重", "方案导向：面向已有对象的结构性改造"),
    ("问题起点", "问题基本明确（“改进智能水杯”“优化快递驿站”）"),
    ("成果形态", "具体改进点/方案清单（如“增加 NFC 刷卡”）"),
    ("适用范围", "“从 1 到 N”：方案优化与拓展"),
    ("代表方法", "SCAMPER、奥斯本检核表法、TRIZ、5W2H/7W5H"),
]
yy = 370
for k, v in left_items:
    d.rounded_rectangle([LX, yy, 780, yy+118], radius=14, fill=(255, 255, 255), outline=ORANGE, width=2)
    d.text((LX+22, yy+22), k, font=F(22, True), fill=(180, 110, 30), anchor="lm")
    for i, ln in enumerate(wrap(d, v, F(19), 620)):
        d.text((LX+22, yy+58+i*26), ln, font=F(19), fill=DGRAY)
    yy += 132

# ---- 右侧：设计思维 ----
RX = 920
d.rounded_rectangle([RX, 240, 1620, 330], radius=16, fill=(74, 144, 226))
d.text((1270, 268), "设计思维", font=F(30, True), fill=(255, 255, 255), anchor="mm")
d.text((1270, 304), "流程型：五阶段系统流程，先定义问题再验证方案", font=F(20), fill=(255, 255, 255), anchor="mm")
right_items = [
    ("流程特征", "共情→定义→构思→原型→测试的完整五阶段，需多轮迭代"),
    ("导向侧重", "用户导向：先理解真实需求，再讨论方案"),
    ("问题起点", "问题模糊（“不知道从哪切入”），起步于用户洞察"),
    ("成果形态", "被验证的需求定义 + 可测试原型"),
    ("适用范围", "“从 0 到 1”：选题定义与方向探索"),
    ("代表方法", "五阶段模型、HMW 提问、同理心地图、MVP"),
]
yy = 370
for k, v in right_items:
    d.rounded_rectangle([RX, yy, 1620, yy+118], radius=14, fill=(255, 255, 255), outline=(74, 144, 226), width=2)
    d.text((RX+22, yy+22), k, font=F(22, True), fill=(30, 90, 170), anchor="lm")
    for i, ln in enumerate(wrap(d, v, F(19), 620)):
        d.text((RX+22, yy+58+i*26), ln, font=F(19), fill=DGRAY)
    yy += 132

# ---- 中部互补关系 ----
cy = 700
d.rounded_rectangle([800, cy-260, 900, cy+60], radius=12, fill=(255, 243, 224), outline=ORANGE, width=2)
d.text((850, cy-190), "互", font=F(26, True), fill=(180, 110, 30), anchor="mm")
d.text((850, cy-130), "补", font=F(26, True), fill=(180, 110, 30), anchor="mm")
d.text((850, cy-70), "关", font=F(26, True), fill=(180, 110, 30), anchor="mm")
d.text((850, cy-10), "系", font=F(26, True), fill=(180, 110, 30), anchor="mm")

# 互补说明条
d.rounded_rectangle([300, 1190, 1400, 1290], radius=18, fill=(240, 244, 252), outline=(74, 144, 226), width=2)
d.text((W/2, 1222), "互补关系：设计思维负责“定义正确的问题”（从 0 到 1），创新方法负责“把问题做到最优”（从 1 到 N）；", font=F(21, True), fill=BLUE, anchor="mm")
d.text((W/2, 1258), "在完整创新流程中，二者交替出现：定义 → 优化 → 验证 → 再优化，共同支撑创新的全周期。", font=F(21), fill=BLUE, anchor="mm")

d.text((W/2, H-36), "绘制说明：左列创新方法（工具型）、右列设计思维（流程型）按五个维度对比；中部标注互补关系。", font=F(17), fill=LGRAY, anchor="mm")

img.save(os.path.join(OUT, "创新方法vs设计思维-思维导图.png"))
print("saved")
