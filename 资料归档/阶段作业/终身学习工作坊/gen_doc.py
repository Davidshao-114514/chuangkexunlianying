# -*- coding: utf-8 -*-
"""生成《“终身学习工作坊”单元的初级认知任务》解答文档（任务1–3）"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data3 as D

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREYT = RGBColor(0x66, 0x6E, 0x7A)
TEALC = RGBColor(0x1E, 0x7A, 0x72)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.12
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.8); sec.top_margin = sec.bottom_margin = Cm(1.8)


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


def h3(t):
    return para(t, size=11, bold=True, sb=7, sa=4, color=TEALC)


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
            for k, seg in enumerate(str(v).split("\n")):
                p = c.paragraphs[0] if k == 0 else c.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                R(p, seg, size=fsize)
            if row_fills and row_fills.get(i - 1): shade(c, row_fills[i - 1])
    for j, w in enumerate(widths):
        for i in range(len(rows) + 1):
            t.cell(i, j).width = Cm(w)
    para("", size=5, sa=2)
    return t


# ---------------- 封面 ----------------
para("华中科技大学《创客训练营》课程", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para("“终身学习工作坊”单元的初级认知任务", size=21, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=4)
para("解答文档（任务 1 ~ 任务 3）", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=10, color=NAVY)
para(f"姓名：{D.STUDENT}　　学号：{D.SID}　　团队：{D.TEAM_FULL}", size=10)
para(f"提交日期：{D.DATE}　　作品：{D.PROJ}（{D.SLOGAN}）", size=10)
cap("本学前成果包清单")
table(["序号", "成果", "对应任务", "提交形式"], [
    ["⑴", "《“终身学习工作坊”单元的初级认知任务》解答文档（本文件）", "任务1 / 任务2 / 任务3⑴⑵", "PDF"],
    ["⑵", "创客竞赛作品海报 · 个体初稿（邵子中）", "任务3⑶", "PDF / 图片（附）"],
    ["⑶", "创客竞赛作品海报 · 团队代表作品", "任务3⑶", "PDF / 图片（附）"],
    ["⑷", "课程测评系统结果截图（雷达图 + 增量图 + AI 评语）", "任务2⑵", "PDF 附件（另传）"],
], [1.4, 9.6, 4.0, 2.6], 9)
para("说明：任务2⑵的雷达图与增量图已在本文件中内嵌（由本人测评结果数据绘制）；测评系统原始截图（含 AI 评语页）作为独立 PDF 附件一并提交。", size=9, color=GREYT)

# ---------------- 任务1 ----------------
doc.add_page_break()
h1("任务 1　终身学习核心概念辨析（10 分）")
h2("⑴ 概念匹配（5 分）")
cap("表 1　四种描述与“终身学习 / 元认知”的匹配")
table(["描述", "匹配终身学习？", "匹配元认知？", "判断依据（一句话）"],
      [list(x) for x in D.CONCEPT], [6.4, 2.2, 2.0, 6.8], 9,
      row_fills={0: "E8F2EA", 2: "E8F2EA"})
para("匹配小结：①②③④ 中，①③ 指向“学习这件事在时间跨度与生活方式上的终身性”，②④ 指向“对认知过程本身的觉察与调控”。"
     "两者的分工可以概括为——终身学习回答“学多久、为什么学”，元认知回答“怎么知道自己学会了”。", size=10)

h2("⑵ 元认知三维结构辨析（5 分）")
cap("表 2　三个场景与元认知三维结构（计划 / 监控 / 评估与调节）")
table(["场景", "维度", "理由"], [list(x) for x in D.META3], [2.2, 2.6, 12.6], 9)
para("三者关系的一句话总结：计划是在行动前“想清楚要做什么”，监控是在行动中“随时知道做到哪、对不对”，"
     "评估与调节是在行动后“判断这套方法值不值得再用”。本课程中我的三次典型经历分别落在三个环节："
     "假设清单与 ICE 优先级（计划）→ 意向金支付率与任务完成率的实时观察（监控）→ 5Why 与 GROW 复盘后更换北极星指标（评估与调节）。", size=10)

# ---------------- 任务2 ----------------
doc.add_page_break()
h1("任务 2　个人终身学习能力发展分析（60 分）")
h2("⑴ 元认知自评量表应用（10 分）")
cap("表 3　元认知自评（1 = 完全不符合，5 = 完全符合）")
table(["陈述", "评分", "依据"], [list(x) for x in D.META_SELF], [7.6, 1.4, 8.4], 9)
para("自评小结：最高的两项是“目标—策略匹配”（5 分）与“方法无效时主动调整”（5 分），因为我在这门课里反复做过这两件事；"
     "最低的是“课外场景中主动运用”（3 分），说明元认知目前仍依赖课程任务驱动，尚未变成自发习惯。", size=10)

h2("⑵ EntreComp 三领域能力发展增量分析与归因（35 分）")
para("数据来源：本人以姓名与学号登录课程测评系统完成前后测问卷，取得三领域 15 项三级指标的雷达图、增量图与 AI 评语。"
     "雷达图与增量图如下（由测评结果数据绘制；系统原图截图作为 PDF 附件提交）。", size=10)
for f, w in [("图A_三领域前后测雷达图.png", 15.2), ("图B_增量图.png", 13.6)]:
    doc.add_picture(os.path.join(OUT, f), width=Cm(w))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap("图 A / 图 B　三领域 15 项三级指标的前后测对比与增量（数据来源：课程测评系统前后测结果）")
para("总体观察：15 项指标全部为正增量，其中 +3 三项（识别机会、资源与调动、体验式学习、财经素养共四项）、+2 六项、+1 五项；"
     "从未出现负增量。增量最小的集中在“道德与可持续思维”“愿景”“计划与管理”三项（各 +1，且仍处于 L3）。", size=10)

h3("第一步　增量观测项的证据追溯（增量 ≥2 级，选取 5 项）")
cap("表 4　增量 ≥2 级指标的触发事件与证据追溯")
table(["增量指标", "等级变化", "触发事件", "事件如何促使能力提升", "证据支撑"],
      [list(x) for x in D.INCREASE], [2.6, 2.0, 4.2, 5.4, 3.2], 8.5)
para("说明：以上 5 项增量全部能对应到课程中的具体节点（选题评审质疑、结题期温升越线、中期资源缺口、MVP 减法决策），"
     "不存在“显示增量但找不到课程经历对应”的指标；因此无需在 AI 评语修正部分对增量真实性提出异议。", size=9.5, color=GREYT)

h3("第二步　增量 ≤1 级且仍在 L3 及以下指标的诊断与建议")
cap("表 5　变化不足项的诊断与后续发展建议")
table(["指标", "当前等级", "不变 / 变化不足原因分析", "后续发展建议"],
      [list(x) for x in D.LOW], [3.0, 3.2, 6.8, 4.4], 8.5)
para("说明：三项均满足“增量 ≤1 且当前等级 ≤L3”；其余增量 ≤1 的指标（如动员他人 L4→L5、创造力以外的高等级项）起始等级已在 L4 以上，按课程说明不纳入本步分析。", size=9.5, color=GREYT)

h3("第三步　AI 评价的分析与修正")
cap("表 6　测评系统 AI 评语（原文摘录）")
table(["编号", "AI 评语原文"], [list(x) for x in D.AI_COMMENT], [2.0, 15.4], 9)
cap("表 7　AI 评语的分析与修正（认同 / 存疑 / 补充与修正）")
table(["环节", "我的分析与修正"], [list(x) for x in D.AI_ANALYSIS], [2.6, 14.8], 9,
      row_fills={0: "E8F2EA", 1: "FDF3DC", 2: "FBE4E2"})
para("小结：三条评语中，一条完全认同（计划与管理）、一条存疑（动员他人的数据覆盖范围）、一条需要修正（创造力应“加广度”与项目实际的“减法策略”相反）。"
     "需要说明的是：存疑并非否定测评，而是指出“系统输入只覆盖课内任务行为”这一测量边界——这也让我意识到，任何评价（包括 AI 与我自己的自评）都要先问“它看到了哪些证据、漏掉了哪些情境”。", size=10)

h2("⑶ 四大关键技能自评（15 分）")
cap("表 8　四大关键技能自评（1–10 分）")
table(["四大关键技能", "当前水平", "课程中的具体事例", "发展建议"],
      [list(x) for x in D.SKILL4], [4.6, 1.8, 6.6, 4.4], 9)

# ---------------- 任务3 ----------------
doc.add_page_break()
h1("任务 3　课程全周期关键事件梳理与创客作品海报设计（30 分）")
h2("⑴ 课程全周期时间轴（8 分）")
cap("表 9　课程全周期时间轴（8 个关键事件）")
table(["时间阶段", "关键事件", "我的角色", "核心影响（一句话）"],
      [list(x) for x in D.TIMELINE], [3.4, 5.6, 3.2, 5.2], 9)

h2("⑵ 关键成功与挫折事件萃取（8 分）")
h3("成功事件：用 1 元意向金识别出 39 个百分点的态度—行为落差")
table(["环节", "内容"], [list(x) for x in D.SUCCESS], [2.4, 15.0], 9.5, row_fills={3: "E8F2EA"})
h3("挫折事件：8 小时工况温升越线（测试条件按“方便”而排）")
table(["环节", "内容"], [list(x) for x in D.SETBACK], [2.4, 15.0], 9.5, row_fills={3: "FBE4E2"})

h2("⑶ 创客竞赛作品海报设计（14 分）")
para("海报共提交两份（均为 A4 电子版，另以 PDF / 图片附件提交）：⑴ 个体初稿（邵子中）；⑵ 团队代表作品——由团队三人互评后选定个体初稿为底稿，"
     "整合修订而成，并作为班级《创客作品海报集》候选。海报七要素对照如下。", size=10)
cap("表 10　海报七要素对照表")
table(["要素", "海报中的呈现"], [
    ["项目名称", "磁吸焊接辅助手电（与结题评审一致）"],
    ["团队信息", "团队名称：1班C组 · 仿真跑不队；口号“一吸即用，指哪照哪”；负责人邵子中，成员李昊桐、姜亚楷，三人角色卡与合影位"],
    ["核心价值主张", "为高校电子类专业学生与 DIY 极客解决狭小焊台“灯照不到、靠不住、要扶灯”的问题：一吸即用、指哪照哪，把每次焊接的 4.2 次“找光”动作变成 0，65 元可得（专业工业灯的 1/5）"],
    ["核心认知收获", "“一个创意是否为真，取决于人们是否愿意为它付出真实成本——态度数据会撒谎，行为数据不会。”"],
    ["关键数据", "意向金支付率 37.3%（22/59 人真实支付，问卷口径 71.3%，落差 34pp）；任务完成率 50% → 78%；8 小时工况温升 49℃（2 台复测、同批极差 3℃）；量产 BOM ¥37.6、保本销量 1,232 台"],
    ["作品呈现", "作品原理示意图（磁吸固定 → 万向悬停 → 无级调光）+ 三代原型演进（V1.0 → V2.0 → V3.0/V4.0）"],
    ["课程归属", "华中科技大学《创客训练营》课程作品"],
], [3.2, 14.2], 9)
doc.add_picture(os.path.join(OUT, "海报_团队代表作品_仿真跑不队.png"), width=Cm(11.4))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap("图 C　团队代表作品（A4 电子版原图见附件的 PNG / PDF；个体初稿同规格另附）")

f = os.path.join(OUT, "《“终身学习工作坊”单元的初级认知任务》解答文档（任务1-3）.docx")
doc.save(f)
print("saved:", f)
