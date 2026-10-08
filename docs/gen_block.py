# -*- coding: utf-8 -*-
"""系统框图 v2（最终硬件版）：电池直供 + BGR 采样 + RY3730×2 + 8kHz 调光 + CH1115 + 3 键 + Flash 记忆"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\docs"
os.makedirs(OUT, exist_ok=True)
FONT_R = r"C:\Windows\Fonts\msyh.ttc"; FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FONT_B if b else FONT_R, sz)

W, H = 1960, 1240
img = Image.new("RGB", (W, H), (252, 253, 255))
d = ImageDraw.Draw(img)
NAVY = (31, 56, 100); DGRAY = (60, 70, 90); LGRAY = (140, 148, 162)
BLUE = (52, 108, 176); GREEN = (46, 160, 90); ORANGE = (232, 106, 32); PURPLE = (120, 84, 176)

d.text((W/2, 40), "磁吸焊接辅助手电 · 系统框图（最终硬件版）", font=F(36, True), fill=NAVY, anchor="mm")
d.text((W/2, 86), "CW32L010F8（HSI 48MHz 无晶振，锂电池直供）｜双路 PWM 8kHz/6000 级｜磁吸 4pin 吸附检测（100ms 去抖）｜BGR 反推电压｜Flash 亮度记忆", font=F(19), fill=LGRAY, anchor="mm")

def box(x, y, w, h, title, lines, col=BLUE, fill=(255, 255, 255), ts=21, ls=16):
    d.rounded_rectangle([x, y, x+w, y+h], radius=12, outline=col, width=3, fill=fill)
    d.text((x+w/2, y+22), title, font=F(ts, True), fill=col, anchor="mm")
    yy = y + 50
    for ln in lines:
        d.text((x+w/2, yy), ln, font=F(ls), fill=DGRAY, anchor="mm")
        yy += ls + 8

def arrow(pts, col=DGRAY, w=4):
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=col, width=w)
    import math
    x1, y1 = pts[-2]; x2, y2 = pts[-1]
    ang = math.atan2(y2-y1, x2-x1)
    p1 = (x2-13*math.cos(ang), y2-13*math.sin(ang))
    d.polygon([(x2, y2), (p1[0]-7*math.sin(ang), p1[1]+7*math.cos(ang)), (p1[0]+7*math.sin(ang), p1[1]-7*math.cos(ang))], fill=col)

# ===== 电源域（左下）
box(70, 820, 360, 210, "① 供电与充电", [
    "TYPE-C 6P 输入",
    "充电/升压管理（含电量指示）",
    "18650 锂电池",
    "→ VBAT 直供 MCU（无稳压器）",
    "→ 3V3 轨（CE=PB04 控制）",
], col=ORANGE)
box(70, 1060, 360, 130, "② 3V3 轨", [
    "仅给磁吸口灯端供电",
    "关机拉低 CE → 彻底断电",
], col=ORANGE)

# ===== 主控（中）
box(700, 380, 560, 330, "CW32L010F8  主控（TSSOP-20）", [
    "HSI 48MHz（无外部晶振，OSC± 复用）",
    "VBAT 直供（无 LDO）",
    "BTIM1 1ms 时基分频调度：",
    "1ms 时基/关屏倒计时 · 5ms 按键+检测",
    "50ms 电池采样+过放保护 · 200ms 界面刷新",
    "主循环只做屏刷（CH1115 慢速刷屏）",
    "输出 = 电源 × 点亮 × 亮度 × 已吸附",
], col=NAVY, fill=(240, 245, 255), ts=22, ls=17)

# ===== 输出域（右上）
box(1330, 360, 550, 180, "③ 双路调光输出", [
    "PWM1：PB01 = ATIM_CH2 → RY3730 → 组A",
    "PWM2：PA03 = ATIM_CH3 → RY3730 → 组B",
    "8kHz / ARR=5999 → 6000 级分辨率",
    "亮度下限 3%（低于会频闪）",
], col=GREEN, ts=21, ls=16)
box(1330, 580, 550, 180, "④ 磁吸 4pin 接口（每灯组）", [
    "①3V3  ②GND  ③LED−（PWM 驱动）  ④DET",
    "DET：灯端 3V3 → 吸附=高电平",
    "未吸附不输出（安全）；脱落即灭",
    "检测去抖 100ms（比按键 15ms 长）",
], col=GREEN, ts=21, ls=16)
box(1330, 800, 550, 160, "⑤ 吸附检测（复用 OSC±）", [
    "组1：PA01（OSC−）｜组2：PA00（OSC+）",
    "外挂款占用；内置款可作按键",
], col=GREEN, ts=20, ls=16)

# ===== 人机域（左上）
box(70, 360, 430, 210, "⑥ 按键（3 键复合语义）", [
    "PB03 开关机（含唤醒，上升沿）",
    "PA04 亮度−（单击/长按/双击）",
    "PA05 亮度+（单击/长按/双击）",
    "高有效（外部下拉，抗 PWM 噪声）",
    "单击=微调 · 长按=连续（三段加速）",
    "双击=切对象/切模式",
], col=BLUE, ts=21, ls=16)
box(70, 610, 430, 170, "⑦ 显示（0.5\" CH1115）", [
    "88×48，软件 IIC：PB05 SDA / PB06 SCL",
    "显示：电压/百分比、组亮度与状态、",
    "吸附状态、调节对象（TGT）",
], col=BLUE, ts=21, ls=16)

# ===== 采样与存储（中下）
box(520, 800, 340, 200, "⑧ 电池电压采样", [
    "无外部电路（省 210µA）",
    "内部 BGR 1.2V 反推 VDD",
    "成对交替采样 + IIR 平滑",
    "过放保护：<3350 告警 / <3200 关断",
], col=PURPLE, ts=20, ls=16)
box(900, 800, 360, 200, "⑨ 掉电记忆与计时", [
    "Flash 第 127 页（0xFE00）",
    "两组亮度 + RTC 时间戳 + magic",
    "恢复窗口 1 小时（LSI 驱动 RTC）",
    "掉电 RTC 归零 → 自然判超时",
], col=PURPLE, ts=20, ls=16)

# ===== 连线（信号与供电方向）=====
arrow([(900, 714), (900, 796)], col=NAVY, w=4)                        # MCU → 内部 BGR 采样（发起）
arrow([(860, 796), (860, 714)], col=NAVY, w=4)                        # 采样结果 → MCU
arrow([(1080, 714), (1080, 796)], col=NAVY, w=4)                      # MCU → 掉电记忆/RTC
arrow([(1264, 480), (1326, 470)], col=GREEN, w=4)                     # MCU → 双路调光
arrow([(1264, 650), (1326, 650)], col=GREEN, w=4)                     # MCU → 磁吸接口
arrow([(1330, 880), (1180, 880), (1180, 714)], col=GREEN, w=4)        # 吸附检测 → MCU
arrow([(504, 470), (696, 470)], col=BLUE, w=4)                        # 按键 → MCU
arrow([(696, 640), (504, 690)], col=BLUE, w=4)                        # MCU → 屏
arrow([(250, 816), (250, 762), (820, 762), (820, 714)], col=ORANGE, w=4)   # 电池 VBAT 直供 MCU
arrow([(250, 1026), (250, 1056)], col=ORANGE, w=4)                    # 电池 → 3V3 轨
arrow([(430, 1125), (1902, 1125), (1902, 670), (1884, 670)], col=ORANGE, w=4)  # 3V3 轨 → 磁吸口灯端供电
arrow([(1520, 544), (1520, 576)], col=GREEN, w=4)                     # 调光输出 → 磁吸 4pin
arrow([(1690, 764), (1690, 796)], col=GREEN, w=4)                     # 磁吸口 DET → 吸附检测

d.text((70, 1215), "学习要点：① 电池直供的代价与解法（BGR 反推电压）② 8kHz/6000 级调光的由来（驱动手册区间 + 3% 下限）③ 磁吸“脱落即灭”安全逻辑", font=F(17), fill=NAVY)

img.save(os.path.join(OUT, "系统框图.png"))
print("框图 v2 saved")
