# -*- coding: utf-8 -*-
"""生成《创客竞赛资源优化方案书》docx（教学活动一 · “资源”领域的迭代验证）"""
import os
import itertools
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data_res as D

OUT = os.path.dirname(os.path.abspath(__file__))
doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.15
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin = sec.bottom_margin = Cm(2.0)
PW, PH = sec.page_width, sec.page_height
CONTENT_CM = 17.0
TAB = itertools.count(1)


def cn_len(t):
    return sum(1 for ch in t if not ch.isspace())


def run(p, text, size=10.5, bold=False, color=None, italic=False):
    r = p.add_run(text)
    r.font.name = "微软雅黑"
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None:
        r.font.color.rgb = color
    return r


def para(text="", size=10.5, bold=False, align=None, space_before=0, space_after=4, color=None, indent=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if text:
        run(p, text, size=size, bold=bold, color=color)
    return p


def h1(text):
    p = para(text, size=15, bold=True, space_before=10, space_after=8)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "3"); bottom.set(qn("w:color"), "2C5AA0")
    pBdr.append(bottom); pPr.append(pBdr)
    return p


def h2(text):
    return para(text, size=12, bold=True, space_before=8, space_after=5, color=RGBColor(0x1F, 0x3B, 0x63))


def h3(text):
    return para(text, size=11, bold=True, space_before=6, space_after=3, color=RGBColor(0x33, 0x44, 0x55))


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def table(headers, rows, widths_cm=None, fsize=8.5, header_fill="D9E2F3", row_fills=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, htxt in enumerate(headers):
        c = t.cell(0, j); c.text = ""
        run(c.paragraphs[0], htxt, size=fsize, bold=True)
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
        shade(c, header_fill)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""
            run(c.paragraphs[0], str(v), size=fsize)
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            if row_fills and row_fills.get(i - 1):
                shade(c, row_fills[i - 1])
    if widths_cm:
        for j, w in enumerate(widths_cm):
            for i in range(len(rows) + 1):
                t.cell(i, j).width = Cm(w)
    para("", size=6, space_after=2)
    return t


def caption(text, auto=True):
    n = next(TAB) if auto else None
    t = f"表 {n}　{text}" if auto else text
    return para(t, size=9, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=6,
                color=RGBColor(0x33, 0x33, 0x33))


def pic(fname, width_cm=CONTENT_CM, cap=None):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(OUT, fname), width=Cm(width_cm))
    if cap:
        para(cap, size=9, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=6,
             color=RGBColor(0x33, 0x33, 0x33))


def shot_box(text):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "dashed"); e.set(qn("w:sz"), "8")
        e.set(qn("w:space"), "6"); e.set(qn("w:color"), "9AA4B2")
        pBdr.append(e)
    pPr.append(pBdr)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(6)
    run(p, text, size=9, color=RGBColor(0x77, 0x80, 0x8C))


# ============================================================ 封面
para("", space_after=26)
para("华中科技大学未来技术学院 · 创客训练营", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0x55, 0x5F, 0x6E))
para("", space_after=4)
para("创客竞赛资源优化方案书", size=26, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para("“资源”领域的迭代验证——创客竞赛作品的优化与再论证", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
para("课后教学活动一 · 48 小时三阶迭代成果（精益画布 V4.0）", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=22)
table(["项目", "内容"], [
    ["团队编号 / 团队名称", f"{D.TEAM_FULL}"],
    ["团队成员", "邵子中（负责人，U202511546）、李昊桐、姜亚楷"],
    ["迭代对象", f"{D.PROJ}——{D.TOPIC}"],
    ["竞赛主题", D.COMP_TOPIC],
    ["迭代窗口", f"{D.WINDOW}（课后 48 小时，三阶迭代法）"],
    ["方案版本", "精益画布 V3.0 → V4.0（9 处实质性修订）；创新核算仪表盘由“当前值”升级为“基准→调整→当前”三阶段"],
    ["提交形式", "PDF（依课程要求：文件务必以 PDF 格式提交）"],
    ["编制日期", D.BUILD_DATE],
], widths_cm=[4.2, 12.8], fsize=10, header_fill="D9E2F3")
para("", space_after=16)
para("指导教师评阅区域（本页由评审填写）", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0x88, 0x90, 0x9C))
doc.add_page_break()

# ============================================================ 目录
h1("目录")
toc = [
    ("摘要", "本轮迭代的一句话结论、三项最重大改动与两项不足"),
    ("第一部分　问题诊断（课后 0–12 小时）", "1.1 反馈来源与汇总　1.2 五维资源管理模型归类　1.3 P0–P3 优先级分级　1.4 5Why 归因　1.5《关键缺陷清单》　1.6 资源全景与缺口诊断　1.7 归档"),
    ("第二部分　快速迭代（课后 12–36 小时）", "2.1《迭代方案设计表》　2.2 验证方法工具箱映射　2.3 再验证执行（六项）　2.4 过程记录　2.5《迭代验证结果汇总表》　2.6 三可追溯标注　2.7 归档"),
    ("第三部分　整合输出（课后 36–48 小时）", "3.1 创新核算仪表盘更新（基准→调整→当前）　3.2 精益画布 V4.0（9 处修订依据）　3.3 RACI-V 调整方案（3 次角色动态调整）　3.4 资源优化三件套　3.5 后续计划与预算"),
    ("第四部分　个人反思与能力发展", "4.1 个人反思报告（3 份）　4.2 能力等级再评估　4.3 能力发展雷达图与变化说明（≤200 字）"),
    ("附录", "A 提交清单对照表　B 原始记录与截图位清单　C 关键口径说明　D 团队分工与过程留痕"),
]
for a, b in toc:
    p = para("", space_after=3)
    run(p, a + "　", size=10.5, bold=True)
    run(p, b, size=9.5, color=RGBColor(0x55, 0x5F, 0x6E))
doc.add_page_break()

# ============================================================ 摘要
h1("摘要")
para("本轮 48 小时迭代的结论是：【维持选题与商业模式，重配资源结构、把资源账算清】。用户价值不需要推翻，需要重算的是“这些资源用得值不值”——把 336 人时按 ¥25/人时折算后，隐性成本占资源总投入 78.7%，而我们此前所有关于经济性的结论，都建立在只占 21.3% 的现金口径上。", size=10.5)
para("三项最重大的改动：① 资源核算从无到有。336 人时折算出 ¥8,400 人力机会成本，建立“现金 / 人力 / 关系”三层成本台账，含人力保本销量由 1,232 台修正为 1,604 台，资源北极星定为“全成本 / 条有效数据”（¥68.0 → ¥52.3）。② 资源获取从“识别”走到“落地”。4 项缺口按“影响严重性 × 修复成本”重排，G-1（缺少 C 端规模化获客渠道）升为唯一 P0；用一场“基地设备 + 课程场景 + 社团网络”组合式工作坊（现金 ¥120 + 12 人时）拿到 42 人到场、19 人留资、26 条有效反馈和 20 台 B 端意向（¥1,180），组合增值率 3.6 倍、协同系数 2.0。③ 责任结构从固化到动态。RACI-V 新增 3 项资源类任务、完成 3 次角色调整，明确“谁对资源账负责、谁对资源获取负责”，调整后任务按时完成率 91% → 94%。", size=10.5)
para("支撑这些改动的再验证覆盖 3 个 P0 与 5 个 P1 缺陷的全部：工时货币化折算、缺口影响-成本矩阵、组合式获客实验（42 人）、三渠道 CAC 复测、留存与转化的三个时间节点追踪、MVC 成本合规核对（6 项）。本单元阶段资源投入为现金 ¥720 + 40 人时（折价 ¥1,000），其中 62% 投向 G-1 与 G-3 两条 P0 缺口；6 项再验证的单次现金支出 5 项 ≤¥300，仅工作坊一项 ¥360 超限 20%（原因见 2.3 与附录 C）。", size=10.5)
para("必须说明本轮的两项不足：H-004（90 天复购率 ≥20%）因周期不足无法验证，已降级为观测项并改用 B 端批量续订意愿作代理指标；“动力和毅力”的个体等级仍停留在 L4——48 小时内出现三次返工（工作坊首场仅到场 9 人、工时误算重算、RACI 初稿只调任务不调人），说明流程前置检查还没有固化。", size=10.5)
doc.add_page_break()

# ============================================================ 第一部分
h1("第一部分　问题诊断（课后 0–12 小时）")
h2("1.1　反馈来源与汇总")
para("本单元共汇总三类反馈：① 个人在线互评意见——在线协作表格中每位同学给出的“两点肯定 + 一点质疑”书面意见；② 教师在线评审意见——教师对各团队中期 PPT 独立评审时给出的判断与等级校准依据；③ 团队互评记录——在线《“创客竞赛作品中期评审”互评》协作表格中各维度评分与关键词反馈。三类来源共摘录 21 条原始反馈，去重合并后得到 15 条有效缺陷；其中 13 条直接指向资源的量化、获取与核算，说明本单元的评审压力集中在“资源用得值不值”这一个问题上。", size=10.5)
caption("反馈来源汇总与采集方式")
rows = []
for (src, tot, uniq, how, ids), econ in zip(D.FB_SOURCES, D.FB_UNIQUE_SRC):
    rows.append([src, tot, uniq, how, ids])
rows.append(["合计", D.FB_TOTAL, D.FB_UNIQUE, "—", "R-01 ~ R-11 / T-01 ~ T-06 / P-01 ~ P-04"])
table(["反馈来源", "原始条目", "归并为缺陷", "采集方式", "条目编号"], rows,
      widths_cm=[3.4, 1.7, 1.8, 7.1, 3.0], fsize=8.5, row_fills={3: "E8F1EA"})
para("归类依据：本单元的归类维度采用五维资源管理模型（识别 — 评估 — 获取 — 增值 — 核算），与前序单元“想法与机会”的五项能力维度区分开，因为本轮被追问的正是“资源”这一领域的完整链条。", size=10)

h2("1.2　五维资源管理模型归类")
para("把 15 条缺陷逐条归入五维后，分布并不均匀：增值（5 条）与核算（3 条）合计占一半以上，说明团队在“资源有没有被组合用好”“资源投入有没有算清”这两环最弱；识别与获取合计 4 条，其中 3 条是 P0——不缺“看得见”，缺“算得清、拿得到”。", size=10.5)
caption("五维资源管理模型的归类标准与本轮缺陷分布")
table(["归类维度", "判定标准（本单元口径）", "本轮缺陷", "其中 P0/P1"], [
    [d, desc, str(sum(1 for x in D.DEFECTS if x[3] == d)), str(sum(1 for x in D.DEFECTS if x[3] == d and x[4] in ("P0", "P1")))]
    for (d, desc) in D.DIM_DESC],
    widths_cm=[1.8, 9.2, 2.0, 2.0], fsize=8.5)
pic("图2_缺陷五维与优先级分布.png", 16.4, "图 2　关键缺陷清单：五维资源管理模型归类 × P0–P3 优先级分布")

h2("1.3　优先级分级（P0–P3）")
para("分级原则沿用“影响严重性 × 修复紧迫性”：P0 表示若不修复项目会被一票否决（资源投入方向错误、成本口径不成立），P1 表示显著削弱竞争力（资源-价值无法量化、仪表盘缺轨迹、责任位错配），P2 影响说服力但非致命，P3 是优化建议。本轮 15 条缺陷的分级结果为 P0 三条、P1 五条、P2 五条、P3 两条。", size=10.5)
caption("P0–P3 分级判据与本轮结果")
table(["等级", "判据（本轮语境下的具体含义）", "条数"],
      [[a, b, str(c)] for (a, b, c) in D.PRIORITY_RULE],
      widths_cm=[3.0, 11.4, 1.6], fsize=8.5, row_fills={0: "FBE4E2"})

h2("1.4　5Why 归因分析")
para("针对 P0 与 P1 级问题，团队完成 3 条完整的 5Why 归因链，每条追问 5 层（课程要求至少完成 1 条）。三条链条指向同一个结构性根因：我们把“记录做了什么”当成资源管理，而没有把资源当成需要排序、需要核算、需要有人负责的对象。三条根因分别落到机制（缺量化排序门槛）、责任（缺独立责任位）、度量（台账事后补记）上，因此在第二阶段全部按“流程类修复”设计，而不是改文案。", size=10.5)
for code, title, whys, root in D.FIVEWHY:
    caption(f"5Why 归因链：{code}　{title}")
    table(["层级", "追问与回答"],
          [[f"Why {i}", w.split(" → ")[1] if " → " in w else w] for i, w in enumerate(whys, 1)] +
          [["根因", root]],
          widths_cm=[1.6, 15.4], fsize=8.5, row_fills={5: "E8F1EA"})

h2("1.5　《关键缺陷清单》")
para("清单含问题编号、反馈来源、问题描述、归类维度、优先级、5Why 根因（仅 P0/P1 填写）与责任成员七列，共 15 条。责任成员的分配规则是：谁的资源职责最相关谁负责，而不是“谁有空谁做”——这一条也是在回应互评意见里“责任看不出变化”的质疑。", size=10.5)
caption("《关键缺陷清单》（含 P0–P3 分级、归类维度与 5Why 归因）")
rows = []
for code, src, desc, dim, prio, root, owner in D.DEFECTS:
    rows.append([code, src, desc, dim, prio, root, owner])
fills = {i: "FBE4E2" for i, x in enumerate(D.DEFECTS) if x[4] == "P0"}
table(["编号", "反馈来源", "问题描述", "归类维度", "优先级", "5Why 根因（仅 P0/P1）", "责任成员"], rows,
      widths_cm=[1.1, 2.4, 5.4, 1.2, 1.0, 4.5, 1.4], fsize=7, row_fills=fills)

h2("1.6　资源全景与缺口诊断（五维视角）")
para("资源全景不再只列“投入了多少”，而是每一类资源都给出“投入 → 产出 → 效率”三栏，并标注它属于五维中的哪一环。这张表也是资源北极星的数据来源。", size=10.5)
caption("资源全景与效率对照表（中期阶段累计，货币化后）")
table(["资源类别", "累计投入", "折合经济口径", "产出证据", "效率指标", "五维归属"],
      [[a, b, c, d, e, f] for (a, b, c, d, e, f) in D.RESOURCE_PANORAMA],
      widths_cm=[1.7, 4.0, 2.4, 4.0, 3.2, 1.7], fsize=7.5, row_fills={1: "F3F6FB"})
para(f"资源台账的三层结构：现金支出 ¥{D.CASH_SPENT:,}（21.3%）、人力机会成本 ¥{D.LABOR_COST:,.0f}（78.7%，{D.LABOR_HOURS} 人时 × ¥{D.LABOR_RATE:.0f}）、外部关系资源（0 现金，等值约 ¥1,700）。资源总投入 ¥{D.TOTAL_RESOURCE_COST:,.0f}，对应 {D.OUTPUT['data']} 条有效验证数据，全成本 ¥{D.COST_PER_DATA:.1f} / 条——这个数字在中期末尾是“答不上来”的那一个，也是本轮的起点。", size=10.5)
caption("资源缺口诊断与影响评估（成本-效益预评估矩阵）")
rows = []
for (name, typ, sev, imp, cost, avail, dim, act) in D.GAPS:
    rows.append([name, typ, f"{sev}/5", imp, cost, avail, act])
table(["资源缺口", "类型", "影响严重性", "影响说明（若不解）", "修复成本", "可获取性", "处理动作"], rows,
      widths_cm=[2.5, 1.4, 1.3, 4.2, 2.0, 2.0, 3.6], fsize=7.5, row_fills={0: "FBE4E2"})
pic("图4_资源缺口四象限.png", 16.4, "图 4　资源缺口影响-修复成本四象限（P0 优先级重排依据）")
para("重排结果与修订说明：G-1 的修复成本按“现金 ¥120 + 12 人时（折价 ¥300）”计为 ¥420，是所有缺口里唯一“高影响 + 低成本 + 高可获取性”的组合，因此从原来的“并列高优先级”升为唯一 P0；G-2（开模资金 ¥3,000）影响分 4/5 但成本过高，处理方式不是立刻投入而是设“投模决策门槛”（确认 B 端订单 ≥20 台或意向金 ≥¥500 才投）；G-3（缺财务经验）现金成本为 0、只需 40 人时学习投入，立即可做；G-4（缺长期使用数据）影响分仅 2/5，降级为观测项，不占用本阶段资源。", size=10.5)

h2("1.7　第一阶段归档")
para("产出物：《评审反馈汇总表》（表 1）、《关键缺陷清单》（表 7，含 P0–P3 分级、五维归类与 3 条完整 5Why）、《资源缺口影响评估表》（表 9）与四象限图（图 4）。留痕位置：飞书文档《48h 资源迭代 · 仿真跑不队》之“诊断”页，含三人独立打分表与分歧项复盘记录。", size=10.5)
doc.add_page_break()
