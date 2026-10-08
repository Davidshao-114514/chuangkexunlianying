# -*- coding: utf-8 -*-
"""演示 PPT V3.0（美化版 · 面向创客竞赛老师）
叙事核心：不是一台灯，而是一套可复制的创业逻辑与盈利链条；突出创客训练效果
设计体系：深蓝/青/金 三色 + 统一页眉页脚 + KPI 大数字 + 信息图整页
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
FNAME = os.path.join(OUT, "磁吸焊接辅助手电_可复制的创业逻辑_汇报PPT.pptx")

NAVY = C(18, 41, 74); TEAL = C(18, 181, 176); GOLD = C(217, 164, 56)
RED = C(200, 60, 55); GREEN = C(36, 150, 96); GRAY = C(108, 120, 138)
LGRAY = C(168, 176, 188); WHITE = C(255, 255, 255); INK = C(45, 55, 72)
SOFT = C(243, 246, 250); PANEL = C(247, 249, 252)

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def slide():
    return prs.slides.add_slide(BLANK)

def tx(s, x, y, w, h, text, size=13, bold=False, color=INK, align=PP_ALIGN.LEFT, line=1.25, font='微软雅黑'):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, ln in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = line
        r = p.add_run(); r.text = ln
        f = r.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = font
    return tb

def rect(s, x, y, w, h, fill=None, line=None, lw=1.2, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=None):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius is not None:
        try: sp.adjustments[0] = radius
        except Exception: pass
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    return sp

PAGE = {"n": 1}   # 封面不编号，故从 1 起算 → 第 2 张幻灯片显示 "02"
def head(s, section, title, sub=None, page=True):
    """统一页眉：左侧竖色条 + 小节名 + 标题 + 细分隔线 + 页码"""
    PAGE["n"] += 1
    rect(s, 0, 0, 0.085, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0.62, 0.42, 0.055, 0.42, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
    tx(s, 0.82, 0.42, 8.0, 0.42, title, size=25, bold=True, color=NAVY)
    tx(s, 0.84, 0.93, 11.5, 0.32, sub or "", size=11.5, color=GRAY)
    rect(s, 0.62, 1.34, 12.1, 0.02, fill=C(222, 228, 238), shape=MSO_SHAPE.RECTANGLE)
    tx(s, 0.62, 0.06, 6.0, 0.3, section, size=10.5, color=LGRAY)
    if page:
        tx(s, 12.3, 6.98, 0.6, 0.3, f"{PAGE['n']:02d}", size=10.5, color=LGRAY, align=PP_ALIGN.RIGHT)

def kpi(s, x, y, w, h, num, unit, label, col=TEAL):
    """KPI 卡：大数字 + 单位 + 说明（文案需短，unit ≤ 12 字、label ≤ 16 字）"""
    rect(s, x, y, w, h, fill=PANEL, line=col, lw=1.4)
    tx(s, x + 0.1, y + 0.24, w - 0.2, 0.7, num, size=32, bold=True, color=col, align=PP_ALIGN.CENTER)
    tx(s, x + 0.08, y + 0.92, w - 0.16, 0.3, unit, size=11, color=GRAY, align=PP_ALIGN.CENTER)
    tx(s, x + 0.08, y + 1.26, w - 0.16, 0.66, label, size=10.5, color=INK, align=PP_ALIGN.CENTER, line=1.2)

def card(s, x, y, w, h, title, body, col=NAVY, tsize=15.5, bsize=11.5, tag=None):
    rect(s, x, y, w, h, fill=PANEL, line=col, lw=1.5)
    rect(s, x, y, w, 0.055, fill=col, shape=MSO_SHAPE.RECTANGLE)
    tx(s, x + 0.2, y + 0.2, w - 0.4, 0.4, title, size=tsize, bold=True, color=col)
    if tag:
        tx(s, x + w - 1.55, y + 0.24, 1.4, 0.3, tag, size=10.5, color=LGRAY, align=PP_ALIGN.RIGHT)
    tx(s, x + 0.2, y + 0.68, w - 0.4, h - 0.8, body, size=bsize, color=INK, line=1.3)

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

def fullpic(s, path, y=1.5, h=None, w=12.1, x=0.62):
    if os.path.exists(path):
        kw = {"width": Inches(w)} if h is None else {"height": Inches(h)}
        s.shapes.add_picture(path, Inches(x), Inches(y), **kw)

# ══════════════ 1 封面
s = slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0, 0, 13.333, 0.12, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 1.35, 11.2, 0.5, "创客训练营 · 项目汇报　|　面向创客竞赛的老师们", size=13.5, color=TEAL)
tx(s, 1.1, 2.0, 11.4, 1.8, "不是一台灯，\n是一套可复制的创业逻辑", size=42, bold=True, color=WHITE, line=1.18)
rect(s, 1.12, 4.15, 2.2, 0.045, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 4.5, 11.4, 1.2,
   "磁吸焊接辅助手电 · 从用户洞察到盈利链条的完整闭环\n"
   "方法可复制 · 数据可核验 · 成果可教学——手电只是它的载体", size=15, color=C(205, 216, 232), line=1.5)
tx(s, 1.1, 6.15, 11.4, 0.9,
   "1 班 C 组 · 仿真跑不队：邵子中 / 李昊桐 / 姜亚楷　|　指导老师提供 CW32L010 开发板与工程框架",
   size=12.5, color=C(178, 192, 212))
# 右侧几何装饰（同心弧 + 色块），填补空白
for r, alpha_col in [(2.9, C(26, 52, 88)), (2.25, C(30, 60, 98)), (1.6, C(34, 70, 112))]:
    rect(s, 11.15 - r/2 + 1.6, 3.75 - r/2 + 1.6, r, r, fill=None, line=alpha_col, lw=1.6, shape=MSO_SHAPE.OVAL)
rect(s, 12.35, 5.35, 0.62, 0.062, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
rect(s, 12.35, 5.52, 0.38, 0.062, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
rect(s, 12.35, 5.69, 0.5, 0.062, fill=C(70, 100, 140), shape=MSO_SHAPE.RECTANGLE)

# ══════════════ 2 一页看懂
s = slide(); head(s, "摘要", "一页看懂：我们做了什么、学到什么、留下什么")
card(s, 0.62, 1.6, 4.0, 2.45, "做了什么", 
     "• 从 126 份问卷与 60 人实景观察，做出一台\n　能用的小批量产品（¥43 级 BOM）\n"
     "• 拿到 22 台 B 端首单、312 条验证数据\n"
     "• 完成从原型到定价、渠道、保本的完整商业闭环", col=TEAL, bsize=11.5)
card(s, 4.75, 1.6, 4.0, 2.45, "学到什么",
     "• 一套「洞察 → 假设 → 验证 → 迭代」的\n　可复制流程（每一步都有判据）\n"
     "• 用行为数据做决策（态度 71.3% ≠ 行为 37.3%）\n"
     "• 用实测推翻预测（毛利 40% → 11.2%）", col=NAVY, bsize=11.5)
card(s, 8.88, 1.6, 3.85, 2.45, "留下什么",
     "• 开源学习包：9 模块课程 + 12 模块固件\n　+ 14 项验收判据 + 完整踩坑实录\n"
     "• 全部硬件/固件/结构/文档公开\n"
     "• 让下一个团队不必从零开始", col=GOLD, bsize=11.5)
yy = 4.35
kpi(s, 0.62, yy, 2.3, 2.0, "312", "条验证数据", "中期 157 → 312，翻倍", TEAL)
kpi(s, 3.14, yy, 2.3, 2.0, "37.3%", "意向金支付率", "行为口径（22/59 真付费）", NAVY)
kpi(s, 5.66, yy, 2.3, 2.0, "22", "台 B 端首单", "老师牵线，零获客成本", GREEN)
kpi(s, 8.18, yy, 2.3, 2.0, "¥8.6", "地推获客成本", "线上 ¥31.8 已停投", GOLD)
kpi(s, 10.7, yy, 2.03, 2.0, "L4", "团队能力等级", "按证据给，不按心情给", RED)

# ══════════════ 3 训练效果（图3整页）
s = slide(); head(s, "创客训练的效果", "训练的效果可以量化：把中期与结题放在一起看", "四条曲线在变好；另一条（毛利率预估）被我们主动按住了——这正是训练的结果")
fullpic(s, os.path.join(FIGS, "fig3_训练效果.png"), y=1.55, w=12.1)
tx(s, 0.62, 6.75, 12.1, 0.5, "数据来源：结题报告 V2.0 表 1-1 / 表 1-3（可核验）；PPT 内所有数字均可在报告中定位到原始记录编号", size=10, color=LGRAY)

# ══════════════ 4 能力怎么长出来的
s = slide(); head(s, "创客训练的效果", "能力不是「学会了」，是被真实问题逼出来的", "每一格都有可核验的证据编号，不是形容词")
table(s, 0.62, 1.6, 12.1, [
    ["能力维度", "真实挑战（事件）", "我们的行动", "结果 / 等级"],
    ["硬件攻坚", "0.5\" CH1115 屏四轮点不亮；ADC 读数恒定；低亮度频闪", "查厂家官方序列、改 BGR 反推、频率 5 次迭代", "屏点亮、电压准、8kHz 无频闪（L4）"],
    ["数据决策", "1 元意向金 20/62 人支付，而问卷 71.3% 说会买", "用行为口径替换态度口径，重设北极星", "意向金支付率 37.3%（L4）"],
    ["商业建模", "原估毛利 40% vs 小批实测 11.2%", "5Why 追因，重建单位经济与保本模型", "保本线 400 → 2,886 台（L4）"],
    ["渠道判断", "线上投放 ¥350 只换 11 条留资（CAC ¥31.8）", "建渠道 CAC 表，确立「先算 CAC 再投钱」", "停线上、转地推与 B 端（L4）"],
    ["协作与交付", "温升越界、机壳备料缺口、排期冲突", "设底线触发机制，触发即冻结并改方案", "22 台首单按期交付（L3 / L4）"],
], fsize=11, hrow=0.72, widths=[1.5, 3.1, 3.3, 2.6])
tx(s, 0.62, 6.5, 12.1, 0.6, "一句话总结训练效果：我们从「把事情做出来」升级到「用数据决定该不该做、值不值得做」。", size=12.5, bold=True, color=NAVY)

# ══════════════ 5 核心观点
s = slide(); head(s, "核心观点", "手电只是载体：真正可交付的是三件「可复制资产」", "如果只看到灯，这个项目就白做了；老师要看的应该是它能不能被复制到下一个团队")
card(s, 0.62, 1.6, 3.95, 4.3, "① 一套洞察方法",
     "从真实使用者身上取数的具体做法：\n\n"
     "• 126 份有效问卷（分层抽样）\n"
     "• 60 名工人的实景观察与动作计数\n"
     "• 把「感觉不好用」翻译成可测数字：\n"
     "　找光动作次数、返工焊点数、桌面占用比例\n\n"
     "→ 换任何选题，这套取数方法都能直接复用", col=TEAL, bsize=11.5)
card(s, 4.72, 1.6, 3.95, 4.3, "② 一套验证闭环",
     "把「我觉得」变成「数据说明」：\n\n"
     "• 1 元可退意向金（行为口径）\n"
     "• A/B 对照（LED 82% vs OLED 86%）\n"
     "• 渠道实测 CAC（¥8.6 / ¥11.5 / ¥31.8）\n"
     "• 保本销量模型（2,886 台）\n"
     "• 失败就改：9 处结论修订、4 处由评审触发\n\n"
     "→ 让决策有据，而不是靠气势", col=NAVY, bsize=11.5)
card(s, 8.82, 1.6, 3.9, 4.3, "③ 一套盈利链条",
     "从成本到规模的完整算式：\n\n"
     "BOM ¥52.3（小批）→ 定价 59–69 元\n"
     "→ 毛利率 11.2%（小批）→ 33.8%（量产）\n"
     "→ 获客 ¥8.6 起 → 保本 2,886 台\n"
     "→ 三条路径：C 端 / DIY 套件 / B 端\n\n"
     "→ 换产品，链条结构照样成立", col=GOLD, bsize=11.5)

# ══════════════ 6 创业逻辑闭环（图1整页）
s = slide(); head(s, "可复制的创业逻辑", "四步闭环：每一步都有输入、判据、输出", "这套流程不依赖灵光一现——它是可以教、可以练、可以复制的")
fullpic(s, os.path.join(FIGS, "fig1_创业逻辑闭环.png"), y=1.52, w=12.1)

# ══════════════ 7 洞察细节
s = slide(); head(s, "可复制的创业逻辑 · ① 洞察", "把「不好用」变成数字：我们怎么取数", "方法与数据都可核验，替换选题后直接复用")
card(s, 0.62, 1.6, 5.95, 2.35, "取数方式（可复制）",
     "• 问卷：126 份有效样本，分层抽样（覆盖度 88%）\n"
     "• 实景观察：60 名工人，记录动作次数与失误\n"
     "• 自我记录：17 个焊点返工 3 次；台灯底座占桌 1/4\n"
     "• 三家对比访谈（同类用户/竞品用户/流失用户）", col=TEAL, bsize=11.5)
card(s, 6.78, 1.6, 5.94, 2.35, "取到的关键事实",
     "• 找光/挪灯动作：每人每次任务平均 4.2 次\n"
     "• 13/15 次「灯头偏移后未复位」\n"
     "• 焊接失败率：50%（焊接新手，0603 器件）\n"
     "• 现有方案痛点：台灯占位 / 廉价灯夹不稳 / 专业灯贵", col=NAVY, bsize=11.5)
card(s, 0.62, 4.15, 12.1, 2.3, "价值主张（由洞察直接推出）",
     "一句话定位：给高校电子类专业学生与 DIY 极客，解决狭小焊台「灯照不到、靠不住、要手扶」的问题。\n"
     "核心价值：给焊接者一双腾出来的手——磁吸固定、万向悬停、无级调光，百元内可得（主线 65 元）。\n"
     "量化目标：找光动作每次减少 4.2 次；焊接失败率 50% → 20%；任务完成率 ≥85%；意向金支付率（行为口径）≥30%。\n"
     "　→ 注意最后一条：目标从一开始就写成「行为口径」，这决定了后面所有决策的方向。", col=GOLD, bsize=11.5)

# ══════════════ 8 验证细节
s = slide(); head(s, "可复制的创业逻辑 · ② 验证", "用行为数据杀假设：一次 1 元钱的实验", "「说会买」和「真的掏钱」差了一倍——这是我们最重要的一次认知修正")
card(s, 0.62, 1.6, 5.95, 2.5, "实验设计（最小成本）",
     "• 1 元可退意向金（真金白银的行为口径）\n"
     "• A/B 对照：无屏 LED 版 vs OLED 版\n"
     "• 实测样本：59 人意向金池 / 62 人问卷对照\n"
     "• 成本：现金 ¥0（自有设备 + 免费渠道）", col=TEAL, bsize=11.5)
card(s, 6.78, 1.6, 5.94, 2.5, "结果（诚实版）",
     "• 问卷态度口径：71.3% 说「会买」\n"
     "• 行为口径：37.3% 真的付了 1 元（22/59）\n"
     "• A 组预售转化 31.8%\n"
     "• A/B 覆盖率：LED 82% vs OLED 86%（差 4 个百分点）\n"
     "→ 结论：LED 标配成立，OLED 转选配", col=RED, bsize=11.5)
table(s, 0.62, 4.35, 12.1, [
    ["被验证的假设", "验证方式", "数据结果", "决策"],
    ["用户愿意为「磁吸+无级调光」付费", "1 元可退意向金", "37.3%（22/59）", "保留该价值主张，纳入 MVP"],
    ["无屏 LED 会显著降低满意度", "A/B 对照（20 人）", "覆盖 82% vs 86%", "LED 标配 + OLED 选配"],
    ["58–79 元价格带可接受", "定价测试 + 预售转化", "收敛至 59–69 元", "标准版定价 65 元"],
    ["线上渠道能低成本获客", "渠道实测 CAC", "LTV/CAC 0.83 ✗", "停线上，转地推与 B 端"],
], fsize=11, hrow=0.56, widths=[2.6, 2.4, 2.2, 3.0])

# ══════════════ 9 渠道决策
s = slide(); head(s, "可复制的创业逻辑 · ③ 迭代", "一个可以写进教科书的决策：先算 CAC 再投钱", "这不是理论推导，是我们花 ¥350 学费换来的判断")
table(s, 0.62, 1.6, 12.1, [
    ["渠道", "转化率", "获客成本 CAC", "判断", "行动"],
    ["实验室/课堂地推", "34.9%", "¥8.6 / 人", "最优", "加投，话术标准化（10 分钟发现 2 个痛点）"],
    ["社团与班级扩散", "27.1%", "¥11.5 / 人", "次优", "维持，靠口碑（NPS 42）"],
    ["线上投放", "5.2%", "¥31.8 / 人", "最差（LTV/CAC 0.83）", "立即停止，¥350 只换 11 条留资"],
    ["B 端实训采买", "—", "0（老师牵线）", "零获客成本", "重点：22 台首单，目标占比 45%"],
], fsize=11, hrow=0.62, widths=[2.4, 1.4, 2.0, 2.4, 3.9])
card(s, 0.62, 4.55, 12.1, 1.9, "由此确立的一条原则（可复制到任何团队）",
     "任何渠道在投钱之前，先算出 CAC，并与 LTV 对比：LTV/CAC < 1 的渠道，不管「传播性」多好都立刻停掉。\n"
     "我们把这条写进了团队的工作准则，并用它做出了「线上 → 地推 + B 端」的资源转移决策。\n"
     "结果：B 端零获客成本拿到 22 台首单；地推贡献了我们最主要的验证数据。", col=GOLD, bsize=11.5)

# ══════════════ 10 盈利链条（图2整页）
s = slide(); head(s, "盈利链条", "从 ¥43 的 BOM 到可复制的三档生意", "链条能不能通，看最窄处——我们把自己的算法错了又改对，链条才真正算得通")
fullpic(s, os.path.join(FIGS, "fig2_盈利链条.png"), y=1.5, w=12.1)

# ══════════════ 11 三档路径对比
s = slide(); head(s, "盈利链条", "三条路径怎么选：单位经济对比", "同一套方法，三种变现结构；我们选择「C 端验证 + B 端放量 + DIY 兜底」")
table(s, 0.62, 1.6, 12.1, [
    ["维度", "C 端零售", "DIY 套件", "B 端实训采买（重点）"],
    ["定价", "65 元/台（59–69）", "≈ 49 元/套", "批量议价（按 20+ 台签）"],
    ["成本/毛利", "小批 BOM ¥52.3，毛利率 11.2%", "自装 + 3D 打印，成本更低", "量产 33.8%（锁定千片报价后）"],
    ["获客成本", "地推 ¥8.6 / 社团 ¥11.5", "近零（社群自然扩散）", "0（渠道即学校/实验室）"],
    ["规模与节奏", "走量薄利，靠复购（NPS 42）", "小批量，随时可出", "22 台首单 → 目标占比 45%"],
    ["风险", "价格敏感、竞品多", "客单价低", "依赖学校采买周期"],
    ["一句话", "验证需求，收集口碑", "学生的入门选择", "把方法卖成「可复制的教学资产」"],
], fsize=10.5, hrow=0.62, widths=[1.7, 3.3, 3.0, 3.6])
tx(s, 0.62, 6.35, 12.1, 0.7, "保本与底线：小批量口径保本 2,886 台；若 B 端放量不及预期，退回 3D 打印路径（降级目标 1,232 台保本线）。", size=12, bold=True, color=RED)

# ══════════════ 12 可复制性验证
s = slide(); head(s, "可复制性", "这套方法已经迁移过一次：同一个团队，换一个选题", "如果在别的题目上照样能跑通，才说明它是「方法」而不是「运气」")
card(s, 0.62, 1.6, 5.95, 4.4, "迁移案例：课堂「泡茶项目」管理演练",
     "把同一套方法（范围界定 → 三级 WBS → 甘特图与关键路径\n→ 成本核算 → 风险登记册）用于一个完全不同的题目：\n\n"
     "• 5 分钟绿茶冲泡服务，总工期硬压到 300 秒\n"
     "• 识别出「自然冷却 3-5 分钟」是最大瓶颈，\n"
     "　用热冷勾兑改造为 15 秒\n"
     "• 五阶段分解、关键路径 299 秒落地、利润 26.2 元\n"
     "• 抽到毛峰时浸泡需 120 秒 → 主动提交工期变更申请\n\n"
     "→ 方法在工作量、风险、成本上都能给出可执行答案", col=TEAL, bsize=11.5)
card(s, 6.78, 1.6, 5.94, 4.4, "换一个团队能不能跑？（可复制清单）",
     "我们把这套流程写成了「可交接」的形式：\n\n"
     "① 取数模板：问卷 + 实景观察记录表\n"
     "② 判据模板：ICE 评分、A/B 对照、CAC 表\n"
     "③ 商业模型：BOM → 毛利 → 保本 → 三路径\n"
     "④ 决策准则：先算 CAC；行为口径优先；底线触发即冻结\n"
     "⑤ 全部写成开源文档（9 模块课程 + 14 项验收判据）\n\n"
     "→ 结论：它不依赖我们三个人的特殊能力，\n"
     "　 依赖的是「有判据的流程」", col=GOLD, bsize=11.5)

# ══════════════ 13 开源学习包
s = slide(); head(s, "留给下一届的东西", "开源学习包：把方法变成公共资产", "这是「可复制」的最终形态——不是我们说能复制，而是别人真的可以拿去用")
kpi(s, 0.62, 1.6, 2.3, 1.85, "9", "个学习模块（16–24 学时）", "从看懂整机到复盘踩坑", TEAL)
kpi(s, 3.14, 1.6, 2.3, 1.85, "12", "个固件模块（BSP 分层）", "Flash 12KB / RAM 1.1KB", NAVY)
kpi(s, 5.66, 1.6, 2.3, 1.85, "14", "项验收判据", "含测试方法与阈值", GREEN)
kpi(s, 8.18, 1.6, 2.3, 1.85, "8", "篇学习文档", "含开发踩坑实录", GOLD)
kpi(s, 10.7, 1.6, 2.03, 1.85, "MIT", "开源许可", "硬件 + 固件 + 结构", RED)
card(s, 0.62, 3.7, 5.95, 2.35, "学习包里有什么",
     "• 固件：CW32L010 分层 BSP（12 模块）、Keil 工程、标准库\n"
     "• 硬件：立创EDA 原理图/PCB、BOM（34 行 56 位号）、数据手册\n"
     "• 结构：外壳/盖子/按键帽/散热片（STEP 可直接打印）\n"
     "• 文档：定位 / 学习路径 / 硬件 / 固件 / 复现 / 验收 / 教学 / 踩坑实录", col=TEAL, bsize=11)
card(s, 6.78, 3.7, 5.94, 2.35, "为什么它比一块开发板更有收获",
     "• 项目式学习：完整产品链路（电源/主控/输出/人机/结构/测试）\n"
     "• 每个设计决策都写清「为什么」与「代价」\n"
     "• 完整踩坑实录：屏四轮点亮、ADC 三段排查、PWM 五次迭代\n"
     "• 稳定复现：BOM ≈ ¥45、3D 打印、驱动可 pin-to-pin 替换\n"
     "• 教师可直接当课程包（含课时、检查点、评分建议）", col=NAVY, bsize=11)

# ══════════════ 14 训练效果量化对照
s = slide(); head(s, "创客训练的效果", "训练前 vs 训练后：能力对照表", "如果说训练有效，就应该能指出「哪一项能力从多少变成了多少」")
table(s, 0.62, 1.6, 12.1, [
    ["能力维度", "训练前（入学/中期）", "训练后（结题）", "可核验证据"],
    ["用户研究", "凭感觉判断需求", "126 份问卷 + 60 人实景观察 + 动作计数", "问卷后台导出、观察记录表"],
    ["数据决策", "看「会买」的态度数据", "用行为口径（1 元意向金 37.3%）驱动决策", "意向金收款记录（22/59）"],
    ["商业建模", "以为算清 BOM 就算清账", "单位经济 + 保本模型（400 → 2,886 台修正）", "表 1-3 成本与定价模型"],
    ["渠道判断", "相信「传播性强」", "先算 CAC 再投钱（¥8.6 / ¥11.5 / ¥31.8）", "渠道 CAC 表（E-04）"],
    ["工程攻坚", "依赖教程与模板代码", "定位屏厂家序列、BGR 反推、8kHz 调优", "开发踩坑实录（8 大类）"],
    ["表达与交付", "写「完成任务」式总结", "评审反馈 9 处修订，4 处主动归因", "评审反馈清单（P0–P3）"],
], fsize=11, hrow=0.6, widths=[1.7, 3.0, 4.2, 3.2])
tx(s, 0.62, 6.4, 12.1, 0.6, "注：上表每一项都能落到具体记录编号；教师可现场抽查任意一行。", size=11, color=GRAY)

# ══════════════ 15 给老师的三条
s = slide(); head(s, "对老师说的话", "我们希望这个项目对课程产生三个作用", "除了「做出一台灯」，它还能继续产生价值")
card(s, 0.62, 1.6, 3.95, 4.3, "① 当一个可用的教学案例",
     "做什么：把这套「洞察 → 假设 → 验证 → 迭代」\n流程和踩坑实录直接搬进课堂。\n\n"
     "为什么有用：\n"
     "• 案例是真实数据，不是虚构练习题\n"
     "• 每个坑都有「现象 → 根因 → 解决」\n"
     "• 学生能看到「算错又改对」的全过程\n\n"
     "我们提供：9 模块讲义、检查点、评分建议", col=TEAL, bsize=11)
card(s, 4.72, 1.6, 3.95, 4.3, "② 当一个可延续的共建项目",
     "做什么：让下一届学生在现有基础上继续做，\n而不是从零开始。\n\n"
     "为什么有用：\n"
     "• 硬件/固件/结构/文档全部开源（MIT）\n"
     "• 有 14 项量化验收判据，成果可比较\n"
     "• 改进可以像代码一样提交（PR 机制）\n\n"
     "我们承诺：维护仓库、评审外部提交、\n把新踩的坑继续写进文档", col=NAVY, bsize=11)
card(s, 8.82, 1.6, 3.9, 4.3, "③ 当一个可核验的训练样本",
     "做什么：用它的数据回答「创客训练到底有没有效」。\n\n"
     "为什么有用：\n"
     "• 中期 → 结题的 4 组指标变化\n"
     "• 能力等级按证据评定（L3/L4）\n"
     "• 主动纠错 9 处（修正率 44%）\n"
     "• 成果可被第三方复现验证\n\n"
     "态度：我们愿意把「不完美」也一起展示", col=GOLD, bsize=11)

# ══════════════ 16 结尾
s = slide()
rect(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=MSO_SHAPE.RECTANGLE)
rect(s, 0, 7.38, 13.333, 0.12, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.1, 2.0, 11.2, 1.3, "一套能被复制的方法，\n比一台能亮的灯更重要", size=34, bold=True, color=WHITE, align=PP_ALIGN.CENTER, line=1.3)
rect(s, 5.55, 3.7, 2.2, 0.045, fill=TEAL, shape=MSO_SHAPE.RECTANGLE)
tx(s, 1.4, 4.05, 10.5, 1.6,
   "312 条验证数据 · 37.3% 行为支付率 · ¥8.6 地推获客 · 22 台 B 端首单 · 9 模块开源课程\n"
   "以及一份把错误也写进去的完整记录",
   size=14.5, color=C(205, 216, 232), align=PP_ALIGN.CENTER, line=1.6)
tx(s, 1.1, 5.9, 11.2, 0.9, "仿真跑不队 · 邵子中 / 李昊桐 / 姜亚楷　|　敬请老师们指正",
   size=12.5, color=C(150, 165, 190), align=PP_ALIGN.CENTER)

prs.save(FNAME)
print("PPT V3.0 saved:", FNAME)
print("页数:", len(prs.slides._sldIdLst))
