# -*- coding: utf-8 -*-
"""生成《创客竞赛作品结题报告》（课前版 V1.0）"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data2 as D
from report_members import CH2, CH3, CH4_PERSONAL
import report_v2_content as V2

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREYT = RGBColor(0x66, 0x6E, 0x7A)
CNT = {"n": 0}
CNTP = {"n": 0}
STOP = {"v": False}   # 进入“附件”（附录）后不再计入正文字数


def R(p, t, size=10.5, bold=False, color=None, count=True):
    r = p.add_run(t); r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None:
        r.font.color.rgb = color
    if count:
        CNT["n"] += sum(1 for ch in t if not ch.isspace())
    return r


def para(t="", size=10.5, bold=False, align=None, sb=0, sa=4, color=None, indent=None, count=True):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if indent: p.paragraph_format.left_indent = Cm(indent)
    if t:
        R(p, t, size=size, bold=bold, color=color, count=(count and not STOP["v"]))
        if count and not STOP["v"]:
            CNTP["n"] += sum(1 for ch in t if not ch.isspace())
    return p


def h1(t):
    if t.startswith("附件"):
        STOP["v"] = True
    p = para(t, size=15, bold=True, sb=12, sa=8, count=False)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
    b.append(e); pPr.append(b)


def h2(t):
    return para(t, size=12, bold=True, sb=8, sa=5, color=NAVY, count=False)


def h3(t):
    return para(t, size=11, bold=True, sb=6, sa=3, color=RGBColor(0x33, 0x44, 0x55), count=False)


def shade(c, hexc):
    tcPr = c._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def table(headers, rows, widths, fsize=8.5, row_fills=None, count=True):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j); c.text = ""
        R(c.paragraphs[0], h, size=fsize, bold=True, count=False)
        c.paragraphs[0].paragraph_format.space_after = Pt(0); shade(c, "D9E2F3")
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""
            for k, seg in enumerate(str(v).split("\n")):
                p = c.paragraphs[0] if k == 0 else c.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                R(p, seg, size=fsize, count=count)
            if row_fills and row_fills.get(i - 1): shade(c, row_fills[i - 1])
    for j, w in enumerate(widths):
        for i in range(len(rows) + 1):
            t.cell(i, j).width = Cm(w)
    para("", size=6, sa=2, count=False)


def cap(t):
    return para(t, size=9, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6,
                color=RGBColor(0x33, 0x33, 0x33), count=False)


doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.2
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(2.0)

# ================= 封面 =================
para("", sa=16, count=False)
para("华中科技大学未来技术学院 · 创客训练营", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT, count=False)
para("创客竞赛作品结题报告（V2.0）", size=24, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6, count=False)
para(f"{D.PROJ} —— {D.TOPIC}", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, sa=18, count=False)
table(["项目", "内容"], [
    ["团队名称", D.TEAM_FULL],
    ["团队成员与角色", "邵子中（负责人，U202511546）：经济模型 / 固件 / 材料统筹　|　李昊桐：焊接工艺 / 实测与可靠性　|　姜亚楷：渠道与 B 端对接 / 财务监督"],
    ["选题名称与主题", f"{D.PROJ}（AI+OPC 能力范式）"],
    ["作品开发阶段", "准成品：核心功能闭环完整（磁吸—悬停—调光—状态—安全保护全链路），已完成 22 台小批量试制与交付、8 小时连续工况复测与同批一致性抽检；量产工艺与长周期使用数据按结题后迭代计划推进（见第四章 4.1 / 附件二）"],
    ["报告版本", "V2.0（课后版，经课堂评审反馈迭代；V1.0 课前版修订对照见下页）　|　项目周期：" + D.PERIOD],
    ["日期", D.FINAL_DATE],
], [3.4, 13.6], 9.5, count=False)
para("", sa=6, count=False)
para("撰写分工：第一章、第四章由团队合写；第二章、第三章由成员分别独立撰写并署名。本次修订遵循“二阶迭代法”：问题锚定与归因（0–12h）→ 证据补强与报告迭代（12–36h）。正文约 X 字（不含附录与表格）。",
     size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT, count=False)

doc.add_page_break()
h1("修订说明：V1.0 → V2.0 修订对照")
para("本次修订以课堂评审反馈为靶向，共整理有效反馈 10 条（P0 2 / P1 4 / P2 2 / P3 2），逐条落位到具体章节；"
     "原则是按“问题-行动-证据”三阶模型重构论证链条，补强优先零现金成本方案。")
cap("表 0-1　V1.0 → V2.0 修订对照表")
table(["位置", "V1.0 的问题", "V2.0 的修订", "触发反馈"], [list(r) for r in V2.REVISION],
      [1.9, 5.0, 7.0, 3.7], 8.5)
para(V2.SUPP_COST, size=9.5, color=GREYT)

doc.add_page_break()
# ================= 第一章 =================
h1("第一章　项目成果总览（团队合写）")

h2("1.1　项目情景分析")
para("三位成员都是狭小焊台照明场景的真实使用者：负责人调测验证板时 17 个焊点返工 3 次；李昊桐用 49 元小夜灯凑合，灯头一碰就歪；"
     "姜亚楷工位桌面仅 0.8×0.6 米，台灯底座占去四分之一。")
para("价值假设由“场景观察 → 需求陈述”形成：选题阶段 126 份问卷 + 3 份洞察记录，提炼出“焊点照明的近、稳、准三缺一”，三类现有灯具都无法同时满足。"
     "原始记录如极客原话“大灯照不到，小灯转天就歪，我干脆手拿着焊”。")

h2("1.2　项目问题分析")
para("用同理心地图拆解用户处境：他们在意的是“这颗焊点能不能一次焊对”，而非灯具亮度。痛点表现为反复中断——行为观察（5 人 × 3 天、15 次）"
     "记录到每次 20 分钟焊接平均 4.2 次“找光/转板”、2.6 次“挪灯/手扶”，13/15 次出现“灯头偏移后未复位”。根因：传统灯具都是“底座思维”，"
     "而焊台需求是在垂直空间里被吸附固定。")
para("天使客户：有课程强制焊接任务、每周焊接 ≥3 次、由实验室统一采购工具的电子类专业学生——既是高频使用者，也是 B 端采买的受益者。")

h2("1.3　项目定位与核心价值主张")
para("一句话定位：为高校电子类专业学生与 DIY 极客，解决狭小焊台“灯照不到、靠不住、要手扶”的磁吸万向焊接照明工具。")
para("核心价值主张：给焊接者一双腾出来的手——磁吸固定、万向悬停、无级调光，百元内可得（主线 65 元）。量化目标：找光动作每次减少 4.2 次；"
     "焊接失败率 50%→20%；任务完成率 ≥85%；意向金支付率（行为口径）≥30%。")

h2("1.4　创新核算仪表盘（完整版）")
cap("表 1-1　创新核算仪表盘：选题 → 中期 → 结题三阶段（含三类对比）")
rows = []
for d in D.DASH:
    name, q1, q2, q3, plan, mean, best = d[0], d[1], d[2], d[3], d[4], d[5], d[6]
    rows.append([name, q1, q2, q3, plan, f"均值 {mean} / 最优 {best}"])
table(["指标", "选题时", "中期", "结题当前值", "计划（结题目标）", "团队均值 vs 最优值"], rows,
      [3.2, 1.6, 1.6, 2.0, 2.6, 3.0], 8.5)
para("三类对比（明细见表 1-1）：中期 vs 结题——验证数据 157→312、完成率 50%→78%、意向金支付率 32.3%→37.3%；计划 vs 实际——达标 3 项、"
     "未达 2 项（完成率 78%<85%、成本 ¥43.0>¥40）；均值 vs 最优——完成率 78% vs 92%、成本 ¥43.0 vs ¥39.6。")
para("决策说明：【坚持】磁吸万向方案与安全底线；【调整】“状态显示”由卖点降级为说明书步骤，验收标准由“功能状态”改为“用户行为指标”；"
     "【转型】商业模式转为“B 端实训采买 + 套件引流 + C 端小而美”——依据是线上 LTV/CAC 仅 0.83，而 B 端零获客成本。")

h2("1.5　关键假设验证总览")
cap("表 1-2　关键假设验证状态（与精益画布 V3.0 编号一致）")
table(["假设编号", "假设内容", "验证方法", "验证结果", "验证状态", "数据来源"],
      [["H-001", "用户愿为“磁吸固定 + 万向调光”支付 59–79 元", "分层问卷 + 预售页双价格锚定 A/B + 1 元可退意向金",
        "态度口径 71.3% 会买；行为口径意向金支付率 37.3%（22/59）；A 组预售转化 31.8%", "部分成立（态度成立、行为未达原预期）",
        "问卷后台导出、收款记录 E-09"],
       ["H-002", "6 颗 LED 状态灯可覆盖 80% 状态查询需求（替代 OLED）", "20 人配对 A/B（交叉重测）",
        "A 组覆盖 82% vs OLED 86%（差 4pp < 10pp）；但实际查询仅 1.6 次/25 分钟，需求被高估", "成立（卖点降级）", "配对测试记录 E-08"],
       ["H-003", "14 天内推荐率 ≥45%（NPS ≥40）", "结题期扩样回访（N=59）", "推荐率 52.5%；NPS 42", "成立", "回访记录 E-05"],
       ["H-004", "90 天复购率 ≥20%", "销售后 90 天回访", "周期不足，未执行；改以“B 端批量续订意愿”作为代理指标（现有 1 项续订意向）", "未验证（延后）", "—"],
       ["H-005", "整机 BOM ≤50 元时毛利率 ≥40%", "三档 BOM 询价 + 单位经济与保本测算",
        "小批量 BOM 实测 ¥52.3（毛利 11.2%）；千片 ¥37.6（标准版单位贡献 ¥22.0、毛利 33.8%）", "已证伪并调整（毛利目标分规模修订）",
        "询价单 E-11"]],
      [1.4, 3.4, 3.0, 4.6, 2.4, 2.2], 8)

h2("1.5.1　数据来源与采集方式标注表（V2.0 新增）")
cap("表 1-2b　关键数据的“三要素”标注（采集时间 / 采集方式 / 样本量）")
table(["关键数据", "采集方式", "原始记录", "采集时间", "样本量"], [list(r) for r in V2.DATA_SOURCE_TABLE],
      [3.4, 3.2, 3.8, 2.6, 4.6], 8)
para("说明：V1.0 未标注三要素（F-03），本表为修订后统一口径，PPT 与报告同源。", size=9.5, color=GREYT)
h2("1.5.2　结论依赖分析：H-004 未验证的影响范围（V2.0 新增）")
cap("表 1-2c　哪些结论依赖 H-004（复购假设）")
table(["项目结论", "是否依赖 H-004", "若不依赖 / 依赖时的处理"], [list(r) for r in V2.DEPEND_ON_H004],
      [5.4, 3.0, 9.2], 8.5)
para("说明（回应 F-05）：四项核心结论均不依赖 H-004，仅“规模增长”依赖且已有降级目标（1,232 台保本线），故不会推翻价值结论。", size=9.5, color=GREYT)
h2("1.6　资源-价值总表")
cap("表 1-3　资源-价值总表（投入量与产出对应关系及转化效率）")
table(["资源类型", "具体项目", "投入量", "产出类型", "具体成果", "转化效率"],
      [["经费", "三阶段现金支出（打样、器件、机构件、验证、试制备料、演示物料）", "¥5,310", "验证数据", "312 项有效验证数据", "每 ¥17.0 = 1 项"],
       ["经费", "调研与测试礼品、支付通道备用金", "¥940", "行为数据", "43 份真实付费行为数据（含 20 份意向金）", "每 ¥21.9 = 1 份"],
       ["时间", "团队全周期工时（720 人时：168 + 336 + 216）", "720 小时", "验证数据", "312 项有效验证数据", "每 2.3 人时 = 1 项"],
       ["时间", "结题阶段追加工时（引导优化 + 温升改造 + 交付）", "216 小时", "产品成果", "V4.0 定稿版 + 修复 31 项缺陷", "每 6.2 小时 = 1 项产品成果"],
       ["外部资源", "实验室设备使用权、导师咨询、社团宣传位（估值）", "¥3,060", "认知突破", "5 个假设验证结论 + 9 条洞察 + 3 个决策转折点", "每 ¥175.8 = 1 项认知成果"]],
      [1.5, 4.6, 1.5, 1.4, 4.0, 2.0], 8)
para("效率换算（主口径）：投入 ¥8,370、产出 376 项 → 每 ¥100 约 4.5 项可验证产出；只按现金 ¥5,310 计为 7.1 项/¥100（附注口径，见表下注）。")

h2("1.7　团队效能数据")
cap("表 1-4　RACI-V 分工总览（结题阶段）")
table(["关键任务", "R（执行）", "A（审批）", "C（咨询）", "I（知悉）", "V（支持者）"],
      [["用户调研与需求分析", "邵子中", "邵子中", "李昊桐、姜亚楷", "全体", "指导老师"],
       ["原型结构设计与制作", "李昊桐", "邵子中", "姜亚楷", "全体", "实验室老师"],
       ["用户测试与数据采集", "李昊桐", "邵子中", "姜亚楷", "全体", "社团同学"],
       ["B 端对接与交付验收", "姜亚楷", "邵子中", "李昊桐", "全体", "实验室老师"],
       ["成本与定价模型", "邵子中", "姜亚楷（财务监督）", "李昊桐", "全体", "指导老师"],
       ["结题材料与演示准备", "姜亚楷", "邵子中", "李昊桐", "全体", "上一届学长"]],
      [4.4, 2.2, 3.2, 2.6, 1.4, 2.2], 8.5)
cap("表 1-5　团队效能指标与成员贡献值")
table(["效能指标", "中期值", "结题值", "提升率", "成员", "难度系数", "完成质量", "协作系数", "贡献值"],
      [["任务按时完成率", "91%", "96%", "＋5.5%", "邵子中", "4.5", "92%", "1.15", "4.76"],
       ["团队协作满意度（10 分制）", "8.0", "9.0", "＋12.5%", "李昊桐", "4.2", "95%", "1.10", "4.39"],
       ["有效决策响应时间", "3.5 小时", "1.8 小时", "−48.6%", "姜亚楷", "4.3", "90%", "1.20", "4.64"],
       ["成员贡献值离散度（最高/最低）", "1.42", "1.08", "−24%", "—", "—", "—", "—", "均值 4.60"]],
      [3.6, 1.6, 1.6, 1.5, 1.4, 1.3, 1.3, 1.3, 1.4], 8)
para("贡献值 = 难度系数 × 完成质量 × 协作系数；计算过程见第二章各成员“合作能力”一节的贡献值表。")

doc.add_page_break()
# ================= 第二章 =================
h1("第二章　行动能力发展纪实（成员分别撰写，各自署名）")
para("本章由三位成员分别独立撰写并署名。每项能力按“初始状态（中期）→ 关键事件 → 个人行动 → 当前状态（结题，含等级与证据）”"
     "四段撰写，证据类型包括过程性证据（迭代日志、会议记录）、结果性证据（测试数据、用户反馈）与认知性证据（反思记录）。",
     size=10, color=GREYT)
for member in D.MEMBERS:
    h2(f"2.{D.MEMBERS.index(member)+1}　{member}（{D.ROLES[member]}）")
    for ab in CH2[member]:
        h3(ab["name"])
        para("初始状态（中期）：" + ab["initial"], size=10)
        para("关键事件：" + ab["event"], size=10)
        para("个人行动：" + ab["action"], size=10)
        para("当前状态（结题）：" + ab["current"], size=10)
        if ab.get("contrib"):
            para("个人贡献值计算：", size=10, sb=2, sa=2)
            table(["任务", "难度系数", "完成质量", "协作系数", "贡献值"], ab["contrib"], [5.4, 2.6, 2.6, 2.6, 3.8], 8.5)

para("")
h2("2.4　关键事件 ↔ 证据对应表（V2.0 新增，回应 F-04）")
para("回应 F-04：补“关键事件—证据—可核验方式”，说明谁能查、怎么查。", size=10)
cap("表 2-1　关键事件与证据对应关系（三列：关键事件 / 证据编号 / 可核验方式）")
rows = []
for mem in D.MEMBERS:
    for i, (ab, ev, code, how) in enumerate(V2.EVENT_EVIDENCE[mem]):
        rows.append([mem if i == 0 else "", ab, ev, code, how])
table(["成员", "能力项", "关键事件", "证据编号 / 名称", "可核验方式"], rows,
      [1.3, 1.7, 4.0, 4.4, 6.2], 8)

doc.add_page_break()
# ================= 第三章 =================
h1("第三章　认知跃迁与深度反思（成员分别撰写，各自署名）")
for member in D.MEMBERS:
    m = CH3[member]
    h2(f"3.{D.MEMBERS.index(member)+1}　{member}")
    h3("3.1　四栏反思对比表（V2.0：显式纳入课后评审反馈）")
    table(["课前/课堂的判断", "支撑该判断的实际数据", "课后评审反馈", "认知修正"], V2.DUAL_V2[member],
          [4.0, 4.2, 4.2, 5.2], 8.5)
    h3("3.2　5Why 根因分析")
    table(["环节", "内容"], m["why5"], [2.0, 15.0], 8.5)
    h3("3.3　GROW 模型总结")
    for g in m["grow"]:
        para(g[0] + "：" + g[1], size=10, indent=0.3)
    h3("3.4　认知跃迁声明（200 字以内）")
    p = para(V2.LEAP_V2[member], size=10.5)
    para(f"（本声明 {sum(1 for ch in V2.LEAP_V2[member] if not ch.isspace())} 字）", size=8.5, color=GREYT, count=False)
    h3("3.5　可持续衔接行动")
    table(["项目", "内容"], m["next"], [3.6, 13.4], 8.5)

h2("3.6　最意外的用户反馈及其影响（V2.0 新增，回应 F-10）")
para(V2.SURPRISE, size=10.5)

doc.add_page_break()
# ================= 第四章 =================
h1("第四章　可持续转化与未来规划")
h2("4.1　项目成果转化路径（团队合写，场景一：成品团队）")
para("所选路径：市场化（C 端小批量与 B 端实训采买并行）+ 学术化（结构点申请实用新型专利 1 项）。依据：功能闭环完整、"
     "已完成 22 台试制交付、千片 BOM 已锁定；量产定价下保本销量 1,232 台 < 3 年 SOM 3,100 台，商业闭环成立。")
h3("短期（结题后 3 个月内）：关键行动与所需资源")
table(["关键行动", "预期产出", "所需资源", "资源来源"],
      [["完成注塑模具制作与首批 200 台试产", "首批 200 台合格品 + 注塑工艺文件", "模具定金 ¥3,000（已投）、试产费 ¥10,000", "创客空间小额资助 ¥6,000（已获批）+ B 端预付款 ¥1,298 + 团队自筹 ¥2,702"],
       ["在电工基地设校园自提点", "取消快递成本的交付通道（物流 ¥1.5→¥0）", "自提点场地与储物柜", "实验室老师协调"],
       ["“3 步开工卡”随首单发货并回收 30 份使用反馈", "任务完成率从 78% 提升至 ≥85%", "印刷费 ¥300、3 人 × 8 小时", "团队自筹 + 社团印刷资源置换"]],
      [4.6, 4.2, 3.8, 4.4], 8.5)
h3("中期（结题后 3–12 个月）：阶段性目标与里程碑")
table(["里程碑", "目标描述", "预期完成时间", "关键资源依赖"],
      [["M1　覆盖 3–4 所高校实训课", "达成 1,232 台（量产定价保本销量），B 端占比提升至 45%", "2027-06", "实训课采购对接关系（实验室老师牵线）"],
       ["M2　实用新型专利申请", "完成结构点（磁吸 + 万向悬停 + 可换向磁吸位）申请受理", "2027-03", "专利代理服务（或自写申请，预计费 ¥600）"],
       ["M3　单位变动成本降至 ≤¥40", "物流集包协议落地（¥1.5→¥0.8/台）", "2027-02", "与两家快递的校园集包协议"]],
      [3.6, 6.4, 2.6, 4.4], 8.5)
h3("长期愿景")
para("做成“校园实训工具 + 焊接工位数据接口”：工具进入实训课标配清单，设备的照明状态、使用时长与电量按标准协议上报"
     "实验室管理系统（AI+OPC 主题中的 OPC 落点）。关键成功指标：实训课渗透率 ≥20%、数据接口在 1 个实验室完成试点。")
h3("关键资源依赖与替代方案")
table(["关键资源", "主要来源", "替代方案（若中断）"], [list(x) for x in D.SUSTAIN_DEP], [4.4, 5.2, 7.4], 8.5)
h3("转化假设的验证方法（V2.0 新增，回应 F-06；三条假设已验证/已提交）")
table(["转化假设", "最小成本验证方式", "成立判据", "时限", "成本", "验证状态", "验证结果"],
      [list(x) for x in V2.TRANSFORM_VERIFY], [2.6, 3.6, 2.6, 1.4, 1.3, 1.5, 4.4], 7.5,
      row_fills={0: "E8F2EA", 1: "E8F2EA", 2: "FDF3DC"})
h3("评审意见逐条回应（V2.0 新增）")
table(["评审意见", "处理方式", "具体落地内容"], [list(x) for x in V2.RESPONSE_TO_REVIEW],
      [3.4, 1.8, 12.4], 8.5, row_fills={0: "E8F2EA", 1: "FDF3DC"})

h2("4.2　个人能力提升计划（成员分别撰写）")
for member in D.MEMBERS:
    h3(f"{member}")
    table(["项目", "内容"], CH4_PERSONAL[member], [4.4, 12.6], 8.5)

doc.add_page_break()
# ================= 附录 =================
h1("附录　三类核心证据索引与三可追溯说明")
cap("表 A-1　三类核心证据索引（过程性 ≥5 项 / 结果性 ≥3 项 / 认知性 ≥2 项）")
rows = []
for kind, key in [("过程性证据", "process"), ("结果性证据", "result"), ("认知性证据", "cognition")]:
    for i, e in enumerate(D.EVIDENCE[key]):
        rows.append([kind if i == 0 else "", e[0], e[1], e[2]])
table(["证据类型", "证据名称", "说明 / 可追溯性", "编号"], rows, [2.6, 4.4, 7.8, 1.2], 8.5)
para("引用对照：E-01~E-03 见第二章；E-07~E-11 见第一章；E-12~E-14 见第三章。", size=9.5, color=GREYT)
para("三可追溯：来源可查 × 过程可复现 × 结果可验证（E-07/E-09/E-10 均可追溯至原始文件）。", size=9.5, color=GREYT)

doc.add_page_break()
h1("附件一　《评审反馈清单》与 5Why 归因（第一阶段：课后 0–12 小时）")
cap("表 A-2　评审反馈清单（P0–P3 分级）")
table(["编号", "来源", "反馈原文（节选）", "归类维度", "优先级"], [list(r) for r in V2.FEEDBACK],
      [1.2, 3.0, 8.4, 3.2, 1.2], 8,
      row_fills={0: "FBE4E2", 1: "FBE4E2", 2: "FDF3DC", 3: "FDF3DC", 4: "FDF3DC", 5: "FDF3DC"})
para("分级：P0 结论将被推翻 / P1 可信度显著削弱 / P2 影响说服力 / P3 优化建议。", size=9, color=GREYT)
for who, title, chain in V2.WHY5_V2:
    h2(f"5Why 归因（{who}）：{title}")
    table(["环节", "内容"], [list(step) for step in chain], [2.2, 14.8], 8.5)

doc.add_page_break()
h1("附件二　定向证据补强方案（第二阶段：课后 12–36 小时）")
cap("表 A-3　证据补强方案设计表")
table(["质疑编号", "质疑内容", "所需补充证据类型", "补强方法", "预计成本"],
      [list(r) for r in V2.SUPPLEMENT], [1.4, 3.6, 2.4, 7.6, 2.0], 8)
para(V2.SUPP_COST, size=9.5, color=GREYT)
para("补强结果（10 条全部结项）：F-01 第 2 台复测（49℃ / 50℃）与同批 20 台一致性（极差 3℃）已完成；F-02 第 2 独立渠道落地 1 单 12 台意向、判据达成；"
     "F-03~F-05、F-07~F-10 已在 V2.0 内落地；F-06 三所高校访谈完成（2 所确认统一采购）。全部补强现金成本 ¥0、人力 40 人时。",
     size=9.5, color=GREYT)

# 回填字数
for p in doc.paragraphs:
    for r in p.runs:
        if "正文约 X 字" in r.text:
            r.text = f"正文约 {CNTP['n']} 字（不含附录/附件与表格；若计入表格内文字合计约 {CNT['n']} 字）"
doc.save(os.path.join(OUT, "仿真跑不队_磁吸焊接辅助手电_结题报告_V2.0.docx"))
print("正文字数（不含表格）：", CNTP["n"], " 含表格合计：", CNT["n"])
print("saved report docx")
