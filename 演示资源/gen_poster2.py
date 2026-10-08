# -*- coding: utf-8 -*-
"""项目海报（A4 竖版 @300dpi，重排版）：保证内容底 ≤ 3258，底部深色条留白 40px"""
import os, re
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营\演示资源"
FR = r"C:\Windows\Fonts\msyh.ttc"; FB = r"C:\Windows\Fonts\msyhbd.ttc"
F = lambda s: ImageFont.truetype(FR, s)
FBf = lambda s: ImageFont.truetype(FB, s)

W, H = 2480, 3508
NAVY = "#12294A"; TEAL = "#12B5B0"; GOLD = "#D9A438"; RED = "#C83C37"
GREEN = "#249660"; INK = "#22303F"; GRAY = "#6C788A"
SOFT = "#F4F7FB"; LINE = "#DBE3EE"; WHITE = "#FFFFFF"; BLUE = "#4A76C8"

im = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(im)
_TOK = re.compile(r"[A-Za-z0-9%¥.+/\-—→≥≤×·]+|.", re.S)

def wrap(text, font, maxw):
    out = []
    for seg in text.split("\n"):
        if not seg:
            out.append(""); continue
        lines, cur = [], ""
        for ch in _TOK.findall(seg):
            t = cur + ch
            if d.textlength(t, font=font) > maxw and cur:
                lines.append(cur); cur = ch
            else:
                cur = t
        if cur: lines.append(cur)
        out.extend(lines)
    return out

def para(x, y, text, font, maxw, fill=INK, lh=1.45, center=False):
    for i, ln in enumerate(wrap(text, font, maxw)):
        xx = x + (maxw - d.textlength(ln, font=font)) / 2 if center else x
        d.text((xx, y + i * font.size * lh), ln, font=font, fill=fill)
    return y + len(wrap(text, font, maxw)) * font.size * lh

def card(box, fill=WHITE, outline=LINE, r=26, w=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)

def sect(x, y, txt, color=TEAL, size=50):
    d.rounded_rectangle([x, y + 4, x + 14, y + size + 4], 6, fill=color)
    d.text((x + 32, y - 6), txt, font=FBf(size), fill=NAVY)

M = 130
# ══════ 顶带（0..470）
d.rectangle([0, 0, W, 470], fill=NAVY)
d.rectangle([0, 0, W, 14], fill=TEAL)
d.text((M, 54), "创客训练营 · 项目海报　|　面向创客竞赛评审", font=F(38), fill=TEAL)
d.text((M, 112), "不是一台灯，", font=FBf(104), fill=WHITE)
d.text((M, 232), "是一套可复制的创业逻辑", font=FBf(104), fill=WHITE)
d.text((M, 366), "磁吸焊接辅助手电 · 从用户洞察到盈利链条的完整闭环｜方法可复制 · 数据可核验 · 成果可教学", font=F(40), fill="#C4D2E6")
d.rectangle([W - 290, 116, W - 130, 124], fill=GOLD)

# ══════ 照片位（占位）+ 简介（540..1085）
y1 = 540
card([M, y1, M + 1080, y1 + 545], fill="#EFF3F9", outline="#C9D5E6")
for i in range(M + 24, M + 1056, 40):
    d.line([(i, y1 + 521), (min(i + 70, M + 1056), y1 + 24)], fill="#DFE7F2", width=4)
d.text((M + 296, y1 + 236), "【替换：产品实物照片】", font=FBf(50), fill="#93A0B4")
d.text((M + 236, y1 + 310), "（2 台样机正视图 / 磁吸吸附演示 / 桌面场景）", font=F(32), fill="#A8B4C4")

card([M + 1130, y1, W - M, y1 + 545], fill=SOFT)
d.text((M + 1170, y1 + 26), "我们做了什么", font=FBf(50), fill=NAVY)
para(M + 1170, y1 + 104,
     "做出一台「吸上就亮、指哪照哪」的焊接照明工具（BOM ≈ ¥45 级，已小批量）。真正交付的是三条可复制资产：",
     F(35), 990, lh=1.42)
yy = y1 + 226
for tag, txt, col in [
    ("洞察方法", "126 份问卷 + 60 人实景观察 + 动作计数", TEAL),
    ("验证闭环", "1 元意向金、A/B 对照、渠道 CAC 实测", GOLD),
    ("盈利链条", "BOM → 定价 → 毛利 → 获客 → 保本 → 三档路径", GREEN)]:
    d.rounded_rectangle([M + 1170, yy, M + 1186, yy + 38], 5, fill=col)
    d.text((M + 1202, yy - 6), tag, font=FBf(36), fill=col)
    d.text((M + 1202, yy + 42), txt, font=F(32), fill=INK)
    yy += 112
d.text((M + 1170, y1 + 486), "数据可在结题报告定位到原始记录（E-01~E-15）", font=F(30), fill=GRAY)

# ══════ KPI（1180..1706）
y2 = 1180
sect(M, y2, "关键数据（可核验）")
yy = y2 + 90
kpis = [("312", "条验证数据", "中期 157 → 结题 312", TEAL),
        ("37.3%", "意向金支付率", "行为口径（22/59 真付费）", NAVY),
        ("¥8.6", "地推获客成本", "线上 ¥31.8 已停投", GOLD),
        ("22", "台 B 端首单", "老师牵线，零获客成本", GREEN),
        ("2,886", "台保本线（小批）", "降级目标 1,232 台", RED),
        ("L4", "团队能力等级", "按证据给，不按心情给", NAVY)]
cw, ch, gap = 730, 195, 24
for i, (num, unit, note, col) in enumerate(kpis):
    r, c = divmod(i, 3)
    x = M + c * (cw + gap)
    y = yy + r * (ch + gap)
    card([x, y, x + cw, y + ch], fill=SOFT, outline=col, w=4)
    d.text((x + 30, y + 20), num, font=FBf(74), fill=col)
    d.text((x + 240, y + 44), unit, font=FBf(36), fill=INK)
    d.text((x + 30, y + 122), note, font=F(31), fill=GRAY)

# ══════ 四步闭环（1752..2152）
y3 = yy + 2 * (ch + gap) + 46
sect(M, y3, "可复制的创业逻辑：四步闭环", TEAL)
yy = y3 + 96
steps = [
    ("① 洞察", "126 份问卷（分层抽样）\n60 名工人实景观察\n把「不好用」变成可测数字", TEAL),
    ("② 假设", "5 条可验证假设\nICE 评分排序\n北极星＝周活跃焊接时长", BLUE),
    ("③ 验证", "1 元意向金 → 37.3%\nA/B：LED 82% vs OLED 86%\nCAC ¥8.6 / ¥11.5 / ¥31.8", GOLD),
    ("④ 迭代", "定价收敛 59–69 元\n停线上（LTV/CAC 0.83）\nB 端 22 台首单", RED),
]
bw, bh, bg = 520, 400, 46
for i, (t, body, col) in enumerate(steps):
    x = M + i * (bw + bg)
    card([x, yy, x + bw, yy + bh], fill=SOFT, outline=col, w=4)
    d.rectangle([x + 3, yy + 3, x + bw - 3, yy + 15], fill=col)
    d.text((x + 30, yy + 32), t, font=FBf(50), fill=col)
    para(x + 30, yy + 118, body, F(34), bw - 60, lh=1.55)
    if i < 3:
        d.polygon([(x + bw + 8, yy + bh / 2 - 15), (x + bw + bg - 8, yy + bh / 2),
                   (x + bw + 8, yy + bh / 2 + 15)], fill=GRAY)

# ══════ 盈利链条（2198..2608）
y4 = yy + bh + 46
sect(M, y4, "盈利链条：从 BOM 到可复制的三档生意", GOLD)
yy = y4 + 96
chain = [("BOM ¥52.3", "小批实测（目标 ¥43.0）", BLUE),
         ("定价 59–69 元", "标准版 65 元", TEAL),
         ("毛利 11.2% → 33.8%", "小批 → 量产（自纠错项）", RED),
         ("获客 ¥8.6 起", "地推最优 / 线上已停", GOLD),
         ("保本 2,886 台", "降级目标 1,232 台", GREEN)]
bw2, bh2, bg2 = 420, 180, 32
for i, (t, sub, col) in enumerate(chain):
    x = M + i * (bw2 + bg2)
    card([x, yy, x + bw2, yy + bh2], fill=WHITE, outline=col, w=4)
    para(x + 24, yy + 36, t, FBf(38), bw2 - 48, fill=col, lh=1.2)
    para(x + 24, yy + 120, sub, F(28), bw2 - 48, fill=GRAY, lh=1.25)
    if i < 4:
        d.polygon([(x + bw2 + 4, yy + bh2 / 2 - 11), (x + bw2 + bg2 - 4, yy + bh2 / 2),
                   (x + bw2 + 4, yy + bh2 / 2 + 11)], fill=GRAY)
yy += bh2 + 26
card([M, yy, W - M, yy + 122], fill=SOFT)
d.text((M + 30, yy + 16), "三档路径：", font=FBf(36), fill=NAVY)
para(M + 246, yy + 14, "C 端零售（65 元/台，CAC ¥8.6–11.5）　·　DIY 套件（≈49 元/套，近零获客）　·　B 端实训采买（零获客，首单 22 台，目标占比 45%）",
     F(31), 2070 - 116, lh=1.35)
d.text((M + 246, yy + 62), "底线：B 端放量不及预期时退回 3D 打印路径（1,232 台保本）——用降级方案守住生存线", font=F(29), fill=GRAY)

# ══════ 训练效果 + 开源学习包（2756..3131）
y5 = yy + 122 + 26
sect(M, y5, "创客训练的效果", RED)
yy2 = y5 + 92
card([M, yy2, M + 1080, yy2 + 375], fill=SOFT)
para(M + 30, yy2 + 22,
     "从「把事情做出来」到「用数据决定该不该做」：\n"
     "· 中期 → 结题：验证数据 157→312、完成率 50%→78%\n"
     "· 能力等级按证据评定：L4 / L3 / L4\n"
     "· 最有力的一份成果：我们把自己的错改掉了——\n"
     "　毛利预估 40% → 实测 11.2%；保本 400 → 2,886 台\n"
     "· 本轮修订 9 处结论，其中 4 处由评审触发（修正率 44%）",
     F(32), 1010, lh=1.45)
sect(M + 1130, y5, "开源学习包（MIT）", GREEN)
card([M + 1130, yy2, W - M, yy2 + 375], fill=SOFT)
para(M + 1160, yy2 + 22,
     "把方法与踩坑写下来，让下一个人不必从零开始：\n"
     "· 9 个学习模块（16–24 学时）· 12 个固件模块（BSP 分层）\n"
     "· 14 项量化验收判据 · 8 篇文档（含完整踩坑实录）\n"
     "· 硬件：立创EDA 工程 / BOM / 3D 打印件（含按键帽）\n"
     "· 仓库：github.com/Davidshao-114514/chuangkexunlianying",
     F(32), 1020, lh=1.45)

# ══════ 底部条（3298..3508）
yb = H - 210
d.rectangle([0, yb, W, H], fill=NAVY)
d.rectangle([0, yb, W, yb + 10], fill=GOLD)
d.text((M, yb + 46), "1 班 C 组 · 仿真跑不队：邵子中 / 李昊桐 / 姜亚楷", font=FBf(44), fill=WHITE)
d.text((M, yb + 116), "致谢：指导老师提供 CW32L010 开发板与工程框架｜数据来源：结题报告 V2.0、资源优化方案书（可核验）", font=F(31), fill="#AEBED4")

im.save(os.path.join(OUT, "海报_可复制的创业逻辑_A4.png"))
im.save(os.path.join(OUT, "海报_可复制的创业逻辑_A4.pdf"), "PDF", resolution=300.0)
print("海报 saved:", W, "x", H)
print("内容底约:", yy2 + 375, "| 底条起点:", yb, "| 留白:", yb - (yy2 + 375))
