# -*- coding: utf-8 -*-
"""磁吸焊接辅助手电 · 精益画布 v2（官方五列布局：客户细分通高列；文字按格宽断行）"""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\作品选题评审-课前任务"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"; FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FONT_B if b else FONT_R, sz)

W, H = 2000, 1420
img = Image.new("RGB", (W, H), (250, 251, 253))
d = ImageDraw.Draw(img)
RED = (214, 48, 49); DGRAY = (50, 60, 80); LGRAY = (130, 138, 152)
BLUE = (31, 56, 100); GOLD = (222, 150, 32)

d.text((W/2, 40), "磁吸焊接辅助手电 —— 精益画布 V1.0（仿真跑不队）", font=F(38, True), fill=BLUE, anchor="mm")
d.text((W/2, 94), "🔴 红=待验证（课前阶段全部待验证；H-001/H-002/H-005 为 ICE“立即验证”优先级）｜逻辑连线：①→②→③，④→③，⑦→⑥，⑨↔⑧", font=F(20), fill=LGRAY, anchor="mm")

def cell(x, y, w, h, title, lines, tl=None, tsize=25, lsize=18):
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, outline=BLUE, width=3, fill=(255, 255, 255))
    d.text((x + 14, y + 10), title, font=F(tsize, True), fill=BLUE)
    yy = y + 10 + tsize + 10
    if tl:
        d.text((x + 14, yy), tl, font=F(16, True), fill=RED); yy += 26
    maxchars = max(4, int((w - 30) / lsize * 1.02))
    for seg in lines:
        for ln in [seg[i:i + maxchars] for i in range(0, len(seg), maxchars)]:
            if yy > y + h - 24: break
            d.text((x + 14, yy), ln, font=F(lsize), fill=DGRAY)
            yy += lsize + 7

XS = [60, 490, 920, 1350, 1660]; WS = [400, 400, 400, 280, 320]
Y1, Y2, HROW = 130, 790, 550
y_mid_1 = Y1 + 310

# 上排 4 格
cell(XS[0], Y1, WS[0], HROW, "① 问题（3 痛点，按严重性）", [
    "【1】焊点照明被手/烙铁遮挡，" "阴影死角（84.13% 每周焊≥3 次）",
    "【2】台灯占空间、灯臂僵直不可" "瞄准（68.25% 问卷反馈）",
    "【3】廉价灯不稳偏斜；专业灯 300+ 元" "（61.11% / 54.76%）",
], "🔴（H-001/H-002）")
cell(XS[1], Y1, WS[1], HROW, "② 解决方案（MVP 对应）", [
    "① 磁吸底座+万向柔臂（N42 磁铁" "≥2.5kg、悬停漂移<1°）→ 解决遮挡",
    "② 无级调光（SY7200A 恒流+" "20kHz PWM）→ 亮度可调",
    "③ LED 状态指示（4 电量+2 充电）" "+ OLED 扩展接口（H1 排针）",
], "🔴（H-002）")
cell(XS[2], Y1, WS[2], HROW, "③ 独特价值主张", [
    "【手工焊接者】通过【能自己站住的" "第三只手】实现【焊点照明零遮挡、",
    "桌面零占用】，相比【台灯/廉价灯】" "我们【吸附即用、万向瞄准、百元内",
    "（59-79 元，比专业机床灯便宜 75%+）】",
], "🔴（H-001）")
cell(XS[3], Y1, WS[3], HROW, "④ 竞争优势", [
    "① 基地“老带新”渠道" "（年 300+ 新生）",
    "② 34 行 56 位号 BOM" "供应链锁定",
    "③ 万向悬停实用新型" "（申请中）",
], tsize=23, lsize=17)

# 下排 4 格
cell(XS[0], Y2, WS[0], HROW, "⑤ 关键指标", [
    "北极星：周活跃焊接时长" "（周使用≥3 小时占比≥60%）",
    "辅助：30 天留存、NPS≥40",
])
cell(XS[1], Y2, WS[1], HROW, "⑥ 渠道", [
    "线下：电工基地/电赛集训营试用",
    "线上：电赛 QQ 群、B 站教程、" "淘宝/闲鱼 DIY 店",
    "种子用户定向邀约",
])
cell(XS[2], Y2, WS[2], HROW, "⑧ 成本结构", [
    "固定：PCBA 打样 500 元+结构开模分摊",
    "可变：BOM≈45 元/台+物流 6 元+包装 3 元",
    "隐性：3C 认证 500 元/次+售后 3% 换件",
], "🔴（H-005）")
cell(XS[3], Y2, WS[3], HROW, "⑨ 收入来源", [
    "标准版 79 元/青春版 59 元" "（毛利 40-45%）",
    "DIY 套件 49 元（引流）",
    "远期：OPC UA 数据服务",
], "🔴（H-001/H-005）", tsize=23, lsize=17)

# ⑦ 客户细分（右侧通高列）
cell(XS[4], Y1, WS[4], (Y2 + HROW) - Y1, "⑦ 客户细分", [
    "① 高校电子/电赛学生：每周焊" "接≥3 次、专业实训用户",
    "② DIY 极客：焊台在家、愿为" "效率付费",
    "③ 实验室研发工程师：工位狭" "小、批量调试",
], "🔴（H-001/H-003）", tsize=23, lsize=17)

# ===== 逻辑连线箭头 =====
def arrow(pts, col=RED, w=5):
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=col, width=w)
    x2, y2 = pts[-1]; x1, y1 = pts[-2]
    ang = math.atan2(y2 - y1, x2 - x1)
    px_, py_ = x2 - 14 * math.cos(ang), y2 - 14 * math.sin(ang)
    d.polygon([(x2, y2), (px_ - 8 * math.sin(ang), py_ + 8 * math.cos(ang)), (px_ + 8 * math.sin(ang), py_ - 8 * math.cos(ang))], fill=col)
# ①→②
arrow([(XS[0] + WS[0], y_mid_1), (XS[1], y_mid_1)])
# ②→③
arrow([(XS[1] + WS[1], y_mid_1), (XS[2], y_mid_1)])
# ④→③（优势支撑价值主张）
arrow([(XS[3], y_mid_1), (XS[2] + WS[2], y_mid_1)])
# ⑨→⑧（收入→成本：循环）
arrow([(XS[3], Y2 + 260), (XS[2] + WS[2], Y2 + 260)])
# ⑧→⑨ 反向（成本支撑收入）
arrow([(XS[2] + WS[2], Y2 + 320), (XS[3], Y2 + 320)])
# ⑦→⑥（客户细分→渠道：沿上下排缝隙走折线）
gap_y = Y1 + HROW + 12
arrow([(XS[4], gap_y), (XS[1] + WS[1] + 10, gap_y), (XS[1] + WS[1] + 10, Y2), (XS[1] + WS[1], Y2 + 8)])

d.text((XS[0], Y2 + HROW + 26), "编号：① 问题 ② 解决方案 ③ 独特价值主张 ④ 竞争优势 ⑤ 关键指标 ⑥ 渠道 ⑦ 客户细分 ⑧ 成本结构 ⑨ 收入来源｜数据来源标注：[1]126 份问卷(2026-08,问卷星) [2]BOM 实测(34 行/56 位号) [3]价值主张句式对应任务书 [4]基地渠道调研 [5]北极星待验证 [6]目标用户聚集地 [7]远期生态", font=F(17), fill=LGRAY)

img.save(os.path.join(OUT, "磁吸焊接辅助手电-精益画布.png"))
print("canvas v2 saved")
