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

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREYT = RGBColor(0x66, 0x6E, 0x7A)
CNT = {"n": 0}
CNTP = {"n": 0}


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
        R(p, t, size=size, bold=bold, color=color, count=count)
        if count:
            CNTP["n"] += sum(1 for ch in t if not ch.isspace())
    return p


def h1(t):
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
para("创客竞赛作品结题报告", size=24, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6, count=False)
para(f"{D.PROJ} —— {D.TOPIC}", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, sa=18, count=False)
table(["项目", "内容"], [
    ["团队名称", D.TEAM_FULL],
    ["团队成员与角色", "邵子中（负责人，U202511546）：经济模型 / 固件 / 材料统筹　|　李昊桐：焊接工艺 / 实测与可靠性　|　姜亚楷：渠道与 B 端对接 / 财务监督"],
    ["选题名称与主题", f"{D.PROJ}（AI+OPC 能力范式）"],
    ["作品开发阶段", "准成品：核心功能闭环完整（磁吸—悬停—调光—状态—安全保护全链路），已完成 22 台小批量试制与交付、8 小时连续工况复测与同批一致性抽检；量产工艺与长周期使用数据按结题后迭代计划推进（见第四章 4.1）"],
    ["报告版本", "V1.0（课前版）　|　项目周期：" + D.PERIOD],
    ["日期", D.FINAL_DATE],
], [3.4, 13.6], 9.5, count=False)
para("", sa=6, count=False)
para("撰写分工：第一章、第四章由团队合写；第二章、第三章由成员分别独立撰写并署名。正文约 X 字（不含附录与表格）。",
     size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT, count=False)

doc.add_page_break()
# ================= 第一章 =================
h1("第一章　项目成果总览（团队合写）")

h2("1.1　项目情景分析")
para("项目针对狭小焊台上的手工焊接照明。三位成员都是该场景的真实使用者：负责人调测验证板时 17 个焊点返工 3 次；"
     "李昊桐用 49 元小夜灯凑合，灯头一碰就歪；姜亚楷工位桌面仅 0.8×0.6 米，台灯底座占去四分之一。")
para("价值假设由“场景观察 → 需求陈述”形成：选题阶段完成 126 份问卷与 3 份独立洞察记录，提炼出“焊点照明的近、稳、准三缺一”，"
     "三类现有灯具都无法同时满足。原始记录：极客原话“大灯照不到，小灯转天就歪，我干脆手拿着焊”；实训学生每焊 2–3 颗就要停下转板“找光”。")

h2("1.2　项目问题分析")
para("用同理心地图拆解用户处境：他们真正在意的是“这颗焊点能不能一次焊对”，而不是灯具的绝对亮度。痛点在行为上表现为反复中断——"
     "行为观察（5 人 × 3 天、15 次）记录到每次 20 分钟焊接平均 4.2 次“找光/转板”、2.6 次“挪灯/手扶”，13/15 次出现“灯头偏移后未复位”。"
     "5Why 追到：传统灯具都是“底座思维”，而焊台的真实需求是在垂直空间里被吸附固定。")
para("天使客户由此明确为：有课程强制焊接任务、每周焊接 ≥3 次、由实验室统一采购工具的电子类专业学生——既是高频使用者，"
     "也是 B 端采买的受益者（零获客成本、单笔 10 台起）。")

h2("1.3　项目定位与核心价值主张")
para("一句话定位：为高校电子类专业学生与 DIY 极客，解决狭小焊台“灯照不到、靠不住、要手扶”问题的磁吸万向焊接照明工具。")
para("核心价值主张：给焊接者一双腾出来的手——磁吸固定、万向悬停、无级调光，百元内可得（主线 65 元，对比专业工业灯 300 元+）。"
     "量化目标：① 单次焊接减少 4.2 次找光动作；② 焊接失败率由 50% 降至 20%；③ 任务完成率 ≥85%；④ 意向金支付率（行为口径）≥30%。")

h2("1.4　创新核算仪表盘（完整版）")
cap("表 1-1　创新核算仪表盘：选题 → 中期 → 结题三阶段（含三类对比）")
rows = []
for d in D.DASH:
    name, q1, q2, q3, plan, mean, best = d[0], d[1], d[2], d[3], d[4], d[5], d[6]
    rows.append([name, q1, q2, q3, plan, f"均值 {mean} / 最优 {best}"])
table(["指标", "选题时", "中期", "结题当前值", "计划（结题目标）", "团队均值 vs 最优值"], rows,
      [3.2, 1.6, 1.6, 2.0, 2.6, 3.0], 8.5)
para("三类对比：① 中期 vs 结题——验证数据 157→312、任务完成率 50%→78%、意向金支付率 32.3%→37.3%、NPS 30→42；"
     "② 计划 vs 实际——达标 3 项、未达 2 项（完成率 78%<85%、成本 ¥43.0>¥40），归因为“引导设计不足”与“物流渠道刚性”；"
     "③ 均值 vs 最优——完成率 78% vs 92%、成本 ¥43.0 vs ¥39.6、按时完成率 96% vs 100%。")
para("决策说明：【坚持】磁吸万向方案与安全底线（结构假设全部通过）；【调整】“状态显示”由核心卖点降级为说明书步骤"
     "（实测 25 分钟平均查询 1.6 次），验收标准由“功能状态”改为“用户行为指标”；【转型】商业模式由 C 端零售单品转为"
     "“B 端实训采买 + 套件引流 + C 端小而美”三源结构——依据是线上 LTV/CAC 仅 0.83，而 B 端零获客成本。")

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

h2("1.6　资源-价值总表")
cap("表 1-3　资源-价值总表（投入量与产出对应关系及转化效率）")
table(["资源类型", "具体项目", "投入量", "产出类型", "具体成果", "转化效率"],
      [["经费", "三阶段现金支出（打样、器件、机构件、验证、试制备料、演示物料）", "¥5,310", "验证数据", "312 项有效验证数据", "每 ¥17.0 = 1 项"],
       ["经费", "调研与测试礼品、支付通道备用金", "¥940", "行为数据", "43 份真实付费行为数据（含 20 份意向金）", "每 ¥21.9 = 1 份"],
       ["时间", "团队全周期工时（720 人时：168 + 336 + 216）", "720 小时", "验证数据", "312 项有效验证数据", "每 2.3 人时 = 1 项"],
       ["时间", "结题阶段追加工时（引导优化 + 温升改造 + 交付）", "216 小时", "产品成果", "V4.0 定稿版 + 修复 31 项缺陷", "每 6.2 小时 = 1 项产品成果"],
       ["外部资源", "实验室设备使用权、导师咨询、社团宣传位（估值）", "¥3,060", "认知突破", "5 个假设验证结论 + 9 条洞察 + 3 个决策转折点", "每 ¥175.8 = 1 项认知成果"]],
      [1.5, 4.6, 1.5, 1.4, 4.0, 2.0], 8)
para("效率换算：全周期投入 ¥8,370（现金 ¥5,310 + 外部资源估值 ¥3,060）、产出 376 项 → 每 ¥100 获得约 4.5 项可验证产出；"
     "只按现金计为 7.1 项/¥100。外部资源按校外市场价估算、估值偏高，故 4.5 项/¥100 属保守口径。")

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
para("贡献值 = 难度系数 × 完成质量 × 协作系数（难度系数三人共同评定 1–5 分，完成质量取验收通过率，协作系数取互评均值）；"
     "各成员计算过程见第二章“合作能力”一节的贡献值表。")

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

doc.add_page_break()
# ================= 第三章 =================
h1("第三章　认知跃迁与深度反思（成员分别撰写，各自署名）")
for member in D.MEMBERS:
    m = CH3[member]
    h2(f"3.{D.MEMBERS.index(member)+1}　{member}")
    h3("3.1　双栏反思对比表")
    table(["PPT 中的判断/结论", "支撑该判断的实际数据", "认知差异分析"], m["dual"], [5.4, 5.4, 6.2], 8.5)
    h3("3.2　5Why 根因分析")
    table(["环节", "内容"], m["why5"], [2.0, 15.0], 8.5)
    h3("3.3　GROW 模型总结")
    for g in m["grow"]:
        para(g[0] + "：" + g[1], size=10, indent=0.3)
    h3("3.4　认知跃迁声明（200 字以内）")
    p = para(m["leap"], size=10.5)
    para(f"（本声明 {sum(1 for ch in m['leap'] if not ch.isspace())} 字）", size=8.5, color=GREYT, count=False)
    h3("3.5　可持续衔接行动")
    table(["项目", "内容"], m["next"], [3.6, 13.4], 8.5)

doc.add_page_break()
# ================= 第四章 =================
h1("第四章　可持续转化与未来规划")
h2("4.1　项目成果转化路径（团队合写，场景一：成品团队）")
para("所选路径：市场化（C 端小批量与 B 端实训采买并行）+ 学术化（结构点申请实用新型专利 1 项）。依据：功能闭环完整、"
     "已完成 22 台试制交付、千片 BOM 已锁定；量产定价下保本销量 1,232 台 < 3 年 SOM 3,100 台，商业闭环成立。")
h3("短期（结题后 3 个月内）：关键行动与所需资源")
table(["关键行动", "预期产出", "所需资源", "资源来源"],
      [["完成注塑模具制作与首批 200 台试产", "首批 200 台合格品 + 注塑工艺文件", "模具定金 ¥3,000（已投）、试产费 ¥10,000", "学校创客空间小额资助 + B 端预付款"],
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
para("引用对照：E-01~E-03 见第二章；E-07~E-11 见第一章 1.4 / 1.5 / 1.6；E-12~E-14 见第三章 3.2 / 3.4。", size=9.5, color=GREYT)
para("三可追溯：来源可查（标注采集时间、方式、样本量）× 过程可复现（方法与剔除规则留档）× 结果可验证（E-07 温升连续记录、"
     "E-09 意向金收款记录、E-10 交付验收单均可追溯至原始文件）。", size=9.5, color=GREYT)

# 回填字数
for p in doc.paragraphs:
    for r in p.runs:
        if "正文约 X 字" in r.text:
            r.text = f"正文约 {CNTP['n']} 字（不含附录与表格；若计入表格内文字合计约 {CNT['n']} 字）"
doc.save(os.path.join(OUT, "仿真跑不队_磁吸焊接辅助手电_结题报告.docx"))
print("正文字数（不含表格）：", CNTP["n"], " 含表格合计：", CNT["n"])
print("saved report docx")
