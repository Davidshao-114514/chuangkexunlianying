# -*- coding: utf-8 -*-
"""图 A：开源获客正循环（开源→客流→反哺→收入→再投入）；图 B：盈利链条（开源免费层 + 付费三档）"""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\演示资源\figs"
FR = r"C:\Windows\Fonts\msyh.ttc"; FB = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FB if b else FR, sz)

NAVY = (18, 41, 74); TEAL = (18, 181, 176); GOLD = (217, 164, 56)
RED = (200, 60, 55); GREEN = (36, 150, 96); GRAY = (108, 120, 138)
BLUE = (74, 118, 200); WHITE = (255, 255, 255); INK = (45, 55, 72)
SOFT = (244, 247, 251); LINE = (219, 227, 238)

def canvas(w, h, bg=WHITE):
    im = Image.new("RGB", (w, h), bg); return im, ImageDraw.Draw(im)

def rrect(d, x, y, w, h, r=16, fill=None, outline=None, width=2):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)

def arrow(d, pts, col=GRAY, w=6, head=18):
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=col, width=w)
    x1, y1 = pts[-2]; x2, y2 = pts[-1]
    a = math.atan2(y2 - y1, x2 - x1); p = (x2 - head * math.cos(a), y2 - head * math.sin(a))
    d.polygon([(x2, y2), (p[0] - head*0.55*math.sin(a), p[1] + head*0.55*math.cos(a)),
               (p[0] + head*0.55*math.sin(a), p[1] - head*0.55*math.cos(a))], fill=col)

# ══════════════ 图 A：开源获客正循环
W, H = 2000, 1130
im, d = canvas(W, H)
d.text((56, 38), "开源项目的获客逻辑：一个越转越省的正循环", font=F(42, True), fill=NAVY)
d.text((56, 96), "别人看到的是「开源＝把东西白送」；我们看到的是「开源＝一台低成本的获客引擎」", font=F(23), fill=GRAY)

# 中心
cx, cy = 1000, 640
rrect(d, cx - 300, cy - 78, 600, 156, 22, fill=(232, 246, 245), outline=TEAL, width=4)
d.text((cx, cy - 44), "开源学习包", font=F(44, True), fill=TEAL, anchor="mm")
d.text((cx, cy + 8), "设计 / 固件 / 文档 / 踩坑全部公开（MIT）", font=F(24), fill=INK, anchor="mm")
d.text((cx, cy + 46), "＝ 一份人人都能验证的「信任物料」", font=F(24, True), fill=NAVY, anchor="mm")

# 四个环上节点
nodes = [
    ("① 降低信任成本", "客户/学校/机构敢买、敢推荐：\n可复现、可审查、可评估", TEAL, 470, 175),
    ("② 降低分发成本", "不再依赖付费投放（线上 CAC ¥31.8）：\n用户主动找上门", GOLD, 1330, 175),
    ("③ 获得精准客流", "吸引的都是真动手的人：\n学生 / 工程师 / 教师 / 实训机构", BLUE, 1470, 810),
    ("④ 客流反哺技术", "反馈定迭代优先级、共建补研发、\n教学场景带来批量需求", GREEN, 330, 810),
]
for title, body, col, x, y in nodes:
    rrect(d, x - 270, y - 92, 540, 184, 18, fill=SOFT, outline=col, width=4)
    d.rectangle([x - 267, y - 89, x + 267, y - 74], fill=col)
    d.text((x - 246, y - 58), title, font=F(34, True), fill=col)
    yy = y - 6
    for ln in body.split("\n"):
        d.text((x - 246, yy), ln, font=F(24), fill=INK); yy += 38

# 循环箭头
arrow(d, [(cx - 320, cy - 60), (cx - 470, cy - 60), (cx - 470, cy - 178)], col=TEAL, w=7)
arrow(d, [(cx + 320, cy - 60), (cx + 470, cy - 60), (cx + 470, cy - 178)], col=GOLD, w=7)
arrow(d, [(cx + 470, cy + 90), (cx + 470, cy + 210), (cx + 330, cy + 210)], col=BLUE, w=7)
arrow(d, [(cx - 470, cy + 90), (cx - 470, cy + 210), (cx - 330, cy + 210)], col=GREEN, w=7)
# 顶部与底部连接
arrow(d, [(cx + 700, cy - 78), (cx + 900, cy - 300), (cx + 900, cy - 240)], col=GOLD, w=0)
d.text((cx, cy + 300), "开源不是终点，是起点：客流进来了，才有后面的一切（收入、迭代、口碑）", font=F(27, True), fill=NAVY, anchor="mm")
d.text((56, H - 62), "实测对照：开源与教师/社团渠道 CAC ¥8.6–11.5；纯线上投放 CAC ¥31.8 且 LTV/CAC 0.83（已停投）",
       font=F(23), fill=GRAY)
im.save(os.path.join(OUT, "fig4_开源获客逻辑.png"))
print("fig4 ok")

# ══════════════ 图 B：盈利链条（开源免费层 + 付费三档）
W, H = 2000, 1060
im, d = canvas(W, H)
d.text((56, 38), "盈利链条：开源免费的部分获客，付费的部分赚钱", font=F(42, True), fill=NAVY)
d.text((56, 96), "开源与盈利不矛盾：开的是「知识与设计」，卖的是「成品、套件、确定性与服务」", font=F(23), fill=GRAY)

# 免费层
rrect(d, 56, 160, 1888, 150, 18, fill=(232, 246, 245), outline=TEAL, width=4)
d.text((90, 186), "免费层（获客）", font=F(34, True), fill=TEAL)
d.text((416, 190), "开源学习包：原理图 / PCB / BOM / 3D 打印件 / 固件源码 / 9 模块课程 / 踩坑实录（MIT）", font=F(26), fill=INK)
d.text((90, 244), "得到什么", font=F(26, True), fill=NAVY)
d.text((416, 244), "信任 + 口碑 + 精准客流 + 共建者 —— 获客成本从 ¥31.8（投放）降到 ¥0–8.6", font=F(26), fill=INK)
arrow(d, [(1000, 318), (1000, 368)], col=TEAL, w=7)

# 付费层三档
d.text((90, 388), "付费层（三档收入，共用同一条链）", font=F(32, True), fill=NAVY)
tiers = [
    ("C 端成品机", "65 元/台（59–69）", ["地推 CAC ¥8.6", "社团 CAC ¥11.5", "走量薄利，靠口碑复购"], TEAL),
    ("DIY 套件", "≈ 49 元/套", ["3D 打印 + 自装", "近零获客成本", "学生入门首选，兜底路径"], GOLD),
    ("B 端实训采买", "批量议价（20+ 台）", ["老师牵线，0 获客成本", "首单 22 台已交付", "目标占比 45%（教学包）"], GREEN),
]
bx, by, bw, bh, bg = 56, 448, 600, 300, 44
for i, (t, price, items, col) in enumerate(tiers):
    x = bx + i * (bw + bg)
    rrect(d, x, by, bw, bh, 18, fill=SOFT, outline=col, width=4)
    d.rectangle([x + 3, by + 3, x + bw - 3, by + 16], fill=col)
    d.text((x + 28, by + 36), t, font=F(36, True), fill=col)
    d.text((x + 28, by + 92), price, font=F(29, True), fill=INK)
    yy = by + 146
    for it in items:
        d.text((x + 28, yy), "· " + it, font=F(24), fill=INK); yy += 44

# 单位经济条
rrect(d, 56, by + bh + 34, 1888, 138, 18, fill=(255, 250, 242), outline=GOLD, width=4)
d.text((90, by + bh + 52), "单位经济（实测，含自我纠错）", font=F(29, True), fill=GOLD)
d.text((90, by + bh + 96), "BOM ¥52.3（小批）→ 目标 ¥43.0　　·　　定价 65 元（59–69）", font=F(25), fill=INK)
d.text((950, by + bh + 96), "毛利率 11.2% → 33.8%（量产）　·　保本 2,886 台（降级 1,232 台）", font=F(25), fill=INK)
im.save(os.path.join(OUT, "fig5_盈利链条.png"))
print("fig5 ok")
