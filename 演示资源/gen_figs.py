# -*- coding: utf-8 -*-
"""演示 PPT 信息图 ×3：①可复制创业逻辑闭环 ②盈利链条全图 ③创客训练效果对照"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r"C:\Users\35464\Desktop\创客训练营\演示资源\figs"
os.makedirs(OUT, exist_ok=True)
FR = r"C:\Windows\Fonts\msyh.ttc"; FB = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FB if b else FR, sz)

NAVY = (18, 41, 74); TEAL = (18, 181, 176); GOLD = (217, 164, 56)
RED = (200, 60, 55); GREEN = (36, 150, 96); GRAY = (108, 120, 138); LGRAY = (168, 176, 188)
BG = (255, 255, 255); SOFT = (243, 246, 250)
PANEL = (247, 249, 252)

def canvas(w, h, bg=BG):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)

def rrect(d, x, y, w, h, r=16, fill=None, outline=None, width=2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)

def arrow(d, pts, col=GRAY, w=5, head=16):
    import math
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=col, width=w)
    x1, y1 = pts[-2]; x2, y2 = pts[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    p = (x2 - head * math.cos(a), y2 - head * math.sin(a))
    d.polygon([(x2, y2), (p[0] - head*0.55*math.sin(a), p[1] + head*0.55*math.cos(a)),
               (p[0] + head*0.55*math.sin(a), p[1] - head*0.55*math.cos(a))], fill=col)

# ============ 图 1：可复制创业逻辑（四步闭环）
W, H = 2000, 1080
im, d = canvas(W, H)
d.text((60, 40), "可复制的创业逻辑：四步闭环（每一环都有我们的实测数据）", font=F(40, True), fill=NAVY)
d.text((60, 96), "这套流程不依赖「灵光一现」，而是每一步都有输入、有判据、有输出——换一个选题、换一个团队，照样能跑", font=F(22), fill=GRAY)

steps = [
    ("① 洞察", "用户研究", ["126 份问卷（有效）", "60 名工人实景观察", "17 个焊点返工 3 次", "台灯底座占桌 1/4"], TEAL,
     "输出：痛点清单 + 量级排序"),
    ("② 假设", "价值与增长", ["5 条可验证假设", "ICE 评分排序", "北极星：周活跃焊接时长", "行为口径优先"], (74, 118, 200),
     "输出：待验证假设台账"),
    ("③ 验证", "最小成本实验", ["1 元可退意向金 → 37.3%", "A/B：LED 82% vs OLED 86%", "渠道实测 CAC ¥8.6 / ¥11.5 / ¥31.8", "小批试产 BOM ¥52.3"], GOLD,
     "输出：数据判据是非结论"),
    ("④ 迭代", "用数据改决策", ["定价收敛 59–69 元", "停线上（LTV/CAC 0.83）", "转 B 端：22 台首单", "保本线 400 → 2,886 台"], RED,
     "输出：可执行的下一步"),
]
x0, y0, cw, ch, gap = 60, 190, 440, 560, 40
for i, (t, sub, items, col, out) in enumerate(steps):
    x = x0 + i * (cw + gap)
    rrect(d, x, y0, cw, ch, 18, fill=PANEL, outline=col, width=3)
    d.rectangle([x, y0, x + cw, y0 + 8], fill=col)
    d.text((x + 30, y0 + 40), t, font=F(40, True), fill=col)
    d.text((x + 30, y0 + 96), sub, font=F(24), fill=GRAY)
    yy = y0 + 150
    for it in items:
        d.text((x + 30, yy), "·", font=F(24, True), fill=col)
        d.text((x + 52, yy), it, font=F(23), fill=(45, 55, 72))
        yy += 52
    rrect(d, x + 24, y0 + ch - 110, cw - 48, 78, 12, fill=(255, 255, 255), outline=LGRAY, width=2)
    d.text((x + 40, y0 + ch - 96), out, font=F(21, True), fill=col)
    if i < 3:
        arrow(d, [(x + cw + 8, y0 + ch/2), (x + cw + gap - 8, y0 + ch/2)], col=GRAY, w=6)

# 底部闭环回路
arrow(d, [(x0 + 4*(cw+gap) - gap - cw + cw/2, y0 + ch + 20), (x0 + 4*(cw+gap) - gap - cw + cw/2, y0 + ch + 70)], col=GRAY, w=5)
d.line([(x0 + cw/2, y0 + ch + 70), (x0 + 4*(cw+gap) - gap - cw + cw/2, y0 + ch + 70)], fill=GRAY, width=5)
arrow(d, [(x0 + cw/2, y0 + ch + 70), (x0 + cw/2, y0 + ch + 20)], col=GRAY, w=5)
d.text((W/2, y0 + ch + 110), "迭代后回到洞察：新问题 → 新假设 → 下一轮（我们把「纠错」当流程的一部分，而不是失败）",
       font=F(24, True), fill=NAVY, anchor="mm")
im.save(os.path.join(OUT, "fig1_创业逻辑闭环.png"))
print("fig1 ok")

# ============ 图 2：盈利链条全图
W, H = 2000, 1120
im, d = canvas(W, H)
d.text((60, 40), "盈利链条：从 ¥43 的 BOM 到可复制的三档生意", font=F(40, True), fill=NAVY)
d.text((60, 96), "每一环都写实测数字（含我们算错又改对的那一环）——链条能不能通，看的是最窄处", font=F(22), fill=GRAY)

chain = [
    ("成本", "BOM", ["小批实测 ¥52.3", "目标 ¥43.0 / 最优 ¥39.6", "量产锁定千片报价"], (74, 118, 200)),
    ("定价", "价格带", ["标准版 65 元（59–69）", "青春版走 3D 打印路径", "态度 71.3% / 行为 37.3%"], TEAL),
    ("毛利", "毛利率", ["中期预估 40%", "小批实测 11.2%", "量产后 33.8%"], RED),
    ("获客", "渠道 CAC", ["地推 ¥8.6（34.9%）", "社团 ¥11.5（27.1%）", "线上 ¥31.8（5.2%）✗"], GOLD),
    ("规模", "保本与首单", ["保本 2,886 台（小批）", "降级目标 1,232 台", "B 端 22 台首单"], GREEN),
]
x0, y0, cw, ch, gap = 60, 190, 352, 470, 32
for i, (t, sub, items, col) in enumerate(chain):
    x = x0 + i * (cw + gap)
    rrect(d, x, y0, cw, ch, 18, fill=PANEL, outline=col, width=3)
    d.rectangle([x, y0, x + cw, y0 + 8], fill=col)
    d.text((x + 26, y0 + 36), t, font=F(36, True), fill=col)
    d.text((x + 26, y0 + 88), sub, font=F(22), fill=GRAY)
    yy = y0 + 140
    for it in items:
        d.text((x + 24, yy), it, font=F(21), fill=(45, 55, 72))
        yy += 62
    if i < 4:
        arrow(d, [(x + cw + 4, y0 + ch/2), (x + cw + gap - 4, y0 + ch/2)], col=col, w=6)

rrect(d, 60, y0 + ch + 40, W - 120, 250, 18, fill=SOFT, outline=NAVY, width=3)
d.text((90, y0 + ch + 62), "怎么赚钱：三档生意共用同一条链，但单位经济完全不同", font=F(30, True), fill=NAVY)
rows = [
    ("C 端零售", "65 元/台", "渠道 ¥8.6–¥11.5", "走量薄利，靠地推与社团复购（NPS 42）", TEAL),
    ("DIY 套件", "≈ 49 元/套", "近零获客", "3D 打印外壳，学生自装，毛利结构更优（兜底路径）", GOLD),
    ("B 端实训采买", "批量议价", "0 获客成本", "老师牵线 22 台首单；B 端占比目标 45%", GREEN),
]
yy = y0 + ch + 118
for name, price, cac, note, col in rows:
    d.text((100, yy), name, font=F(24, True), fill=col)
    d.text((400, yy), price, font=F(23, True), fill=(45, 55, 72))
    d.text((700, yy), cac, font=F(23), fill=GRAY)
    d.text((1050, yy), note, font=F(21), fill=(45, 55, 72))
    yy += 54
im.save(os.path.join(OUT, "fig2_盈利链条.png"))
print("fig2 ok")

# ============ 图 3：创客训练效果对照（中期 → 结题）
W, H = 2000, 1060
im, d = canvas(W, H)
d.text((60, 40), "创客训练的效果：中期 → 结题，四条曲线都在变好（也有一条被我们按住了）", font=F(38, True), fill=NAVY)
d.text((60, 96), "数据口径：结题报告 V2.0 表 1-1（三类对比：中期 vs 结题 / 计划 vs 实际 / 均值 vs 最优）", font=F(21), fill=GRAY)

# 左：三项指标条形对比
d.text((60, 165), "指标变化（中期 → 结题）", font=F(28, True), fill=NAVY)
metrics = [("验证数据量", 157, 312, "条", 320), ("任务完成率", 50, 78, "%", 100), ("意向金支付率", 32.3, 37.3, "%", 100)]
bx, by = 90, 230
for name, a, b, unit, mx in metrics:
    d.text((bx, by), name, font=F(24), fill=(45, 55, 72))
    # 中期条
    rrect(d, bx + 260, by + 4, int(520 * a / mx), 30, 6, fill=LGRAY)
    d.text((bx + 250, by), f"中期 {a}{unit}", font=F(20), fill=GRAY, anchor="rm")
    # 结题条
    rrect(d, bx + 260, by + 44, int(520 * b / mx), 30, 6, fill=TEAL)
    d.text((bx + 250, by + 40), f"结题 {b}{unit}", font=F(20, True), fill=TEAL, anchor="rm")
    by += 130

# 右：能力等级 + 纠错统计
rrect(d, 1060, 200, 880, 300, 18, fill=PANEL, outline=NAVY, width=3)
d.text((1090, 222), "个人能力等级（结题评定）", font=F(28, True), fill=NAVY)
d.text((1090, 280), "邵子中", font=F(24), fill=(45, 55, 72)); d.text((1320, 278), "L4", font=F(30, True), fill=TEAL)
d.text((1090, 330), "李昊桐", font=F(24), fill=(45, 55, 72)); d.text((1320, 328), "L3", font=F(30, True), fill=GOLD)
d.text((1090, 380), "姜亚楷", font=F(24), fill=(45, 55, 72)); d.text((1320, 378), "L4", font=F(30, True), fill=TEAL)
d.text((1090, 430), "「不因完成率 96% 就调高等级」——等级按证据给，不按心情给", font=F(19), fill=GRAY)

rrect(d, 60, 620, 1080, 380, 18, fill=(255, 252, 246), outline=RED, width=3)
d.text((90, 644), "最有力的一份成果：我们把自己的错改掉了", font=F(30, True), fill=RED)
fixes = [
    ("毛利率", "预估 40%", "小批实测 11.2%", "重建单位经济与保本模型"),
    ("保本销量", "自检 400 台", "修正 2,886 台", "补分项依据，重算 BOM 与定价"),
    ("购买意愿", "态度 71.3%", "行为 37.3%", "北极星改用行为口径"),
    ("线上渠道", "「传播性强」", "LTV/CAC 0.83", "停投放，转地推与 B 端"),
]
yy = 706
for name, a, b, act in fixes:
    d.text((95, yy), name, font=F(23, True), fill=(45, 55, 72))
    d.text((300, yy), a, font=F(22), fill=GRAY)
    arrow(d, [(520, yy + 14), (600, yy + 14)], col=RED, w=4, head=11)
    d.text((620, yy), b, font=F(23, True), fill=RED)
    d.text((900, yy), act, font=F(20), fill=(45, 55, 72))
    yy += 68

rrect(d, 1180, 620, 760, 380, 18, fill=PANEL, outline=TEAL, width=3)
d.text((1210, 644), "训练留下的痕迹", font=F(30, True), fill=TEAL)
traces = [
    "本轮修订 9 处结论，其中 4 处由评审触发（修正率 44%）",
    "从「算清 BOM ≠ 算清经济账」的认知跃迁（偏差率 72% → 已修正）",
    "硬件攻坚：屏驱动 4 轮点亮、ADC 三段排查、PWM 5 次频率迭代",
    "低功耗四个连环坑逐个定位（唤醒沿/时序/回弹/供电）",
    "把全部过程与踩坑写成开源文档——下一个人不用重走",
]
yy = 706
for t in traces:
    d.text((1215, yy), "·", font=F(24, True), fill=TEAL)
    d.text((1240, yy), t, font=F(21), fill=(45, 55, 72))
    yy += 62
im.save(os.path.join(OUT, "fig3_训练效果.png"))
print("fig3 ok")
