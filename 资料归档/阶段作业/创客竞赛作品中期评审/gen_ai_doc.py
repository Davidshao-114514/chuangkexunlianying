# -*- coding: utf-8 -*-
"""生成《任务4 AI 辅助中期评价与团队分析记录》docx（含截图位）"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data as D

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREYT = RGBColor(0x66, 0x6E, 0x7A)
RED = RGBColor(0xA0, 0x2D, 0x24)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.15
s = doc.sections[0]
s.page_width, s.page_height = Cm(21.0), Cm(29.7)
s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(2.0)


def R(p, t, size=10.5, bold=False, color=None):
    r = p.add_run(t); r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None: r.font.color.rgb = color
    return r


def para(t="", size=10.5, bold=False, align=None, sb=0, sa=4, color=None, indent=None):
    p = doc.add_paragraph()
    if align: p.alignment = align
    if indent: p.paragraph_format.left_indent = Cm(indent)
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if t: R(p, t, size=size, bold=bold, color=color)
    return p


def h1(t):
    p = para(t, size=15, bold=True, sb=10, sa=8)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
    b.append(e); pPr.append(b)


def shade(c, hexc):
    tcPr = c._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def table(headers, rows, widths, fsize=8.5, row_fills=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j); c.text = ""
        R(c.paragraphs[0], h, size=fsize, bold=True)
        c.paragraphs[0].paragraph_format.space_after = Pt(0); shade(c, "D9E2F3")
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""
            for k, seg in enumerate(str(v).split("\n")):
                p = c.paragraphs[0] if k == 0 else c.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                R(p, seg, size=fsize)
            if row_fills and row_fills.get(i - 1): shade(c, row_fills[i - 1])
    for j, w in enumerate(widths):
        for i in range(len(rows) + 1):
            t.cell(i, j).width = Cm(w)
    para("", size=6, sa=2)


def shot(text):
    p = doc.add_paragraph(); pPr = p._p.get_or_add_pPr(); pBdr = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "dashed"); e.set(qn("w:sz"), "8"); e.set(qn("w:space"), "6"); e.set(qn("w:color"), "9AA4B2")
        pBdr.append(e)
    pPr.append(pBdr); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(6)
    R(p, text, size=9, color=GREYT)


para("", sa=16)
para("创客训练营 · 创客竞赛作品中期评审单元", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para("任务 4：AI 辅助中期评价与团队分析记录", size=19, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=16)
table(["项目", "内容"], [
    ["团队", D.TEAM_FULL],
    ["评价对象", "《仿真跑不队_磁吸焊接手电_中期汇报PPT_V1.0》（PDF 版，完整文件已上传）"],
    ["AI 工具名称", D.AI_TOOL],
    ["提问日期", D.AI_DATE],
    ["叙事前提告知", "已告知 AI：本 PPT 围绕三重叙事问题——① 项目进展是否符合预期？② 资源投入产生了什么价值？③ 团队在困难面前如何坚持与协作？"],
], [3.4, 13.6], fsize=10)
para("记录留存说明：AI 对话窗口截图（提示词 + PPT V1.0 上传记录 + AI 返回全文）已按任务要求留存，"
     "编号 A-1 / A-2，随本记录一并归档；如需核验可索取原图（含工具名称与提问日期的完整界面）。",
     size=9, color=GREYT)

h1("一、提示词（完整原文）")
p = para(D.AI_PROMPT, size=10)
p.paragraph_format.left_indent = Cm(0.6)
para("前置输入方式：PPT V1.0 的完整文件（PDF）已直接上传至 AI 对话窗口，未做删减，AI 对全文含附录数据索引可见。不使用工具文件上传功能时，须在提示词中说明“因工具限制，以下为 PPT 文字摘要”。",
     size=9.5, color=GREYT)

h1("二、AI 评价摘要（7 条，覆盖“资源”领域全部 5 项能力）")
table(["#", "能力项", "AI 评价原文摘要"], [[str(i + 1), x[0], x[1]] for i, x in enumerate(D.AI_POINTS)],
      [0.8, 2.4, 13.8], fsize=8.5)
para(D.AI_SUMMARY_NOTE, size=9.5, color=GREYT)

h1("三、团队分析与回应（3 条代表性观点 · 逐条标注能力项）")
for title, ability, parts in D.AI_RESPONSES:
    para(f"观点：{title}", size=11, bold=True, sb=6, sa=3, color=NAVY)
    para(f"对应 EntreComp 能力项：{ability}　|　AI 原文见上表", size=9.5, color=GREYT, sa=4)
    for seg in parts:
        p = para(seg, size=10, indent=0.4)

h1("四、批判性吸收说明与整体判断")
table(["处理方式", "条数", "对应观点"], [
    ["完全认同并已执行", "3", "观点 ①③（财经素养、动员他人）+ 观点 ⑦（跨维度口径统一）"],
    ["部分认同并已执行", "2", "观点 ②（投模决策门槛）、观点 ④（返工工时构成）"],
    ["建立应对计划", "1", "观点 ⑥（群体一致性偏差：自评改为“先独立填写 → 再比对 → 差异须书面解释”，本次自评已按此执行）"],
    ["有理据存疑", "1", "观点 ③（资源缺口清单是否必须覆盖全部威胁）"],
], [3.4, 1.6, 12.0], fsize=9)
para("我们对 AI 的整体判断：AI 最有价值的两处是“每份行为数据成本 ¥53、其中 20 份还是 1 元可退”与“68% 没有口径”——这两条都是我们自己看得见、"
     "但因为熟悉而忽略的问题。而它在“威胁必须全部转成动作”这一点上越界了：它不知道中期阶段只有 12 天可用、资源边界在哪，"
     "把“完整项目周期”的期待套在一个阶段汇报上。这正是我们把 AI 定位为“外部视角的镜子”而非“裁判”的原因。", size=10)

h1("五、用于 PPT V2.0 的修改点溯源（6 处，要求 ≥3 处）")
table(["#", "修改点（页面 → 内容）", "触发来源（AI 观点）"], [[str(i + 1), c[0] + " → " + c[2], c[3]] for i, c in enumerate(D.V2_CHANGES)],
      [0.8, 12.4, 3.8], fsize=8.5)
para("以上 6 处修改均已写入 PPT V2.0 对应页（标题角标【V2 修改①~⑥】），并在演讲者备注中标注对应 AI 观点来源。", size=9.5, color=GREYT)
para("", sa=6)
para("— 记录结束 —", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

f = os.path.join(OUT, "仿真跑不队_任务4_AI评价与团队分析记录.docx")
doc.save(f)
print("saved:", f)
