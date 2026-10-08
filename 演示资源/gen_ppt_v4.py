# -*- coding: utf-8 -*-
"""汇报 PPT V4.0：开源项目的获客逻辑与盈利链条（面向创客竞赛老师）
叙事：团队思维转变（技术思维 → 客流思维）→ 开源是获客引擎 → 客流反哺技术 → 盈利链条 → 盈利信心
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor as C
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE = r"C:\Users\35464\Desktop\创客训练营"
OUT = os.path.join(BASE, "演示资源")
FIGS = os.path.join(OUT, "figs")
FNAME = os.path.join(OUT, "磁吸焊接辅助手电_获客逻辑与盈利链条_汇报PPT.pptx")

NAVY = C(18, 41, 74); TEAL = C(18, 181, 176); GOLD = C(217, 164, 56)
RED = C(200, 60, 55); GREEN = C(36, 150, 96); GRAY = C(108, 120, 138)
LGRAY = C(168, 176, 188); WHITE = C(255, 255, 255); INK = C(45, 55, 72)
SOFT = C(243, 246, 250); PANEL = C(247, 249, 252); BLUE = C(74, 118, 200)

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def slide(): return prs.slides.add_slide(BLANK)

def tx(s, x, y, w, h, text, size=13, bold=False, color=INK, align=PP_ALIGN.LEFT, line=1.25):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, ln in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = line
        r = p.add_run(); r.text = ln
        f = r.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = '微软雅黑'
    return tb

def rect(s, x, y, w, h, fill=None, line=None, lw=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    try: sp.adjustments[0] = 0.06
    except Exception: pass
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb = line; sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    return sp

PAGE = {"n": 1}
def head(s, section, title, sub=None):
    PAGE["n"] += 1
    rect(s, 0, 0, 0.085, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0.62, 0.42, 0.055, 0.42, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
    tx(s, 0.82, 0.42, 9.6, 0.42, title, size=25, bold=True, color=NAVY)
    tx(s, 0.84, 0.93, 11.5, 0.32, sub or "", size=11.5, color=GRAY)
    rect(s, 0.62, 1.34, 12.1, 0.02, fill=C(222, 228, 238), shape=MSO_SHAPE.RECTANGLE)
    tx(s, 0.62, 0.06, 6.0, 0.3, section, size=10.5, color=LGRAY)
    tx(s, 12.3, 6.98, 0.6, 0.3, f"{PAGE['n']:02d}", size=10.5, color=LGRAY, align=PP_ALIGN.RIGHT)

def kpi(s, x, y, w, h, num, unit, label, col=TEAL):
    rect(s, x, y, w, h, fill=PANEL, line=col, lw=1.4)
    tx(s, x + 0.1, y + 0.24, w - 0.2, 0.7, num, size=32, bold=True, color=col, align=PP_ALIGN.CENTER)
    tx(s, x + 0.08, y + 0.92, w - 0.16, 0.3, unit, size=11, color=GRAY, align=PP_ALIGN.CENTER)
    tx(s, x + 0.08, y + 1.26, w - 0.16, 0.66, label, size=10.5, color=INK, align=PP_ALIGN.CENTER, line=1.2)

def card(s, x, y, w, h, title, body, col=NAVY, tsize=16, bsize=11.5, tag=None):
    rect(s, x, y, w, h, fill=PANEL, line=col, lw=1.5)
    rect(s, x, y, w, 0.055, fill=col, shape=MSO_SHAPE.RECTANGLE)
    tx(s, x + 0.2, y + 0.18, w - 0.4, 0.4, title, size=tsize, bold=True, color=col)
    if tag:
        tx(s, x + w - 1.6, y + 0.22, 1.45, 0.3, tag, size=10.5, color=LGRAY, align=PP_ALIGN.RIGHT)
    tx(s, x + 0.2, y + 0.66, w - 0.4, h - 0.78, body, size=bsize, color=INK, line=1.3)

def table(s, x, y, w, rows, fsize=11, hrow=0.42, widths=None):
    shp = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(hrow * len(rows)))
    t = shp.table
    if widths:
        tot = sum(widths)
        for j, ww in enumerate(widths):
            t.columns[j].width = Emu(int(Inches(w) * ww / tot))
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(hrow)
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = str(v)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = Inches(0.06); c.margin_right = Inches(0.06)
            c.margin_top = Inches(0.02); c.margin_bottom = Inches(0.02)
            for p in c.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                p.line_spacing = 1.05
                for r in p.runs:
                    r.font.size = Pt(fsize); r.font.name = '微软雅黑'
                    r.font.color.rgb = WHITE if i == 0 else INK
                    if i == 0: r.font.bold = True
            if i == 0:
                c.fill.solid(); c.fill.fore_color.rgb = NAVY
            elif i % 2 == 0:
                c.fill.solid(); c.fill.fore_color.rgb = SOFT
    return t

def fullpic(s, path, y=1.5, w=12.1):
    if os.path.exists(path):
        s.shapes.add_picture(path, Inches(0.62), Inches(y), width=Inches(w))

# ══════════════ 1 封面
s = slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0, 0, 13.333, 0.12, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 1.25, 11.2, 0.5, "创客训练营 · 项目汇报　|　面向创客竞赛的老师们", size=13.5, color=TEAL)
tx(s, 1.1, 1.85, 11.4, 1.8, "把技术开源，\n把客流做起来", size=46, bold=True, color=WHITE, line=1.16)
rect(s, 1.12, 4.0, 2.2, 0.045, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 4.35, 11.4, 1.5,
   "一个开源项目的获客逻辑与盈利链条\n"
   "—— 我们不再问「技术还能做什么」，而是问「谁会来、为什么来、怎么留住」",
   size=16, color=C(205, 216, 232), line=1.5)
tx(s, 1.1, 6.15, 11.4, 0.9,
   "磁吸焊接辅助手电 · 1 班 C 组 仿真跑不队：邵子中 / 李昊桐 / 姜亚楷　|　指导老师提供 CW32L010 开发板与工程框架",
   size=12, color=C(178, 192, 212))
for r in (2.9, 2.25, 1.6):
    rect(s, 11.55 - r/2 + 1.5, 3.72 - r/2 + 1.5, r, r, fill=None, line=C(30, 60, 98), lw=1.6, shape=MSO_SHAPE.OVAL)
rect(s, 12.35, 5.35, 0.62, 0.062, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
rect(s, 12.35, 5.52, 0.38, 0.062, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)

# ══════════════ 2 一页看懂
s = slide(); head(s, "摘要", "一页看懂：开源怎么带来客流，客流怎么变成收入", "这不是一份技术汇报，而是一条能被复制的商业逻辑")
card(s, 0.62, 1.6, 4.0, 2.5, "第一步：开源 → 获客",
     "把设计 / 固件 / 文档 / 踩坑全部公开\n（MIT），让它成为一份「人人都能验证\n的信任物料」：\n"
     "· 客户与学校敢买、敢推荐\n· 不再依赖付费投放，用户主动找来", col=TEAL, bsize=11.5)
card(s, 4.75, 1.6, 4.0, 2.5, "第二步：客流 → 反哺",
     "使用反馈决定迭代优先级；社区共建\n补上研发力量；教学场景带来批量需求；\n"
     "口碑让后续获客成本继续下降。\n"
     "· 客流不是终点，是研发与收入的源头", col=BLUE, bsize=11.5)
card(s, 8.88, 1.6, 3.85, 2.5, "第三步：回流 → 盈利",
     "开的是「知识与设计」，卖的是\n「成品、套件、确定性与服务」：\n"
     "· C 端成品机 65 元\n· DIY 套件 ≈49 元\n· B 端实训采买（批量、零获客）", col=GOLD, bsize=11.5)
yy = 4.4
kpi(s, 0.62, yy, 2.3, 2.0, "¥8.6", "地推获客成本", "线上 ¥31.8 已停投", TEAL)
kpi(s, 3.14, yy, 2.3, 2.0, "37.3%", "行为支付率", "1 元意向金真付费", NAVY)
kpi(s, 5.66, yy, 2.3, 2.0, "22", "台 B 端首单", "零获客成本", GREEN)
kpi(s, 8.18, yy, 2.3, 2.0, "33.8%", "量产毛利率", "小批 11.2% → 量产", GOLD)
kpi(s, 10.7, yy, 2.03, 2.0, "2,886", "台保本线", "降级目标 1,232 台", RED)

# ══════════════ 3 思维转变（训练痕迹）
s = slide(); head(s, "训练带来的变化", "我们最实质的变化：从「技术思维」到「客流思维」",
                  "技术做好只是起点；技术商品要先有客流，才能活下去")
card(s, 0.62, 1.6, 5.95, 2.55, "过去：用技术看「能做什么」",
     "· 想的是：参数能不能更好、功能能不能更多\n"
     "· 做出来一台设备，然后呢？——没人知道、没人买\n"
     "· 看到开源会问：「开源＝白送，图什么？」\n"
     "· 结果：技术停在桌面上，价值没有被看见", col=GRAY, bsize=12)
card(s, 6.78, 1.6, 5.94, 2.55, "现在：用客流看「谁会来、为什么来」",
     "· 想的是：客流从哪来、谁愿意买、怎么让别人愿意试\n"
     "· 把设计/固件/文档全部开源，让它成为可验证的信任物料\n"
     "· 用实测算清每个渠道的获客成本，再决定投不投钱\n"
     "· 结果：技术被看见、被使用，并开始产生订单", col=TEAL, bsize=12)
card(s, 0.62, 4.35, 12.1, 2.2, "一次点拨，改变了我们的判断",
     "在与老师的交流中我们意识到：技术商品需要客流才能活下去——再好的技术，如果没有用户、没有订单，就只是实验室里的作品。\n"
     "所以我们做了一个决定：把这个项目做成开源项目。\n"
     "开源不是放弃盈利，而是换一种活法：用开源获得信任和客流，再用客流反哺技术与项目——客流让我们知道该改什么，也让产品真正卖得动。\n"
     "这也是我们参加训练最实在的收获：从「我能做什么」，走到「谁会来、为什么来、怎么留住」。", col=GOLD, bsize=12)

# ══════════════ 4 开源获客逻辑（整页图）
s = slide(); head(s, "获客逻辑", "为什么开源是最好的获客方式（图：一个越转越省的正循环）",
                  "别人看到「失去」，我们看到「降低信任成本 + 降低分发成本 + 拿到精准客流」")
fullpic(s, os.path.join(FIGS, "fig4_开源获客逻辑.png"), y=1.5, w=12.1)

# ══════════════ 5 渠道与实测
s = slide(); head(s, "获客逻辑", "客流从哪来：我们用实测数据决定投哪个渠道", "任何渠道在投钱之前，先算 CAC，再与 LTV 对比——这是我们定下的准则")
table(s, 0.62, 1.6, 12.1, [
    ["渠道", "性质", "转化率", "获客成本", "结论"],
    ["开源 + 教师/同学推荐", "信任驱动（获客引擎）", "—", "≈ ¥0", "B 端首单 22 台，零获客成本"],
    ["实验室 / 课堂地推", "面对面演示", "34.9%", "¥8.6 / 人", "最优渠道：加投并标准化话术"],
    ["社团与班级扩散", "口碑扩散", "27.1%", "¥11.5 / 人", "维持：靠复购与口碑（NPS 42）"],
    ["线上投放", "付费买流量", "5.2%", "¥31.8 / 人", "LTV/CAC 0.83 ✗ 立即停投"],
], fsize=11, hrow=0.62, widths=[3.0, 2.6, 1.4, 1.8, 3.3])
card(s, 0.62, 4.6, 5.95, 1.95, "开源在这里起什么作用",
     "· 让「信任」先于「销售」发生：可复现、可审查、可评估\n"
     "· 让教师和机构能自己判断值不值得买\n"
     "· 学生看完开源就能自己装出一台 —— 成交不需要解释成本", col=TEAL, bsize=11.5)
card(s, 6.78, 4.6, 5.94, 1.95, "为什么停掉线上投放",
     "· 花了 ¥350，只换来 11 条留资（CAC ¥31.8）\n"
     "· 单台毛利远低于获客成本（LTV/CAC 0.83）\n"
     "· 资源转向地推 + B 端：一个靠自己讲，一个靠口碑与信任", col=RED, bsize=11.5)

# ══════════════ 6 客流反哺
s = slide(); head(s, "客流反哺", "客流进来之后：它反过来养技术与项目", "这就是我们坚持开源的理由——客流是研发、迭代与收入的共同源头")
card(s, 0.62, 1.6, 3.95, 4.4, "① 反馈决定迭代",
     "用户怎么用、哪里不好用，直接告诉我们\n下一步改什么：\n\n"
     "· 焊台狭小 → 磁吸与柔臂做小、做稳\n"
     "· 担心屏幕亮影响焊接 → LED 指示 + 屏幕扩展并存\n"
     "· 有人嫌贵 → 保留 DIY 套件路线（≈49 元）\n\n"
     "→ 没有客流，就只能凭想象改产品", col=TEAL, bsize=11.5)
card(s, 4.72, 1.6, 3.95, 4.4, "② 共建补上研发",
     "把设计、固件、文档开放出去，会有人愿意\n一起改：\n\n"
     "· 外部可以提交改进（硬件替代件、结构件、固件补丁）\n"
     "· 使用者会把踩过的坑写回来\n"
     "· 教学场景会提出真实需求（实训套件）\n\n"
     "→ 相当于获得了一支免费的、真实的研发队伍", col=BLUE, bsize=11.5)
card(s, 8.82, 1.6, 3.9, 4.4, "③ 教学场景 → 批量收入",
     "开源学习包天然适配课堂：\n\n"
     "· 教师可直接把它当项目式课程包\n"
     "· 学校/实训机构按批采买（B 端 22 台首单）\n"
     "· 目标：B 端占比 45%，且获客成本为 0\n\n"
     "→ 客流不只带来零售，更带来稳定的批量订单", col=GOLD, bsize=11.5)

# ══════════════ 7 盈利链条（整页图）
s = slide(); head(s, "盈利链条", "开源免费的部分获客，付费的部分赚钱", "开的是「知识与设计」，卖的是「成品、套件、确定性与服务」——两者不矛盾")
fullpic(s, os.path.join(FIGS, "fig5_盈利链条.png"), y=1.5, w=12.1)

# ══════════════ 8 开源与付费的边界
s = slide(); head(s, "盈利链条", "我们把边界划清楚：什么免费、什么收费", "免费的部分越彻底，客流和信任来得越快；收费的部分越具体，越卖得动")
table(s, 0.62, 1.6, 12.1, [
    ["", "免费开源（获客）", "付费（盈利）"],
    ["设计文件", "原理图 / PCB / BOM / 3D 打印件全部公开", "不含"],
    ["固件代码", "全部源码 + 9 模块学习课程 + 踩坑实录", "不含"],
    ["成品", "不含（自己动手是免费的）", "整机 65 元/台（含装配、测试、质保）"],
    ["套件", "不含", "DIY 套件 ≈49 元/套（3D 打印外壳 + 元件）"],
    ["确定性与服务", "不含", "B 端批量采买：交付、教学支持、备件（批量议价）"],
], fsize=11, hrow=0.6, widths=[2.2, 5.0, 4.9])
card(s, 0.62, 5.15, 12.1, 1.45, "一句话说清这个模式",
     "开源负责把「信任」做厚（信任＝获客成本），付费负责把「确定性」卖出（交付、质保、教学支持、批量稳定）。\n"
     "我们卖的不是知识——知识已经公开了；我们卖的是「省时间、有保障、能批量交付」的确定性。", col=GOLD, bsize=12)

# ══════════════ 9 盈利信心
s = slide(); head(s, "盈利信心", "为什么我们相信这条路能赚钱：六项实测数据",
                  "不是口号，每一条都有可核验的原始记录（结题报告 E-01~E-15）")
yy = 1.6
kpi(s, 0.62, yy, 2.3, 2.1, "37.3%", "行为支付率", "1 元可退意向金，22/59 真付费", TEAL)
kpi(s, 3.14, yy, 2.3, 2.1, "¥8.6", "地推获客成本", "线上 ¥31.8（已停）", NAVY)
kpi(s, 5.66, yy, 2.3, 2.1, "22", "台 B 端首单", "零获客成本，已交付", GREEN)
kpi(s, 8.18, yy, 2.3, 2.1, "33.8%", "量产毛利率", "小批 11.2% → 量产", GOLD)
kpi(s, 10.7, yy, 2.03, 2.1, "2,886", "台保本线", "降级目标 1,232 台", RED)
card(s, 0.62, 4.1, 3.95, 2.45, "需求是真的",
     "· 态度数据 71.3% 说会买，行为数据 37.3%\n  真的付了 1 元——我们只信后者\n"
     "· NPS 42（使用者愿意推荐）", col=TEAL, bsize=11.5)
card(s, 4.72, 4.1, 3.95, 2.45, "渠道是算得清的",
     "· 地推 ¥8.6、口碑 ¥11.5，线上 ¥31.8\n"
     "· 已有渠道能撑起零售，开源与 B 端\n  把获客成本压到 0", col=BLUE, bsize=11.5)
card(s, 8.82, 4.1, 3.9, 2.45, "账是算得完的",
     "· BOM ¥52.3（小批）→ 目标 ¥43.0\n"
     "· 量产毛利 33.8%；保本 2,886 台，\n  降级方案（3D 打印）1,232 台\n"
     "· 现金流不需要重资产投入", col=GOLD, bsize=11.5)

# ══════════════ 10 过程与下一步
s = slide(); head(s, "过程与下一步", "我们是怎么走通这条逻辑的（也是我们想展示的「过程」）",
                  "从发现需求，到算出渠道，到拿到订单，再到决定开源——每一步都由数据推动")
steps = [("① 发现需求", "126 份问卷 + 60 人实景观察\n把「不好用」变成可测数字"), 
         ("② 做出样机", "小批试产，BOM ¥52.3\n实测成本高于预估 → 重算经济账"),
         ("③ 跑渠道", "地推 ¥8.6 / 社团 ¥11.5 / 线上 ¥31.8\n算清 CAC 后，停线上、转地推"),
         ("④ 拿订单", "老师牵线，B 端首单 22 台\n零获客成本，验证批量需求"),
         ("⑤ 决定开源", "把设计/固件/文档全部开放\n用开源换信任与客流，形成正循环")]
bw, bg = 2.36, 0.21
for i, (t, body) in enumerate(steps):
    x = 0.62 + i * (bw + bg)
    col = [TEAL, BLUE, GOLD, GREEN, RED][i]
    card(s, x, 1.6, bw, 2.5, t, body, col=col, tsize=13.5, bsize=10)
    if i < 4:
        tx(s, x + bw + 0.02, 2.7, 0.2, 0.3, "▶", size=12, color=LGRAY, align=PP_ALIGN.CENTER)
card(s, 0.62, 4.35, 5.95, 2.2, "下一步（已经在做）",
     "· 锁定千片报价：把量产毛利做到 33.8%\n"
     "· 拓 B 端：目标占比 45%（教学包 + 实训采买）\n"
     "· 社区共建：把外部改进并入版本，继续摊薄研发成本", col=GREEN, bsize=11.5)
card(s, 6.78, 4.35, 5.94, 2.2, "我们希望老师看到的三件事",
     "① 一个团队已经能从「技术能做什么」转向「客流从哪来」——这是训练留下的思维方式\n"
     "② 一条能被别的团队复制的获客逻辑：开源 → 信任 → 客流 → 反哺\n"
     "③ 一份有真实数据支撑的盈利信心，而不是一厢情愿", col=TEAL, bsize=11.5)

# ══════════════ 11 结尾
s = slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0, 7.38, 13.333, 0.12, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 1.95, 11.2, 1.4, "技术商品需要客流才能活下去。\n开源，是我们找到的那条路", size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER, line=1.35)
rect(s, 5.55, 3.75, 2.2, 0.045, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.4, 4.05, 10.5, 1.7,
   "开源 → 信任 → 客流 → 反哺技术与项目 → 成品卖得动\n"
   "37.3% 行为支付率 · ¥8.6 地推获客 · 22 台 B 端首单 · 33.8% 量产毛利 · 2,886 台保本",
   size=14.5, color=C(205, 216, 232), align=PP_ALIGN.CENTER, line=1.6)
tx(s, 1.1, 5.95, 11.2, 0.9, "1 班 C 组 · 仿真跑不队：邵子中 / 李昊桐 / 姜亚楷　|　敬请老师们指正",
   size=12.5, color=C(150, 165, 190), align=PP_ALIGN.CENTER)

prs.save(FNAME)
print("PPT V4.0 saved:", FNAME)
print("页数:", len(prs.slides._sldIdLst))
