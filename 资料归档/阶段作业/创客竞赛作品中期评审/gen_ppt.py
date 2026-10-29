# -*- coding: utf-8 -*-
"""生成中期汇报 PPT V1.0 / V2.0（python-pptx）"""
import os, copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import data as D

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREEN = RGBColor(0x22, 0x7F, 0x57)
YELLOW = RGBColor(0xC8, 0x8A, 0x10)
RED = RGBColor(0xC0, 0x39, 0x2F)
GREY = RGBColor(0x6B, 0x74, 0x84)
LIGHT = RGBColor(0xF4, 0xF6, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x24, 0x29, 0x33)
FONT = "微软雅黑"
SW, SH = 13.333, 7.5


def setrun(r, text, size=14, bold=False, color=DARK, font=FONT):
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    # 中文字体
    from pptx.oxml.ns import qn
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {}); rPr.append(ea)
    ea.set("typeface", font)


def tb(slide, x, y, w, h, text, size=14, bold=False, color=DARK, align=PP_ALIGN.LEFT,
       wrap=True, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        setrun(p.add_run(), ln, size=size, bold=bold, color=color)
    return box


def rect(slide, x, y, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line; sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    sh.adjustments[0] = 0.06
    sh.shadow.inherit = False
    return sh


class Deck:
    def __init__(self, v2=False):
        self.v2 = v2
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW)
        self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    # ---------- 基础版式 ----------
    def page(self, kicker, title, sub=None, tag=None):
        s = self.prs.slides.add_slide(self.blank)
        self.n += 1
        rect(s, 0, 0, SW, 0.16, NAVY)
        tb(s, 0.55, 0.34, 9.6, 0.5, title, size=25, bold=True, color=NAVY)
        if kicker:
            tb(s, 0.55, 0.90, 8.6, 0.32,
               f"EntreComp 映射：{kicker}" if not kicker.startswith("—") else kicker,
               size=11.5, bold=True, color=GREEN)
        if sub:
            tb(s, 0.55, 1.22 if kicker else 0.92, 12.2, 0.36, sub, size=11.5, color=GREY)
        if tag:
            rect(s, 11.05, 0.34, 1.72, 0.4, YELLOW)
            tb(s, 11.05, 0.415, 1.72, 0.3, tag, size=10.5, bold=True,
               color=WHITE, align=PP_ALIGN.CENTER)
        # 页脚
        tb(s, 0.55, 7.09, 8.0, 0.26, f"{D.TEAM} · {D.PROJ} · 中期汇报", size=9, color=GREY)
        tb(s, 11.6, 7.09, 1.2, 0.26, f"{self.n}", size=10, bold=True, color=NAVY, align=PP_ALIGN.RIGHT)
        return s

    def table(self, s, x, y, w, headers, rows, colw, fsize=11, rowh=0.36, headh=0.42,
              row_fills=None, head_fill=NAVY):
        nr, nc = len(rows) + 1, len(headers)
        shp = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(headh + rowh * len(rows)))
        t = shp.table
        t.first_row = True
        total = sum(colw)
        for j, cw in enumerate(colw):
            t.columns[j].width = Emu(int(Inches(w) * cw / total))
        t.rows[0].height = Inches(headh)
        for i in range(len(rows)):
            t.rows[i + 1].height = Inches(rowh)
        for j, h in enumerate(headers):
            c = t.cell(0, j)
            c.fill.solid(); c.fill.fore_color.rgb = head_fill
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.02)
            tf = c.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            setrun(p.add_run(), h, size=fsize, bold=True, color=WHITE)
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                c = t.cell(i + 1, j)
                fill = LIGHT if i % 2 == 0 else WHITE
                if row_fills and row_fills.get(i):
                    fill = row_fills[i]
                c.fill.solid(); c.fill.fore_color.rgb = fill
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.margin_left = c.margin_right = Inches(0.06)
                c.margin_top = c.margin_bottom = Inches(0.02)
                tf = c.text_frame; tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT if j != 0 or len(str(v)) > 12 else PP_ALIGN.CENTER
                setrun(p.add_run(), str(v), size=fsize, color=DARK)
        return t

    def img(self, s, path, x, y, w=None, h=None):
        kw = {}
        if w: kw["width"] = Inches(w)
        if h: kw["height"] = Inches(h)
        return s.shapes.add_picture(os.path.join(OUT, path), Inches(x), Inches(y), **kw)

    def note(self, s, lines):
        s.notes_slide.notes_text_frame.text = "\n".join(lines)

    def bullets(self, s, x, y, w, items, size=12.5, gap=0.06, dot="●"):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(5.4))
        tf = box.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
        first = True
        for it in items:
            if isinstance(it, tuple):
                txt, lvl = it
            else:
                txt, lvl = it, 0
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.line_spacing = 1.18
            p.space_after = Pt(int(gap * 72))
            if lvl == 0:
                p.alignment = PP_ALIGN.LEFT
                setrun(p.add_run(), f"{dot} ", size=size * 0.8, bold=True, color=GREEN)
                setrun(p.add_run(), txt, size=size, color=DARK)
            else:
                p.level = 1
                setrun(p.add_run(), txt, size=size - 1.2, color=GREY)
        return box

    # ---------- 各页 ----------
    def build(self):
        v2 = self.v2
        # P1 封面
        s = self.prs.slides.add_slide(self.blank); self.n = 1
        rect(s, 0, 0, SW, SH, NAVY)
        rect(s, 0, 3.02, SW, 0.06, GREEN)
        tb(s, 1.0, 1.62, 11.3, 0.5, "创客竞赛作品中期汇报", size=38, bold=True, color=WHITE)
        tb(s, 1.0, 2.28, 11.3, 0.5, f"{D.PROJ} —— {D.TOPIC}", size=19, color=RGBColor(0xC9, 0xD6, 0xE6))
        tb(s, 1.0, 3.4, 11.3, 1.5,
           f"团队名称：{D.TEAM_FULL}\n团队成员：{D.MEMBERS}\n汇报日期：{D.MID_DATE}　|　"
           f"版本：中期汇报 PPT {'V2.0（AI 迭代后终稿）' if v2 else 'V1.0（课前提交）'}",
           size=15, color=WHITE, spacing=1.5)
        tb(s, 1.0, 5.5, 11.3, 0.9,
           "本汇报以欧盟《创业能力框架》“资源”领域五项能力为叙事线索：\n"
           "① 项目进展是否符合预期　② 资源投入产生了什么价值　③ 团队在困难面前如何坚持与协作",
           size=13, color=RGBColor(0x9F, 0xB4, 0xCE), spacing=1.35)

        # P2 资源全景页 A
        tag = "【V2 修改①】" if v2 else None
        s = self.page("资源与调动", "资源全景页（一）：投入了什么，产出了什么",
                      "资源投入-成果对照总表：回答“做得值不值”", tag)
        rows = []
        for a, b, c in D.TOTAL_TABLE:
            rows.append([a, b, c])
        if v2:
            rows[0][2] = "每 2.1 人时 = 1 条验证数据（其中付费行为 1.9 份 / 每 ¥100）"
            rows[1][2] = "每 ¥53 = 1 份付费行为数据（含 20 份 1 元意向金）"
        self.table(s, 0.55, 1.72, 12.2, ["我们投入了", "我们获得了", "效率说明"], rows,
                   colw=[4.3, 4.4, 3.5], fsize=12, rowh=0.62, headh=0.44)
        y = 4.18
        rows2 = [["时间", f"{D.HOURS_TOTAL} 人时（邵 120 / 李 110 / 姜 106）", "有效验证数据 157 条 · 原型 3 版 · 代码提交 23 次", "0.47 条 / 人时"],
                 ["资金", f"¥{D.MONEY_TOTAL}（打样 / 机构件 / 验证）", "付费行为数据 43 份 · 问卷回收 87 份", "¥53 / 份"],
                 ["外部资源", "导师 2 次 · 实验室 3 次 · 专利检索 1 次", "11 条改进建议 · 1 项 B 端意向（20 台）", "每次 = 2.2 项"]]
        if v2:
            rows2.append(["分渠道\n单客经济", "地推 CAC ¥8.6（LTV/CAC 3.07）", "线上投放 CAC ¥31.8（LTV/CAC 0.83）", "线上渠道不可持续，已停投"])
        self.table(s, 0.55, y, 12.2, ["资源类型", "投入（中期阶段）", "产出", "转化效率"], rows2,
                   colw=[1.7, 4.4, 4.4, 1.7], fsize=10.5, rowh=0.56, headh=0.4)
        self.note(s, ["数据来源：工时台账 + 采购记录 + 验证原始记录（附录页索引）"] +
                  (["【V2 修改①｜对应 AI 观点①】效率口径由单一“每 ¥100 = 3.7 份反馈”拆为含付费行为的双口径，并新增分渠道单客经济一行。"] if v2 else []))

        # P3 资源全景页 B
        tag = "【V2 修改②】" if v2 else None
        s = self.page("资源与调动 + 计划与管理", "资源全景页（二）：里程碑进度总览",
                      "回答“做得快不快”——计划执行情况与三色状态", tag)
        rows = []
        for name, due, pct, status in D.PROGRESS:
            color = "完成" if pct == 100 else "进行中"
            rows.append([name.split("：")[0], name.split("：")[1], due, f"{pct}%", status])
        self.table(s, 0.55, 1.72, 12.2, ["里程碑", "内容", "计划完成", "完成度", "状态"], rows,
                   colw=[1.2, 6.4, 1.6, 1.3, 1.5], fsize=11, rowh=0.6, headh=0.42,
                   row_fills={0: RGBColor(0xE6, 0xF2, 0xEA)})
        self.img(s, "图B_资源效率与进度.png", 1.35, 4.05, w=10.6)
        txt = "目标完成度口径：按 3 个里程碑计划权重加权（M1 40% / M2 35% / M3 25%），68% = 100%×40% + 62%×35% + 25%×25%" if v2 \
            else "目标完成度 68%（进度条可视化见下）"
        rect(s, 0.55, 6.55, 12.2, 0.42, LIGHT)
        tb(s, 0.7, 6.62, 11.9, 0.3, ("【注释】" if v2 else "") + txt, size=11, bold=v2, color=DARK if v2 else GREY)
        self.note(s, ["里程碑三色：绿=已完成/超前，黄=进行中/部分达成，红=滞后/未达预期"] +
                  (["【V2 修改②｜对应 AI 观点⑦】补充 68% 的加权口径与算式，消除三个数字口径不一致。"] if v2 else []))

        # P4 价值主张页 A
        s = self.page("自我意识与自我效能感", "价值主张页（一）：一句话说清 + 算清经济账",
                      "核心主张公式与量化经济账")
        v = D.UVP_VALUE
        rect(s, 0.55, 1.72, 12.2, 1.5, LIGHT)
        tb(s, 0.8, 1.86, 11.7, 1.3,
           f"【{v['user']}】通过【{v['solution']}】实现【{v['benefit']}】，"
           f"{v['vs']}，我们【{v['diff']}】。", size=15, bold=True, color=NAVY, spacing=1.35)
        rows = [
            ["用户侧收益（可量化）", "单次焊接减少 4.2 次“找光”动作；沉浸式实测焊接失败率 50% → 20%；单用户年化可货币化效益 ¥144.5（SROI ≈ 2.2 : 1）"],
            ["团队侧收益（算账逻辑）", f"标准版 65 元：量产后单位贡献 ¥22.0（33.8%）；B 端实训套装 59 元/台（10 台起、零获客成本）；加权单位贡献 ¥18.67"],
            ["回本门槛", "保本销量：小批定价 2,886 台 / 量产定价 1,232 台（含人力机会成本 2,196 台）；3 年 SOM 预期 3,100 台 → 可行，安全边际 1.4 倍"],
            ["与竞品对比", "价格约为专业工业灯 1/4；照度 780 lux（专业灯 1100、台灯 420）；光斑直径 6cm 为四款最小；瞄准自由度与空间占用唯一满分"],
        ]
        self.table(s, 0.55, 3.45, 12.2, ["维度", "量化说明"], rows,
                   colw=[2.6, 9.6], fsize=11.5, rowh=0.72, headh=0.4)
        self.note(s, ["对比基准：选题评审阶段精益画布 V3.0（2026-09-26）；经济账口径见《选题优化方案书》表 7–表 9"])

        # P5 价值主张页 B
        s = self.page("资源与调动 + 财经素养", "价值主张页（二）：验证矩阵（竞品盲测雷达图）",
                      "清晰性 / 竞争力 / 可行性 三维验证")
        self.table(s, 0.55, 1.70, 6.0, ["维度", "验证结果"], [
            ["清晰性", "电梯演讲三句话互测：请 2 位非团队成员复述“为谁解决什么”，2/2 准确复述；每句 ≤10 秒（实际 7–9 秒）"],
            ["竞争力", f"盲测 N={D.BLIND_N}，5 维度 1–5 分：功能覆盖 4.0 vs 台灯 2.4 / 便携灯 1.9；用户体验 4.5 vs 2.6 / 2.2；价格 4.3 vs 专业灯 2.1（≥3 个维度高出 ≥1 分）"],
            ["可行性", "10 位目标用户完成核心任务：状态查询 4.2 秒（≤5 秒达标）、吸附 3.2kg（≥2.5kg 达标）；温升 52℃（黄，8 小时连续工况未测）"],
            ["劣势自陈", "可信度 3.7 分低于专业工业灯 4.5——缺品牌与长期可靠性背书，用“结构实测数据 + 30 天无理由退换”部分对冲"],
        ], colw=[1.3, 4.7], fsize=10.5, rowh=0.9, headh=0.4)
        self.img(s, "图A_盲测雷达图.png", 6.75, 1.66, w=6.0)
        self.note(s, ["盲测方法：不告知品牌，15 位目标用户对 4 款产品在 5 个维度打分（1–5），取均值"])

        # P6 进展总览页 A
        s = self.page("财经素养 + 动力和毅力", "进展总览页（一）：关键假设状态（三色标识）",
                      "与《选题优化方案书》精益画布 V3.0 假设编号一致")
        rows = []
        fills = {}
        for i, (hid, stmt, status, color, ev, risk) in enumerate(D.HYPOTHESES):
            rows.append([hid, stmt, status, ev, risk])
            fills[i] = {"绿": RGBColor(0xE6, 0xF2, 0xEA), "黄": RGBColor(0xFD, 0xF3, 0xDC),
                        "红": RGBColor(0xFB, 0xE4, 0xE2)}[color]
        self.table(s, 0.55, 1.7, 12.2, ["编号", "假设陈述", "状态", "数据支撑 / 进度", "风险应对与下一步"], rows,
                   colw=[1.0, 3.3, 1.4, 3.8, 2.7], fsize=9.5, rowh=0.85, headh=0.4, row_fills=fills)
        rect(s, 0.55, 6.6, 12.2, 0.4, LIGHT)
        tb(s, 0.7, 6.66, 11.9, 0.3,
           "三色标识：绿 = 已验证（附具体数据）　黄 = 验证中/部分成立（附进度与预计完成时间）　红 = 未验证或已证伪（附失效应对）",
           size=10.5, color=GREY)
        self.note(s, ["H-001/H-003 为部分成立（黄）：态度与行为口径需同时呈现", "H-004 未验证：明确写出“周期不足、未执行”，不以“规划中”替代"])

        # P7 进展总览页 B
        tag = "【V2 修改⑥】" if v2 else None
        s = self.page("动力和毅力 + 资源与调动", "进展总览页（二）：“挑战 - 资源 - 突破”三段式", None, tag)
        st = D.STORY
        self.table(s, 0.55, 1.66, 12.2, ["阶段", "内容要求", "证据要求", "本项目事实"], [
            ["挑战", "遇到的核心问题", "原始数据佐证",
             f"{st['challenge']}\n{st['challenge_ev']}"],
            ["资源", "采取的措施与投入的资源（人力 / 技术 / 资金）", "具体数值",
             f"{st['resource']}\n{st['resource_ev']}"],
            ["突破", "改进成效数据", "对比数据（与基线对比）",
             f"{st['break_']}\n{st['break_ev']}"],
        ], colw=[0.9, 3.0, 2.4, 5.9], fsize=10, rowh=1.32, headh=0.4)
        extra = ("返工工时构成（回应“量化坚持”）" if v2 else "成功与失败记录")
        rect(s, 0.55, 6.05, 12.2, 1.0, LIGHT)
        tb(s, 0.75, 6.15, 11.8, 0.85,
           (f"{extra}：72 人时返工中 40 人时用于修正团队自身的设计错误（问卷抽样框不合规 8 人时、"
            "观察记录表指标缺“可计数行为”导致首日作废 24 人时、外壳转轴尺寸返工 8 人时）。"
            "改进机制：新增两道前置检查——配额表预审、观察指标预演；改进后同类返工 0 次。") if v2 else
           f"{extra}：48 小时迭代共有 3 处失败记录（专利检索式一次写错、民族志首日记录表设计错误作废、画布 V3.0 首版模块口径自相矛盾），全部保留在飞书文档修订历史中，未做删除。",
           size=11, color=DARK, spacing=1.3)
        self.note(s, ([f"【V2 修改⑥｜对应 AI 观点④】补入返工工时构成（40 人时/72 人时为修正自身错误）与两道前置检查机制。"] if v2 else []) +
                  ["失败记录不删除：可作为“量化坚持”与迭代透明度的证据"])

        # P8 进展总览页 C
        s = self.page("财经素养 + 动力和毅力", "进展总览页（三）：关键指标仪表盘（红黄绿）",
                      "2–3 个核心量化指标 + 与基线的对比")
        rows = [[n, std, now, {"绿": "绿色 达标", "黄": "黄色 临界", "红": "红色 不达标"}[c], note] for n, std, now, c, note in D.DASHBOARD]
        fills = {i: (RGBColor(0xE6, 0xF2, 0xEA) if r[3].startswith("绿色") else RGBColor(0xFD, 0xF3, 0xDC))
                 for i, r in enumerate(rows)}
        self.table(s, 0.55, 1.7, 12.2, ["核心指标", "三色阈值（绿）", "当前实测", "状态", "说明"], rows,
                   colw=[2.9, 1.9, 1.5, 1.5, 4.4], fsize=10.5, rowh=0.56, headh=0.4, row_fills=fills)
        self.img(s, "图C_基线与中期对比.png", 0.95, 5.05, w=11.4)
        self.note(s, ["阈值来源：MVC 与选题评审阶段设定的成功标准", "黄灯项处理：温升与单位变动成本列入 M2 里程碑，不隐藏"])

        # P9 团队效能页 A
        tag = "【V2 修改③】" if v2 else None
        s = self.page("资源与调动", "团队效能页（一）：SWOT 与资源缺口热力图", "回答“资源在哪里、缺什么”", tag)
        sw = D.SWOT
        self.table(s, 0.55, 1.68, 7.4, ["内/外部", "积极因素", "消极因素"], [
            ["内部", "优势 S：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(sw["S"])),
             "劣势 W：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(sw["W"]))],
            ["外部", "机会 O：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(sw["O"])),
             "威胁 T：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(sw["T"]))],
        ], colw=[0.8, 3.3, 3.3], fsize=9, rowh=2.15, headh=0.38)
        gaps = [[g[0], g[1], {"高": "红色 高", "中": "黄色 中", "低": "绿色 低"}[g[2]], g[3]] for g in D.GAPS]
        if v2:
            gaps.append(["威胁-动作对照：大厂可仿制", "外部合作", "黄色 中", "资源与调动"])
            gaps.append(["威胁-动作对照：认证成本不确定", "外部资金", "黄色 中", "财经素养"])
        self.table(s, 8.15, 1.68, 4.6, ["资源缺口", "缺口类型", "紧急度", "对应能力"], gaps,
                   colw=[2.2, 1.0, 0.9, 1.5], fsize=9, rowh=0.62, headh=0.38)
        tb(s, 8.15, 1.30, 4.6, 0.32, "资源缺口热力图（≥3 项）", size=11.5, bold=True, color=NAVY)
        rect(s, 0.55, 5.98, 12.2, 1.02, LIGHT)
        tb(s, 0.72, 6.05, 3.4, 0.9,
           f"最高优先级缺口\n{D.GAP_TOP['gap']}\n对应能力：{D.GAP_TOP['ability']}",
           size=9.5, bold=True, color=NAVY, spacing=1.25)
        tb(s, 4.25, 6.05, 4.2, 0.9, f"若不解决的影响\n{D.GAP_TOP['impact']}", size=9, color=DARK, spacing=1.2)
        tb(s, 8.6, 6.05, 4.1, 0.9, f"初步解决思路\n{D.GAP_TOP['plan']}", size=9, color=DARK, spacing=1.2)
        self.note(s, ([f"【V2 修改③｜对应 AI 观点②】新增“威胁-动作对照”两行，把 T 象限的威胁转化为可执行动作。"] if v2 else []) +
                  ["威胁中“价格战风险”在千片规模前无法真实应对，列为观察项并标注触发条件（见 V2 团队效能页备注）"])

        # P10 团队效能页 B
        tag = "【V2 修改④】" if v2 else None
        s = self.page("动员他人 + 动力和毅力", "团队效能页（二）：RACI-V 分工、SMART-C 里程碑与协作效能", None, tag)
        self.table(s, 0.55, 1.62, 12.2, ["任务 / 决策", "邵子中", "李昊桐", "姜亚楷", "角色分工说明"],
                   [list(r) for r in D.RACI], colw=[3.4, 1.1, 1.1, 1.1, 3.6], fsize=9.5, rowh=0.46, headh=0.38)
        tb(s, 0.55, 4.62, 5.9, 0.3, "SMART-C 里程碑（下一阶段）", size=11.5, bold=True, color=NAVY)
        self.table(s, 0.55, 4.96, 5.9, ["里程碑", "衡量标准", "时限", "检查点"],
                   [[f"{m[0]}：{m[1][:18]}…", m[2][:22] + "…", m[3], m[4][:16] + "…"] for m in D.MILESTONES],
                   colw=[1.9, 1.9, 0.7, 1.4], fsize=8.5, rowh=0.62, headh=0.34)
        tb(s, 6.75, 4.62, 6.0, 0.3, "协作效能（含统计口径）", size=11.5, bold=True, color=NAVY)
        coop = D.COOP if not v2 else ("统计口径：对象为已进入执行的任务卡 46 张（不含未启动项）；站会校准前两周按时完成 33 张 = 72%，"
                                       "校准后两周 42 张 = 91%（提升 9 张中 6 张为“都以为对方在做”的灰色任务）。"
                                       "响应时间取群内 @ 到首次响应时长的中位数（9 小时 → 3.5 小时）。")
        rect(s, 6.75, 4.96, 6.0, 1.35, LIGHT)
        tb(s, 6.9, 5.06, 5.7, 1.2, coop, size=10.5, color=DARK, spacing=1.3)
        self.note(s, ([f"【V2 修改④｜对应 AI 观点③/⑤】补入效能指标的统计口径与分母（46 张任务卡）。"] if v2 else []) +
                  ["RACI-V 中的 V（志愿者/支持者）：实验室学长提供演示场地与评阅意见；指导老师提供开模与费率报价口径"])

        # P11 财经素养页 A
        s = self.page("财经素养", "财经素养页（一）：成本-收益分析（显性 + 隐性）",
                      "成本口径与方法说明见《选题优化方案书》附录 C")
        rows = [["显性成本", "、".join(f"{c[0]} {c[1]}" for c in D.EXPLICIT_COST[:3]),
                 f"¥{D.MONEY_TOTAL}",
                 "PCBA 打样 2 轮 ¥680；3D 打印耗材 ¥180；机构件 ¥320；迭代验证 ¥940；交通与打印 ¥160"],
                ["隐性成本", "、".join(c[0].split("（")[0] for c in D.IMPLICIT_COST[:3]),
                 f"{D.HOURS_TOTAL} 人时",
                 "例会 60 + 学技术 96 + 返工 72 + 验证执行 48 + 文档 60（按学生兼职 ¥25/人时折 ¥8,400 机会成本）"],
                ["总投入", "现金 + 人力机会成本", f"¥{D.MONEY_TOTAL} + ¥8,400 机会成本", "现金部分不含团队成员的人工支出，人力按机会成本单列"],
                ["收益（验证成果）", "MVP 测试付费意向率 32.3%（1 元意向金行为口径）", "43 份付费行为数据",
                 "预售页下单 23 份 + 意向金 20 份；问卷 87 份；盲测 15 份"],
                ["转化效率", "每 ¥100 获得 3.7 份有效用户反馈", "3.7 份 / ¥100",
                 "其中付费行为数据 1.9 份 / ¥100（V2 口径细化）"]]
        self.table(s, 0.55, 1.7, 12.2, ["成本 / 收益项", "项目", "金额 / 量化", "备注说明"], rows,
                   colw=[1.9, 4.0, 2.4, 4.6], fsize=10, rowh=0.82, headh=0.4)
        self.note(s, ["MVC 原则（单次验证 ≤2 周 / ≤¥300）的遵守情况与例外说明见下一页"])

        # P12 财经素养页 B
        tag = "【V2 修改⑤】" if v2 else None
        s = self.page("财经素养 + 资源与调动", "财经素养页（二）：MVC 遵守说明、决策机制与资金教训", None, tag)
        rows = [["MVC 遵守情况", D.FIN["mvc_ok"]],
                ["单次试错上限", D.FIN["decision"]],
                ["资金使用教训", D.FIN["lesson"]],
                ["下一阶段预算", "、".join(f"{b[0]} {b[1]}" for b in D.NEXT_BUDGET) + f"（合计 ¥{D.BUDGET_TOTAL:,}）"]]
        if v2:
            rows.insert(3, ["投模决策门槛\n（V2 新增）", "确认 B 端订单 ≥20 台（或已收意向金 ≥¥500）方可投模具定金 ¥3,000；未达标则退回 3D 打印路径，"
                                            "BOM 停在 ¥52.3 并接受毛利率 11.2% 的现实——退路提前写明，避免 ¥3,000 成为沉没成本。"])
        self.table(s, 0.55, 1.7, 12.2, ["维度", "内容"], rows, colw=[2.4, 9.8], fsize=11, rowh=1.05, headh=0.4)
        self.note(s, ([f"【V2 修改⑤｜对应 AI 观点②】新增投模决策门槛（确认订单 ≥20 台或意向金 ≥¥500 才投 ¥3,000 模具定金）。"] if v2 else []) +
                  ["MVC 例外说明：单次验证成本 ¥360 略高于 ¥300 上限，原因是行为口径测试需补偿参与者的真实成本（1 元可退意向金），已说明理由"])

        # P13 后期规划页
        s = self.page("计划与管理", "后期规划页：三阶段计划、里程碑与风险预案", f"至结题评审（{D.PERIOD.split('—')[1].strip()}）")
        self.table(s, 0.55, 1.7, 12.2, ["阶段", "时间", "关键任务", "负责人", "风险预案"],
                   [list(p) for p in D.PLAN], colw=[1.0, 1.5, 5.6, 1.6, 2.5], fsize=10.5, rowh=1.05, headh=0.42)
        rect(s, 0.55, 5.44, 12.2, 1.42, LIGHT)
        tb(s, 0.75, 5.52, 11.8, 1.3,
           "资源调配预案（若关键资源不到位）：\n"
           "① 若注塑模具资金未落实 → 退回 3D 打印小批量路径，BOM 停在 ¥52.3，商业目标改为“成本自给（回收打样投入）”，不追求规模毛利；\n"
           "② 若 B 端首单未成 → 把 20 台样品转为“创客空间演示 + 社团借用”渠道，用使用数据换取第二批意向；\n"
           "③ 若 8 小时连续工况温升超标 → 降 10% 驱动电流并加厚铝基板，牺牲约 8% 照度保安全（安全性在评审中占 20% 权重）。",
           size=11, color=DARK, spacing=1.35)
        self.note(s, ["里程碑 M1–M3 与 SMART-C 六要素的对应关系见团队效能页（二）"])

        # P14 Q&A 预判页
        s = self.page("不确定性管理", "Q&A 预判页：3 个最尖锐问题与应对话术", "来源于项目健康度自检识别出的薄弱环节")
        rows = [[f"{i+1}", q, a] for i, (q, a) in enumerate(D.QA)]
        self.table(s, 0.55, 1.7, 12.2, ["序号", "尖锐问题（来源于薄弱环节）", "应对话术（含数据 / 证据）"],
                   rows, colw=[0.7, 3.6, 7.9], fsize=9.5, rowh=1.6, headh=0.4)
        self.note(s, ["创业者三问自检结论：① 关键假设 = H-001 付费意愿（行为口径）；② 最低成本验证 = 1 元可退意向金（¥360 / 48h）；"
                      "③ 数据决策 = 行为口径 32.3% → 下调 C 端预期、转 B 端；若 B 端首单 <10 台则转纯套件版"])

        # V2：AI 评价与团队分析（2 页）
        if v2:
            s = self.page("AI 评价与团队分析", "AI 评价与团队分析（一）：评价摘要（7 条，覆盖 5 项能力）",
                          f"工具：{D.AI_TOOL}　提问日期：{D.AI_DATE}")
            self.table(s, 0.55, 1.62, 12.2, ["#", "能力项", "AI 评价原文摘要"],
                       [[str(i + 1), p[0], p[1]] for i, p in enumerate(D.AI_POINTS)],
                       colw=[0.6, 1.9, 9.7], fsize=9.5, rowh=0.66, headh=0.38)
            tb(s, 0.55, 6.78, 12.2, 0.4, D.AI_SUMMARY_NOTE, size=10, color=GREY)
            self.note(s, ["前置输入：PPT V1.0（PDF）已上传至 AI 对话窗口；提示词原文见附录《AI 评价与团队分析记录》",
                          "截图佐证：任务 4 记录文件（含对话截图）"])

            s = self.page("AI 评价与团队分析", "AI 评价与团队分析（二）：逐条回应（认同 / 已执行 / 存疑）",
                          "每条回应标注对应 EntreComp“资源”领域能力项")
            rows = []
            for title, ability, parts in D.AI_RESPONSES:
                rows.append([title + f"\n（能力项：{ability}）", "\n".join(parts)])
            self.table(s, 0.55, 1.62, 12.2, ["AI 观点", "团队回应（认同 / 已执行 / 存疑）"], rows,
                       colw=[3.0, 9.2], fsize=9.5, rowh=1.62, headh=0.4)
            tb(s, 0.55, 6.72, 12.2, 0.4,
               "处理原则：AI 是“外部视角的镜子”，不是“正确答案”。本页 3 条回应中 1 条含有理据的“存疑”（资源缺口清单是否必须覆盖全部威胁），"
               "并给出保留原方案的辩护理由与观察项处理方式。", size=10, color=GREY)
            self.note(s, ["【V2 修改①~⑥】对应 AI 观点来源见各页标题角标与备注；修改点共 6 处（要求 ≥3 处）"])
        # P15 附录
        s = self.page("—", "附录：数据来源与“三可追溯”索引", "本页不计入正页页数")
        self.table(s, 0.55, 1.7, 12.2, ["数据项", "来源（可查）", "采集时间"],
                   [list(x) for x in D.SOURCES], colw=[3.4, 6.8, 2.0], fsize=10.5, rowh=0.66, headh=0.4)
        tb(s, 0.55, 6.35, 12.2, 0.6,
           "三可追溯：来源可查（文件 / 时间 / 样本量）× 过程可复现（方法 / 配额 / 剔除规则）× 结果可验证（原始记录截图，编号 B-1 ~ B-13）。",
           size=11, bold=True, color=NAVY)

        return self.prs

    def save(self, name):
        path = os.path.join(OUT, name)
        self.prs.save(path)
        print("saved:", path, "slides =", len(self.prs.slides.__iter__.__self__._sldIdLst))
        return path


if __name__ == "__main__":
    d1 = Deck(v2=False); d1.build(); d1.save(f"{D.TEAM}_{D.PROJ}_中期汇报PPT_V1.0.pptx")
    d2 = Deck(v2=True); d2.build(); d2.save(f"{D.TEAM}_{D.PROJ}_中期汇报PPT_V2.0.pptx")
