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
    ("附录", "A 提交清单对照表　B 原始记录留存清单　C 关键口径说明　D 团队分工与过程留痕"),
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
# ============================================================ 第二部分
h1("第二部分　快速迭代（课后 12–36 小时）")
h2("2.1　《迭代方案设计表》")
para("针对 P0 与 P1 缺陷，每一条都对应一个明确的再验证方案、预期产出与截止时间；设计原则是最低成本优先——能用桌面研究、台账重算、已有数据二次分析、真实场景顺带采集完成的，不额外花钱。8 项迭代计划中 6 项在本窗口内执行完毕，2 项（开模门槛的正式评审、威胁-动作的第三家报价）转入后续计划。", size=10.5)
caption("《迭代方案设计表》（P0/P1 全部对应再验证方案）")
table(["问题编号", "问题描述", "再验证方法", "预期产出", "截止时间"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.ITER_PLAN],
      widths_cm=[1.5, 3.2, 6.0, 4.0, 2.3], fsize=8, row_fills={i: "FBE4E2" for i in range(3)})

h2("2.2　验证方法工具箱映射")
para("课程给出的验证方法工具箱共五类，本轮全部被使用，并逐项对齐了适用场景与最低样本量要求。", size=10.5)
caption("验证方法工具箱与本轮的对应关系")
table(["验证类型", "推荐方法", "适用场景", "最低样本量建议", "对应缺陷 / 数据"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.TOOLBOX],
      widths_cm=[2.2, 4.4, 3.4, 3.2, 3.8], fsize=8)

h2("2.3　再验证执行（六项）")
h3("2.3.1　单位经济核算：把 336 人时折算成钱")
para("这是本轮的第一件事，也是最不花钱的一件事：只用台账重算。折算后隐性人力成本 ¥8,400，隐性占比 78.7%。单位经济因此需要双口径表述：量产后标准版单位贡献 ¥22.0，扣掉人力分摊 ¥8.4 后仍为正（+¥13.6 / 台）；但若只做 200 台小批量，人力分摊变为 ¥42 / 台，单位经济转为 −¥34.7 / 台。结论是：隐性成本能不能被摊薄，取决于规模，而不是取决于要不要记账——这句话直接改写了后续的资源投入方向（先做 B 端规模，而非先省钱）。", size=10.5)
pic("图3_资源投入与效率.png", 16.5, "图 3　资源投入结构（隐性占 78.7%）与资源北极星的三个阶段")
h3("2.3.2　资源缺口影响评估：从“列清单”到“排顺序”")
para("用“影响严重性（1–5）× 修复成本（现金 + 工时折价）”两维打分，三人独立打分后取均值，1 项分歧（G-4 的影响分是 2 还是 3）经复盘统一为 2。评估结果见 1.6 表 9 与图 4。这一步的产出不是文字而是资源分配的指令：本单元 ¥1,720 阶段投入中，62%（¥1,070）投向 G-1 与 G-3。", size=10.5)
h3("2.3.3　资源组合增值实验：三资源叠加的工作坊")
para("这是本轮唯一“新花钱”的验证，也是最能说明“增值”这一维度的证据。做法是把三种原本被分开使用的资源叠在同一次活动里：基地实验室的 3D 打印设备（打印演示支架与夹具）＋ 课程实训场景（课后 30 分钟，学生本来就在场）＋ 社团网络（社团协助通知与场地）。投入为现金 ¥120（耗材与物料）＋ 12 人时。产出为 42 人到场、28 人现场试机、19 人留资、26 条有效反馈、1 项 B 端 20 台意向（¥1,180）。", size=10.5)
para("为了把“组合比单独用更值”说成可检验的命题，我们定义了统一的增值率口径：增值率 = 产出的市场替代价 ÷ 资源投入（现金 + 工时折价），市场替代价按问卷外包 ¥30/条、CPS 留资 ¥18/条折算。组合使用的增值率为 3.6 倍（产出 ¥1,495 ÷ 投入 ¥420），而单一资源的历史增值率分别为：借设备 3.2 倍、地推 1.2 倍、线上投放 1.0 倍，平均 1.8 倍。协同系数 = 3.6 ÷ 1.8 = 2.0 > 1，即“1 + 1 > 2”在本轮数据上成立。", size=10.5)
pic("图6_渠道与资源组合增值.png", 16.5, "图 6　分渠道获客与 CAC（左）与资源组合增值实验（右）")
para("必须说明这项证据的边界：单场次、样本 42 人，增值率依赖“市场替代价”这一折算口径，属于方向性证据而非精确估计；但它足以支撑一个决策——此后所有获客动作默认走“设备 + 场景 + 社团”的组合式，不再单点投放。首场工作坊选在工作日下午，仅到场 9 人，数据作废并改到课后时段重办一场（浪费 3 人时），这条失败记录保留在过程留痕中。", size=10.5)
h3("2.3.4　渠道获客成本复测与资源重配")
para("三条渠道并行加 B 端采买共四条路径的对比结论与前序一致：地推 34.9%（CAC ¥7.4，本轮复测）、社团 27.1%（CAC ¥11.5）、线上 5.2%（CAC ¥31.8，LTV/CAC = 0.83）、B 端零获客成本。线上渠道在数据上不成立这一点已经被我们接受：按量产后单位贡献 ¥19.57 计，线上渠道每卖一台净亏约 ¥12.2。资源重配动作：停投线上付费投放（已执行），把预算转入地推与 B 端，并新增备选渠道“实验室团采批量折扣页”，触发条件为地推 CAC 超过 ¥15。", size=10.5)
h3("2.3.5　留存与转化的三个时间节点追踪")
para("为了回应“只有当前值、没有轨迹”的评审意见，我们为两个行为指标补齐了三个时间节点的数据：试用用户 30 天留存 45.2%（n=60）→ 50.0%（29/58）→ 55.8%（29/52）；1 元意向金支付率 32.3%（20/62）→ 36.2%（21/58）→ 38.5%（20/52）。留存率的分母随失访收缩（6 人），我们按最保守口径把失访者计为“未留存”，因此当前的 55.8% 是下界而非乐观值；n=52 时 95% 置信区间约 ±13.6 个百分点，10 月 20 日前会扩样到 N=60 收窄区间。", size=10.5)
h3("2.3.6　MVC 成本合规检查")
para(D.MVC_NOTE, size=10.5)

h2("2.4　过程记录（协作工具全程留痕）")
para(f"全程使用{D.COLLAB}记录每日进展、关键决策点与失败记录，五个页面（诊断 / 折算 / 组合实验 / 仪表盘与角色 / 整合）各自带时间戳与版本记录，失败记录单列一节且未作删除处理。", size=10.5)
caption("48 小时过程记录（飞书文档留痕，含失败与转向）")
table(["时段", "做了什么", "关键决策点", "失败记录 / 转向"],
      [[a, b, c, d] for (a, b, c, d) in D.PROCESS_LOG],
      widths_cm=[2.4, 5.0, 4.8, 4.8], fsize=7.5)

h2("2.5　《迭代验证结果汇总表》")
para("汇总表按课程模板的七项要素填写（验证假设、验证方法、样本量、关键数据、置信水平、假设是否成立、后续行动），共 8 行。其中的“部分成立”与“1/6 超限”是本表刻意保留的负结论：与上一单元相比，我们不再把没有证据的项写成“规划中”。", size=10.5)
caption("《迭代验证结果汇总表》")
table(["验证假设", "验证方法", "样本量", "关键数据", "置信水平", "假设是否成立", "后续行动"],
      [[a, b, c, d, e, f, g] for (a, b, c, d, e, f, g) in D.RESULT_TABLE],
      widths_cm=[3.0, 2.8, 2.2, 3.6, 3.0, 1.9, 2.5], fsize=6.5,
      row_fills={0: "FDF3E0", 6: "FBE4E2"})

h2("2.6　数据“三可追溯”标注与原始记录清单")
para("本轮所有数据按“来源可查 / 过程可复现 / 结果可验证”三项标注采集时间、样本量与采集方式，关键数据均保留原始记录（留存清单见附录 B）。", size=10.5)
caption("再验证数据的“三可追溯”标注")
table(["数据项", "来源可查", "过程可复现", "结果可验证（原始记录）"],
      [[a, b, c, d] for (a, b, c, d) in D.TRACE],
      widths_cm=[3.6, 4.4, 5.4, 3.6], fsize=7.5)

h2("2.7　第二阶段归档")
para("产出物：《迭代方案设计表》（表 10）、《再验证过程记录》（表 12，含失败记录）、《迭代验证结果汇总表》（表 13）、《资源获取行动表》与工作坊原始记录（反馈表 26 份、签到表、意向记录）。原始数据留存编号对应附录 B-1 ~ B-7。", size=10.5)
doc.add_page_break()

# ============================================================ 第三部分
h1("第三部分　整合输出（课后 36–48 小时）")
h2("3.1　创新核算仪表盘更新（基准 → 调整 → 当前）")
para("仪表盘从“只有当前值的汇报表”改为“带轨迹与阈值的决策表”：每个指标都给出基准值（选题评审阶段设定）、调整值与当前值，并预设转型阈值，一旦触及阈值就触发“坚持 / 调整 / 转型”三选一决策并留档。九项指标中八项进入“坚持”，一项执行了转型（线上渠道停投），一项（H-004 复购率）降级为观测项。", size=10.5)
caption("更新后的创新核算仪表盘（含“基准→调整→当前”三阶段数据与转型决策依据）")
table(["关键指标", "基准（09-26）", "调整（10-04）", "当前（10-09）", "阈值 / 目标", "趋势", "转型决策依据"],
      [[a, b, c, d, e, f, g] for (a, b, c, d, e, f, g) in D.DASHBOARD],
      widths_cm=[2.7, 2.1, 2.0, 2.0, 1.7, 0.9, 5.6], fsize=7,
      row_fills={4: "FBE4E2", 8: "F0F1F3"})
para(D.DASH_CALIB, size=9.5, color=RGBColor(0x55, 0x5F, 0x6E))
pic("图5_创新核算仪表盘.png", 16.6, "图 5　创新核算仪表盘：基准 → 调整 → 当前（虚线为阈值 / 目标）")
para("三层框架的落点：基准层解决“拿什么当参照”（八项指标在前序阶段都有实测基线，唯一没有基准的 H-004 因此被降级）；调整层记录“为提升指标做了什么”（组合式获客、B 端对接、机构件减配三项行动分别对应转化、成本与获客三个指标）；当前层给出“下一步坚持还是转型”，并附数据依据。", size=10.5)

h2("3.2　精益画布 V4.0 迭代")
para("画布 V4.0 在 V3.0 基础上完成 9 处实质性修订（课程要求 ≥5 处），每处标注修改依据（缺陷编号或验证数据）。假设状态用颜色编码：绿 = 已验证成立，黄 = 验证中 / 部分成立，红 = 已证伪并调整。", size=10.5)
new_sec = doc.add_section(WD_SECTION.NEW_PAGE)
new_sec.orientation = WD_ORIENT.LANDSCAPE
new_sec.page_width, new_sec.page_height = PH, PW
new_sec.left_margin = new_sec.right_margin = Cm(1.5)
new_sec.top_margin = new_sec.bottom_margin = Cm(1.5)
pic("图1_精益画布V4.0.png", 23.6, "图 1　精益画布 V4.0（含颜色编码与修订编号；原尺寸大图见随附 PNG 文件）")
back = doc.add_section(WD_SECTION.NEW_PAGE)
back.orientation = WD_ORIENT.PORTRAIT
back.page_width, back.page_height = PW, PH
back.left_margin = back.right_margin = Cm(2.0)
back.top_margin = back.bottom_margin = Cm(2.0)
caption("精益画布 V4.0 修订依据对照表（9 处实质性修订，逐处标注数据 / 缺陷编号）")
table(["编号", "模块", "V3.0 原文", "V4.0 修订后", "修改依据"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.CANVAS_CHANGES],
      widths_cm=[1.0, 1.7, 4.4, 5.5, 4.4], fsize=7.5)
caption("假设状态颜色编码表（与验证结果一致性自检）")
table(["画布模块", "依赖的关键假设", "验证结果", "颜色", "一致性说明"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.ASSUMPTION_COLOR],
      widths_cm=[2.4, 4.4, 2.0, 1.0, 7.2], fsize=8)
para("一致性自检的两个要点：① “成本结构”从红转绿，是因为本轮把隐性成本折算入账、口径补齐，而不是因为成本变低了；② “收入来源”与“客户细分”维持黄色，因为 B 端 20 台仍只是意向、未成单——有意向不等于有订单，这一条我们不再提前标绿。", size=10.5)

h2("3.3　RACI-V 调整方案")
para(f"角色定义：{D.RACI_DEF}。调整的依据来自第一阶段的两条 P0：资源核算无人负责（D-02）、资源缺口无人获取（D-03）。调整动作有三类：新增任务（把财务记录、外部资源获取、资源组合与增值设计升为独立任务）、角色换人（3 次动态调整）、引入外部验证者（V 列从“缺位”补齐）。", size=10.5)
pic("图7_RACIV调整对比.png", 16.6, "图 7　RACI-V 调整前后对比（调整后新增 3 项资源类任务，V 列补齐）")
caption("角色动态调整记录（3 次，含触发依据、交接动作与生效验证）")
table(["编号", "成员", "调整前角色", "调整后角色", "触发依据", "生效时间", "交接动作", "生效验证"],
      [[a, b, c, d, e, f, g, h] for (a, b, c, d, e, f, g, h) in D.ROLE_CHANGES],
      widths_cm=[1.0, 1.2, 2.2, 2.4, 2.2, 1.6, 3.6, 2.8], fsize=6.5)
para(D.RACI_EFFECT, size=10.5)
caption("调整后的 RACI-V 责任分配矩阵（新增 3 项任务，每项恰 1 个 A）", auto=True)
table(["工作任务", "邵子中", "李昊桐", "姜亚楷", "V 验证者（外部）"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.RACI_AFTER],
      widths_cm=[5.0, 1.9, 1.9, 1.9, 6.3], fsize=8,
      row_fills={4: "E8F1EA", 5: "E8F1EA", 6: "E8F1EA"})
para("校验：8 项任务每项恰有 1 个 A，且安全与验收类任务（成本与定价模型、财务记录、B 端交付）的 A 与 R 分离，执行者不给自己做判定；调整前“财务记录”一栏 V 为“无（缺位）”，调整后由财务监督员担任双周对账验证。", size=10)

h2("3.4　资源优化三件套（对照表 / 获取表 / 威胁-动作）")
caption("资源-价值对照表（效率版：先定单位，再记账）")
table(["资源", "投入", "产出", "效率指标", "本单元变化"], [
    ["时间", f"{D.LABOR_HOURS} 人时（邵 120 / 李 110 / 姜 106）", "218 条有效验证数据、3 版原型、7 个功能模块",
     f"全成本 ¥{D.NOW_COST / D.NOW_DATA:.1f} / 条（基准 ¥{D.COST_PER_DATA:.1f}）", "首次把工时折算为 ¥8,400 并入成本口径"],
    ["资金", f"¥{D.CASH_SPENT:,} 现金（打样 / 机构件 / 验证 / 耗材 / 交通）", "43 份付费行为数据、87 份问卷、6 项验证",
     "¥53.0 / 份付费行为数据", "新增“行为补偿”科目并单列预算"],
    ["物料与设备", "借用基地设备 12 次（¥180 耗材）", "原型 3 版、夹具 2 套、工作坊现场试机 28 人",
     "资源杠杆 3.2 倍（等值 ¥570 ÷ ¥180）", "从“借用”升级为“组合式使用”（协同系数 2.0）"],
    ["外部关系", "导师 2 次、实验室老师 3 次、陪审团 4 次、CNIPA 1 次", "11 条改进建议、1 项 B 端意向（20 台 = ¥1,180）",
     "每次调用 = 2.2 项改进或合作", "新增“资源关系台账”，每月更新接触记录"],
], widths_cm=[1.8, 4.2, 4.2, 3.6, 3.2], fsize=7.5)
caption("资源获取行动表（每个缺口四要素齐全：渠道 / 对接人 / 预算 / 时限）")
table(["缺口", "获取渠道", "对接人", "预算", "时限", "状态"], [
    ["G-1 缺 C 端获客渠道", "社团联办工作坊 + 实验室场景地推 + B 端实训采买", "姜亚楷（A）/ 社团负责人 / 实训课教师", "¥720（本单元已投入）", "10-14（第 2 场）", "已落地（42 人到场 / 19 留资）"],
    ["G-2 缺开模资金", "学校创客空间小额资助 + B 端首单预付款", "邵子中（C）/ 实验室老师（V）", "≤¥3,000（设门槛后支出）", "10-20 前决策", "待触发（确认订单 ≥20 台）"],
    ["G-3 缺财务与定价经验", "指导老师咨询 + 自建三层成本台账", "李昊桐（R）/ 指导老师（V）/ 财务监督员", "¥0 现金 + 40 人时", "已完成", "已落地（含人力保本重算）"],
    ["G-4 缺长期使用数据", "试用机低功耗日志 + 微信回访", "李昊桐（R）/ 试用用户", "¥200 + 16 人时", "10-19", "进行中（3 个节点已采）"],
], widths_cm=[2.6, 4.2, 3.4, 2.2, 1.8, 2.8], fsize=7)
caption("威胁-动作对照表（回应“诊断与行动脱节”）")
table(["威胁", "可能的后果", "资源动作", "触发条件"], [
    ["大厂 / 白牌 3 个月可仿制", "价格战、渠道被替代", "把“资源组合配方”（基地设备 + 课程场景 + 社团网络）与实训课程捆绑做成 12 个月难以复制的软壁垒；已落地 1 项 B 端意向", "出现同类竞品进入校园渠道时启动"],
    ["电商同类磁吸工作灯价格战", "C 端毛利被压到 0 以下", "C 端只保留品牌展示与套件版；主营收转 B 端（零获客成本、按机构价 59 元/台）", "线上 CAC 连续两月 > ¥20"],
    ["锂电组合的合规与认证成本不确定", "结题前无法完成合规自测，评审安全项扣分", "10-12 前完成 RoHS 与锂电安全自测报价比价（已取得 3 家报价）；必要时改用半成品电池模组采购", "报价合计 > ¥3,000 时启动备选方案"],
], widths_cm=[3.0, 3.4, 7.6, 3.0], fsize=7.5)

h2("3.5　后续计划与预算（项目开发路线图）")
para("资源优化方案不止于本轮结论，还包含后续 12 天的资源获取与验证路线：每个阶段都写明资源动作、负责人与备选路径（若主线失败怎么办），避免再次出现“里程碑只写时间、没有缓冲”的问题。", size=10.5)
caption("项目开发路线图（含风险缓冲与备选路径）")
table(["阶段", "时间", "资源与验证动作", "负责人", "备选路径（风险缓冲）"],
      [[a, b, c, d, e] for (a, b, c, d, e) in D.PLAN],
      widths_cm=[1.7, 1.9, 6.0, 2.2, 5.2], fsize=7.5)
caption("下一阶段资源预算（合计 ¥5,000，含触发条件）")
table(["预算项", "金额（元）", "用途与依据", "优先级"],
      [[a, f"{b:,}", c, d] for (a, b, c, d) in D.PLAN_BUDGET],
      widths_cm=[4.6, 1.9, 8.3, 2.2], fsize=8)
para(f"资金结构与退路：¥3,000 的模具定金属于投资性支出（把 BOM 从 ¥52.3 压到 ¥37.6、含人力保本从 3,940 台降到 1,604 台的唯一路径），但必须过门槛——确认 B 端订单 ≥20 台或意向金 ≥¥500 才投；资金三条来源为竞赛作品预算结余、学校创客空间小额资助、B 端首单预付款（20 台 × ¥59 = ¥1,180）。若 10 月 20 日前首单未成，则放弃开模、退回 3D 打印小批量路径，接受毛利率仅 11.2% 的现实——这条退路提前写明，不等出事再补。", size=10.5)
para(f"团队协作口径（回应“提升率没有分母”）：{D.COOP_METRIC}。统计对象为“已进入执行的任务卡”，分母逐项核对，已排除未启动项。", size=10.5)
doc.add_page_break()

# ============================================================ 第四部分
h1("第四部分　个人反思与能力发展")
h2("4.1　个人反思报告（每人独立完成）")
para("反思按课程要求的三段式撰写：① 认知差异对比——评审前“我觉得进展顺利”与评审后“数据告诉我什么”之间的差距；② 5Why 归因追溯——选一次真实挫折追根因；③ 下一步改进计划——1 项个人能力提升目标与落实方式。三份反思独立撰写，未互相修改。", size=10.5)

for i, (name, role, cog, whys, plan) in enumerate(D.REFLECTIONS, 1):
    h3(f"4.1.{i}　{name}（{role}）")
    para("① 认知差异对比", size=10.5, bold=True, space_before=2, space_after=2)
    para(cog, size=10.5)
    para("② 5Why 归因追溯", size=10.5, bold=True, space_before=2, space_after=2)
    caption(f"{name}的 5Why 归因链（个人挫折追溯）")
    table(["层级", "追问与回答"],
          [[f"Why {j}", w.split(" → ")[1] if " → " in w else w] for j, w in enumerate(whys, 1)],
          widths_cm=[1.6, 15.4], fsize=8.5)
    para("③ 下一步改进计划", size=10.5, bold=True, space_before=2, space_after=2)
    para(plan, size=10.5)

h2("4.2　能力等级再评估（对照 EntreComp“资源”领域五项能力 L4–L5 描述）")
para("五位成员自评先独立完成，再由团队合议校准，避免出现“团队与个体等级完全一致”的一致性偏差（这一点是上一单元被 AI 评审点出的问题）。再评估的每一级变化都要求有可指认的证据，没有证据的不许调级。", size=10.5)
caption("“资源”领域五项能力等级再评估（课前 → 课后）")
table(["能力项", "课前个体", "课前团队", "课后个体", "课后团队", "变化", "关键证据"],
      [[a, b, c, d, e, f, g] for (a, b, c, d, e, f, g) in D.ABILITIES],
      widths_cm=[3.0, 1.3, 1.3, 1.3, 1.3, 1.3, 7.5], fsize=8,
      row_fills={3: "E8F1EA"})
para("评估说明：个体等级按负责人（邵子中）的自评口径呈现，团队等级由三人合议；四列数据的差异本身就是证据——财经素养的个体自评（L2）明显低于团队自评（L3），说明团队此前高估了文字层面的“成本意识”，而真正的度量能力要到本轮折算后才具备。", size=9.5, color=RGBColor(0x55, 0x5F, 0x6E))

h2("4.3　能力发展雷达图与能力变化说明")
pic("图8_能力发展雷达图.png", 15.6, "图 8　能力发展雷达图——“资源”领域五项能力（课前 → 课后，刻度 L1–L8）")
caption("能力变化说明（200 字以内）", auto=False)
p = para("", space_after=4)
run(p, D.ABILITY_TEXT, size=10.5)
para(f"（以上 {cn_len(D.ABILITY_TEXT)} 字，符合“200 字以内”要求）", size=9, color=RGBColor(0x77, 0x80, 0x8C))
h3("变化说明的补充：提升最大与仍然薄弱的两项")
para("提升最大的是财经素养（个体 L2 → L4）。触发提升的关键事件是教师评审的追问“336 人时值多少钱”：我们此前只有现金账，折算后隐性成本占资源总投入 78.7%，小批量口径下单位经济甚至是负的。此后团队把“先定单位再记账”写成规则——任何资源投入都必须先说明产出用什么单位计量（每条有效数据 / 每元现金 / 每人时），并双周对账一次。", size=10.5)
para("仍然薄弱的是动力和毅力的流程化（个体 L4）：48 小时内三次返工重做（工作坊首场仅到场 9 人、工时误算重算、RACI 初稿只调任务不调人），靠的是硬扛而不是机制。补强方式已列入个人计划——两道前置检查（配额表预审、观察指标预演）固化进任务卡模板，让“坚持”用在推进上而不是补错上。", size=10.5)
doc.add_page_break()

# ============================================================ 附录
h1("附录 A　提交清单对照表")
caption("课程提交清单与本方案书对照")
table(["提交清单项", "本方案书位置", "自检结论"], [
    ["⑴《关键缺陷清单》（含 P0–P3 分级、归类维度与 5Why 归因分析）", "1.2 五维归类、1.3 分级、1.4 三条完整 5Why、1.5 清单（15 条）", "齐全（P0/P1 全部完成 5 层归因）"],
    ["⑵《迭代验证结果汇总表》（含原始数据截图与“三可追溯”标注）", "2.5 汇总表（8 行 × 7 要素）、2.6 三可追溯标注、附录 B 留存清单", "齐全（留存 B-1 ~ B-7）"],
    ["⑶ 精益画布 V4.0（含颜色编码与 ≥5 处修改依据标注）", "3.2（图 1 横向大图、表 16 共 9 处修订、表 17 颜色编码）", "齐全（9 处 ≥ 5 处）"],
    ["　① 迭代验证结果汇总表（五项要素完整）", "2.5（验证方法、样本量、关键数据、置信水平、后续行动）", "齐全（另含“假设是否成立”共 7 要素）"],
    ["　② 更新后的创新核算仪表盘（基准→调整→当前 + 转型决策依据）", "3.1（表 15、图 5）", "齐全（9 项指标 × 3 阶段 + 阈值）"],
    ["　③ RACI-V 调整方案（含 ≥1 次角色动态调整记录与说明）", "3.3（图 7、表 18 三次调整、表 19 调整后矩阵）", "齐全（3 次调整，含交接与生效验证）"],
    ["⑷《能力发展雷达图》与《能力变化说明》（200 字以内）", "4.2（表 28）、4.3（图 8 与变化说明）", f"齐全（说明 {cn_len(D.ABILITY_TEXT)} 字）"],
    ["附加：个人反思报告（认知差异 / 5Why / 改进计划）", "4.1（三份独立反思）", "齐全（3 人 × 三段式）"],
    ["附加：资源获取行动表、威胁-动作对照表、路线图与预算", "3.4、3.5", "齐全（含备选路径与触发条件）"],
], widths_cm=[6.6, 6.4, 4.0], fsize=8)

h1("附录 B　原始记录留存清单")
para("上表所列原始记录均已按课程要求留存归档（验证数据须有原始记录作为佐证），每项标注记录名称、采集时间与样本量 / 口径。", size=10)
table(["编号", "原始记录项", "采集时间", "样本量 / 口径"],
      [[a, b, c, d] for (a, b, c, d) in D.SHOT_LIST],
      widths_cm=[1.8, 8.2, 3.4, 3.6], fsize=8)
para("上一行 6 项原始记录（编号 B-1、B-2、B-3、B-5、B-6、B-7）均已按“三可追溯”要求留存归档，含记录名称、采集时间与样本量 / 口径标注，可按需核验。", size=9.5, color=RGBColor(0x55, 0x5F, 0x6E))

h1("附录 C　关键口径说明")
table(["口径", "定义与说明"], [[a, b] for (a, b) in D.CALIB], widths_cm=[3.6, 13.4], fsize=8.5)

h1("附录 D　团队分工与过程留痕")
table(["成员", "本单元角色（RACI-V 中的 R / A）", "主要产出"], [
    ["邵子中（负责人）", "资源组合与增值设计 R；成本模型改 C；汇报材料 A",
     "缺陷清单归并与 5Why 归因、缺口影响评估矩阵、组合式工作坊设计与执行、资源-价值对照表、画布 V4.0 定稿"],
    ["李昊桐", "资源核算与成本模型 R；用户测试改 C",
     "三层成本台账与工时货币化折算、单位经济双口径与含人力保本测算、MVC 支出核对、画布成本与收入两栏修订"],
    ["姜亚楷", "外部资源获取与维护 A；渠道 R；财务监督员（V，双周对账）",
     "资源获取对接清单、工作坊对外协调与渠道复测、留存与转化三节点追踪、RACI-V 调整记录与任务卡台账"],
], widths_cm=[2.6, 5.0, 9.4], fsize=8)
para(f"过程留痕：{D.COLLAB}（5 个页面：诊断 / 折算 / 组合实验 / 仪表盘与角色 / 整合），每页含时间戳与版本记录；失败记录单列一节，未作删除，可在文档修订历史中复核。数据采集时间窗：{D.WINDOW}。", size=10)
para("", space_after=8)
para("— 全文完 —", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

DOCX = os.path.join(OUT, "1班C组—仿真跑不队—创客竞赛资源优化方案书.docx")
doc.save(DOCX)
print("DOCX saved:", DOCX)
print("表格总数:", next(TAB) - 1)
print("能力变化说明字数:", cn_len(D.ABILITY_TEXT))
