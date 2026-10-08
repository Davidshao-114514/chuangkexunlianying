# -*- coding: utf-8 -*-
"""图 A（重排）：开源获客正循环——留足标题间距，箭头沿节点边缘走不穿框"""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\演示资源\figs"
FR = r"C:\Windows\Fonts\msyh.ttc"; FB = r"C:\Windows\Fonts\msyhbd.ttc"
def F(sz, b=False): return ImageFont.truetype(FB if b else FR, sz)
NAVY=(18,41,74); TEAL=(18,181,176); GOLD=(217,164,56); RED=(200,60,55)
GREEN=(36,150,96); GRAY=(108,120,138); BLUE=(74,118,200); WHITE=(255,255,255)
INK=(45,55,72); SOFT=(244,247,251)

W, H = 2000, 1250
im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)

def rrect(x, y, w, h, r=16, fill=None, outline=None, width=2):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)

def arrow(pts, col=GRAY, w=7, head=20):
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=col, width=w)
    x1,y1 = pts[-2]; x2,y2 = pts[-1]
    a = math.atan2(y2-y1, x2-x1); p = (x2-head*math.cos(a), y2-head*math.sin(a))
    d.polygon([(x2,y2), (p[0]-head*0.55*math.sin(a), p[1]+head*0.55*math.cos(a)),
               (p[0]+head*0.55*math.sin(a), p[1]-head*0.55*math.cos(a))], fill=col)

d.text((56, 40), "开源项目的获客逻辑：一个越转越省的正循环", font=F(44, True), fill=NAVY)
d.text((56, 104), "别人看到的是「开源＝把东西白送」；我们看到的是「开源＝一台低成本的获客引擎」", font=F(25), fill=GRAY)

# 中心
CX, CY = 1000, 720
rrect(CX-360, CY-92, 720, 184, 22, fill=(232,246,245), outline=TEAL, width=5)
d.text((CX, CY-52), "开源学习包", font=F(46, True), fill=TEAL, anchor="mm")
d.text((CX, CY+0), "设计 / 固件 / 文档 / 踩坑全部公开（MIT）", font=F(25), fill=INK, anchor="mm")
d.text((CX, CY+46), "＝ 一份人人都能验证的「信任物料」", font=F(26, True), fill=NAVY, anchor="mm")

# 四节点（中心坐标）
N1 = (470, 300); N2 = (1330, 300); N3 = (1470, 900); N4 = (330, 900)
nodes = [
    (N1, "① 降低信任成本", "客户 / 学校 / 机构敢买、敢推荐：\n可复现、可审查、可评估", TEAL),
    (N2, "② 降低分发成本", "不再依赖付费投放（线上 CAC ¥31.8）：\n用户主动找上门", GOLD),
    (N3, "③ 获得精准客流", "吸引的都是真动手的人：\n学生 / 工程师 / 教师 / 实训机构", BLUE),
    (N4, "④ 客流反哺技术", "用户反馈定迭代优先级、共建补研发、\n教学场景带来批量需求", GREEN),
]
BW, BH = 560, 190
for (x, y), title, body, col in nodes:
    rrect(x-BW/2, y-BH/2, BW, BH, 18, fill=SOFT, outline=col, width=5)
    d.rectangle([x-BW/2+3, y-BH/2+3, x+BW/2-3, y-BH/2+17], fill=col)
    d.text((x-BW/2+26, y-BH/2+34), title, font=F(35, True), fill=col)
    yy = y-BH/2+92
    for ln in body.split("\n"):
        d.text((x-BW/2+26, yy), ln, font=F(25), fill=INK); yy += 40

# 循环箭头（沿节点边缘，不穿框）
arrow([(CX-150, CY-92), (CX-150, 440)], col=TEAL, w=7)          # 中心 → ① 底
arrow([(N1[0]+BW/2+10, N1[1]), (N2[0]-BW/2-10, N2[1])], col=GOLD, w=7)   # ① → ②
arrow([(N2[0]+90, N2[1]+BH/2+10), (N2[0]+90, N3[1]-BH/2-10)], col=BLUE, w=7)  # ② → ③
arrow([(N3[0]-BW/2-10, N3[1]), (N4[0]+BW/2+10, N4[1])], col=GREEN, w=7)  # ③ → ④
arrow([(N4[0]+90, N4[1]-BH/2-10), (CX-150, CY+92)], col=GREEN, w=7)      # ④ → 中心

d.text((CX, 1120), "开源不是终点，是起点：客流进来了，才有后面的一切（收入、迭代、口碑）", font=F(29, True), fill=NAVY, anchor="mm")
d.text((56, 1180), "实测对照：开源与教师 / 社团渠道 CAC ¥8.6–11.5；纯线上投放 CAC ¥31.8 且 LTV/CAC 0.83（已停投）", font=F(24), fill=GRAY)
im.save(os.path.join(OUT, "fig4_开源获客逻辑.png"))
print("fig4 v2 ok")
