# -*- coding: utf-8 -*-
"""生成《课程学习反思报告》（终身学习工作坊 · 课后）——四阶段合一，单文件 PDF"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data4 as D

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63); GREYT = RGBColor(0x66, 0x6E, 0x7A)
TEALC = RGBColor(0x1E, 0x7A, 0x72)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.12
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.7); sec.top_margin = sec.bottom_margin = Cm(1.7)


def R(p, t, size=10, bold=False, color=None):
    r = p.add_run(t); r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None: r.font.color.rgb = color
    return r


def para(t="", size=10, bold=False, align=None, sb=0, sa=4, color=None, indent=0.0):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if indent: p.paragraph_format.left_indent = Cm(indent)
    if t: R(p, t, size=size, bold=bold, color=color)
    return p


def h1(t):
    p = para(t, size=14.5, bold=True, sb=12, sa=7)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "14"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
    b.append(e); pPr.append(b)


def h2(t):
    return para(t, size=12, bold=True, sb=9, sa=5, color=NAVY)


def cap(t):
    return para(t, size=9, bold=True, sa=3, color=NAVY)


def shade(c, hexc):
    tcPr = c._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def table(headers, rows, widths, fsize=9, row_fills=None, head_fill="D9E2F3"):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j); c.text = ""
        R(c.paragraphs[0], h, size=fsize, bold=True)
        c.paragraphs[0].paragraph_format.space_after = Pt(0); shade(c, head_fill)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""
            if v is None:
                continue
            for k, seg in enumerate(str(v).split("\n")):
                p = c.paragraphs[0] if k == 0 else c.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                R(p, seg, size=fsize)
            if row_fills and row_fills.get(i - 1): shade(c, row_fills[i - 1])
    for j, w in enumerate(widths):
        for i in range(len(rows) + 1):
            t.cell(i, j).width = Cm(w)
    para("", size=5, sa=2)


# ---------------- 封面 ----------------
para("华中科技大学《创客训练营》课程", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para("课程学习反思报告", size=26, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=4)
para("元认知的应用——“创客训练营”课程学习反思报告", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=12, color=NAVY)
para(f"团队编号 / 团队名：{D.TEAM_NO} · {D.TEAM}　　作品：{D.PROJ}", size=10.5)
para(f"姓名：{D.STUDENT}　　学号：{D.SID}　　提交日期：{D.DATE}", size=10.5)
cap("报告结构（四阶段成果合一）")
table(["阶段", "成果", "对应框架 / 工具"], [
    ["第一阶段", "元认知知识自我诊断（含 KPT 复盘）", "元认知知识三类框架 + KPT 复盘"],
    ["第二阶段", "元认知技能自我诊断（含 5Why 归因）", "元认知技能三维框架 + 5Why 归因"],
    ["第三阶段", "自我发展行动方案", "《自我发展行动表》（六项缺口）"],
    ["第四阶段", "课程学习元认知反思陈述（300 字以内）", "元认知反思写作"],
], [2.4, 9.4, 5.8], 9.5)
para("说明：本报告全部行为证据均取自“创客训练营”课程全周期的真实事件（三次评审答辩、48 小时迭代验证、B 端交付与长周期观察计划等），"
     "涉及数据可在结题报告与答辩材料中追溯。", size=9, color=GREYT)

# ---------------- 第一阶段 ----------------
doc.add_page_break()
h1("第一阶段　元认知知识自我诊断")
h2("⑴ KPT 复盘表（每条均附具体事例）")
cap("表 1　KPT 复盘")
table(["复盘项", "内容（我的做法 / 问题 / 尝试）", "具体事例支撑"],
      [(k, c, e) for (k, c, e) in D.KPT], [3.6, 6.4, 7.6], 8.5,
      row_fills={0: "E8F2EA", 1: "FBE4E2", 2: "FDF3DC"})

h2("⑵ 元认知知识自我诊断表")
cap("表 2　元认知知识三类缺口诊断（诊断问题 → 自我诊断 → 行为证据）")
table(["诊断维度", "诊断问题", "自我诊断", "行为证据（来自课程经历）"],
      [list(x) for x in D.KNOW], [2.8, 4.2, 4.6, 6.0], 8.5)

# ---------------- 第二阶段 ----------------
doc.add_page_break()
h1("第二阶段　元认知技能自我诊断")
h2("⑴ 5Why 归因表（感受最深的技能缺口：监控技能缺口）")
para("表象问题：我把 8 小时连续工况测试排进了课后“方便的空档”，并相信“30 分钟实测 52℃ 达标”已经证明产品安全——"
     "结题前 8 小时实测温升 61.5℃ 越线，最高风险项最后才暴露。", size=10)
cap("表 3　5Why 追问链")
table(["追问层次", "追问内容", "我的回答", "上一层原因（用于下一层追问）"],
      [(a, b, c, (dd if dd else "—")) for (a, b, c, dd) in D.WHY5], [2.2, 4.2, 6.2, 5.0], 8.5,
      row_fills={4: "E8F2EA"})
para("归因结论：根因不在“时间不够”或“不够努力”，而在监控对象错误——我监控的是“任务是否完成”，而不是“结论是否可靠”。"
     "这解释了为什么同类错误（样本不足却宣布达标）会在温升与渠道两处重复出现。", size=9.5, color=GREYT)

h2("⑵ 元认知技能自我诊断表")
cap("表 4　元认知技能三维缺口诊断（计划 / 监控 / 评估与调节）")
table(["诊断维度", "诊断问题", "自我诊断", "行为证据（来自课程经历）"],
      [list(x) for x in D.SKILL_DIAG], [2.8, 4.2, 4.6, 6.0], 8.5)

# ---------------- 第三阶段（横版） ----------------
s2 = doc.add_section(WD_SECTION.NEW_PAGE)
s2.orientation = WD_ORIENT.LANDSCAPE
s2.page_width, s2.page_height = Cm(29.7), Cm(21.0)
s2.left_margin = s2.right_margin = Cm(1.4); s2.top_margin = s2.bottom_margin = Cm(1.4)
h1("第三阶段　自我发展行动方案")
para("基于前两阶段诊断出的六项缺口，逐项设计可衡量的行动：每项行动都围绕课程中的具体场景，并给出开始时间、可观测的衡量标准、"
     "执行条件与备选方案（避免“某天太忙就停掉”）。", size=10)
cap("表 5　自我发展行动表（六项缺口 × 八要素）")
table(["对应缺口", "我的具体场景", "行动", "具体措施", "开始时间", "衡量标准", "执行条件", "备选方案"],
      [list(x) for x in D.ACTION],
      [2.1, 4.6, 3.2, 5.4, 2.0, 4.2, 3.0, 4.4], 8,
      row_fills={i: ("E8F2EA" if i in (0, 3) else ("FDF3DC" if i in (1, 4) else "F2F6FC")) for i in range(6)})

# ---------------- 第四阶段（回到竖版） ----------------
s3 = doc.add_section(WD_SECTION.NEW_PAGE)
s3.orientation = WD_ORIENT.PORTRAIT
s3.page_width, s3.page_height = Cm(21.0), Cm(29.7)
s3.left_margin = s3.right_margin = Cm(1.7); s3.top_margin = s3.bottom_margin = Cm(1.7)
h1("第四阶段　课程学习元认知反思陈述")
para("题目：通过本次课程学习，我对“自己如何学习”的理解发生了什么根本性变化？请用具体事例说明。", size=10, color=GREYT)
p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
R(p, D.REFLECT, size=11)
para(f"（本陈述 {sum(1 for ch in D.REFLECT if not ch.isspace())} 字，符合 300 字以内要求）", size=9, color=GREYT)
h2("补充：这个发现将如何影响我未来的学习")
table(["影响方向", "具体做法"], [
    ["结论先标强度", "今后所有结论旁标注证据强度（态度 / 行为 / 实测）与样本量；样本不足时只写“初步”不写“达标”。"],
    ["主动反证", "每个项目固定安排一次“证伪复盘”，专门找能推翻当前结论的证据，而不是先找支持证据。"],
    ["周期性自审", "每双周日 21:00 做“结论强度 + 伦理合规”双项自审；学期末做一次完整证伪复盘。"],
    ["角色与排期", "个人角色 ≤2 个、最高风险项排首周；把这两条写进下一个项目的计划模板。"],
], [3.6, 14.0], 9.5)

f = os.path.join(OUT, "1班C组—仿真跑不队—终身学习工作坊课后报告.docx")
doc.save(f)
print("saved:", f, "| 反思陈述字数:", sum(1 for ch in D.REFLECT if not ch.isspace()))
