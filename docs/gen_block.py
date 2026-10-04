# -*- coding: utf-8 -*-
"""系统框图（开源学习包 docs 用）"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\docs"
os.makedirs(OUT, exist_ok=True)
FONT_R = r"C:\Windows\Fonts\msyh.ttc"; FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FONT_B if b else FONT_R, sz)

W, H = 1900, 1150
img = Image.new("RGB", (W, H), (252, 253, 255))
d = ImageDraw.Draw(img)
NAVY = (31, 56, 100); DGRAY = (60, 70, 90); LGRAY = (140, 148, 162)
BLUE = (52, 108, 176); GREEN = (46, 160, 90); ORANGE = (232, 106, 32); PURPLE = (120, 84, 176)

d.text((W/2, 40), "磁吸焊接辅助手电 · 系统框图（基于老师研发的 CW32L010 开发板）", font=F(34, True), fill=NAVY, anchor="mm")
d.text((W/2, 84), "CW32L010F8（TSSOP-20，HSI 48MHz 无外部晶振）｜双路独立 PWM 20kHz 无级调光｜磁吸 4pin 吸附检测｜STOP 低功耗", font=F(19), fill=LGRAY, anchor="mm")

def box(x, y, w, h, title, lines, col=BLUE, fill=(255, 255, 255)):
    d.rounded_rectangle([x, y, x+w, y+h], radius=12, outline=col, width=3, fill=fill)
    d.text((x+w/2, y+22), title, font=F(21, True), fill=col, anchor="mm")
    yy = y + 48
    for ln in lines:
        d.text((x+w/2, yy), ln, font=F(16), fill=DGRAY, anchor="mm")
        yy += 24

def arrow(pts, col=DGRAY, w=4):
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=col, width=w)
    import math
    x1, y1 = pts[-2]; x2, y2 = pts[-1]
    ang = math.atan2(y2-y1, x2-x1)
    px_, py_ = x2-13*math.cos(ang), y2-13*math.sin(ang)
    d.polygon([(x2, y2), (px_-7*math.sin(ang), py_+7*math.cos(ang)), (px_+7*math.sin(ang), py_-7*math.cos(ang))], fill=col)

# ==== 电源域（下排）
box(80, 850, 330, 190, "① 供电与充电", ["TYPE-C 6P 输入", "充电/升压管理（IP5306 类）", "18650 锂电池", "→ 系统 3V3（LDO，PB04 使能）"], col=ORANGE)
box(440, 850, 300, 190, "② 整机电源软开关", ["LDO CE = PB04", "开机：CE 拉高 + 唤醒", "关机：CE 拉低 + STOP 停机", "任意键唤醒（HSW 重使能）"], col=ORANGE)
box(770, 850, 340, 190, "③ 电池电压采样", ["PB00 → ADC_IN7", "ADCCLK 6MHz（PCLK/8）", "42 周期采样 + 多次均值", "分压比换算 → mV/百分比"], col=PURPLE)

# ==== 主控（中）
box(700, 400, 500, 300, "CW32L010F8  主控（TSSOP-20）", [
    "1ms 时基中断（BTIM1）调度：",
    "5ms → 按键扫描 + 吸附检测（去抖）",
    "50ms → VBAT 采样（ADC 均值）",
    "200ms → 界面数值刷新请求",
    "主循环：OLED 刷屏（耗时 ms 级，仅主循环做）",
    "输出刷新 = 电源 × 组点亮 × 亮度 × 吸附状态",
], col=NAVY, fill=(240, 245, 255))

# ==== 输出域（右）
box(1300, 360, 520, 170, "④ 双路 PWM 调光输出", ["PWM1：PB01 = ATIM_CH2 → LED 组1", "PWM2：PA03 = ATIM_CH3 → LED 组2", "20kHz（SY7200 规格下限，无可见频闪）", "计数时钟 48MHz → 2400 级分辨率（0.1% 步进）"], col=GREEN)
box(1300, 580, 520, 170, "⑤ 磁吸 4pin 接口（每组一个）", ["1) 3V3  2) GND  3) LED-  4) DET", "DET：灯端 3V3 接到检测线", "未吸附（板侧下拉=低）→ 不输出（防空载）", "吸附（高）→ 允许点亮；脱落即灭"], col=GREEN)
box(1300, 800, 520, 150, "⑥ 磁吸吸附检测", ["组1：PA01（OSC-，复用）", "组2：PA00（OSC+，复用）", "5ms 采样 + 连续 N 次一致去抖", "防磁吸瞬间抖动误判"], col=GREEN)

# ==== 人机域（左）
box(80, 400, 420, 200, "⑦ 按键（5 / 7 键）", ["外挂款 5 键：PA02 PA04 PA05 PA06 PB03", "内置款 7 键：+PA00 PA01", "功能：整机开关 / 当前组亮度 ±10%", "分组切换 / 全部亮灭（内置款可分组亮灭）", "内部上拉，按下低有效，15ms 去抖"], col=BLUE)
box(80, 640, 420, 160, "⑧ OLED 状态显示", ["0.91\" OLED（SSD1306）", "软件 IIC：PB05 SDA / PB06 SCL", "显示：电池 mV 与百分比 /", "组1、组2 亮度档位 / 吸附状态"], col=BLUE)

# ==== 连线（信号方向）====
arrow([(880, 704), (880, 800), (690, 800), (690, 846)], col=NAVY, w=4)      # MCU → ② 电源软开关（PB04 控制）
arrow([(380, 945), (444, 945)], col=ORANGE, w=4)                            # ① 充电 → ② 软开关
arrow([(920, 846), (920, 704)], col=PURPLE, w=4)                            # ③ → MCU（电压采样输入）
arrow([(1200, 480), (1296, 480)], col=GREEN, w=4)                           # MCU → ④ PWM
arrow([(1200, 640), (1296, 640)], col=GREEN, w=4)                           # MCU → ⑤ 磁吸接口
arrow([(1560, 754), (1560, 796)], col=GREEN, w=4)                           # ⑤ DET → ⑥ 检测
arrow([(1296, 875), (1150, 875), (1150, 706)], col=GREEN, w=4)              # ⑥ → MCU（吸附状态输入）
arrow([(504, 480), (696, 480)], col=BLUE, w=4)                              # ⑦ 按键 → MCU
arrow([(696, 620), (504, 700)], col=BLUE, w=4)                              # MCU → ⑧ OLED

d.text((80, 1080), "学习要点：① 电源链路（充电→LDO→软开关）② 双路独立 PWM 调光（20kHz/2400 级）③ 磁吸检测的“脱落即灭”安全逻辑", font=F(17), fill=NAVY)
d.text((80, 1110), "④ 复用引脚设计（OSC± → 检测/按键，双型号一行宏切换）⑤ 低功耗（STOP + 按键唤醒）⑥ 中断分层调度（5/50/200ms）", font=F(17), fill=NAVY)

img.save(os.path.join(OUT, "系统框图.png"))
print("框图 saved")
