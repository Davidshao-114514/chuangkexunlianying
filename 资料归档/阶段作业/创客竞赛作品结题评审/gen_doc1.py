# -*- coding: utf-8 -*-
"""生成《结题评审单元初级认知任务》解答文档（任务 1）"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import data2 as D

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = RGBColor(0x1F, 0x3B, 0x63)
GREYT = RGBColor(0x66, 0x6E, 0x7A)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "微软雅黑"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.15
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(2.0)


def R(p, t, size=10.5, bold=False, color=None):
    r = p.add_run(t); r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None:
        r.font.color.rgb = color
    return r


def para(t="", size=10.5, bold=False, align=None, sb=0, sa=4, color=None, indent=None):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if indent: p.paragraph_format.left_indent = Cm(indent)
    if t: R(p, t, size=size, bold=bold, color=color)
    return p


def h1(t):
    p = para(t, size=15, bold=True, sb=10, sa=8)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
    b.append(e); pPr.append(b)


def h2(t):
    return para(t, size=12, bold=True, sb=8, sa=5, color=NAVY)


def h3(t):
    return para(t, size=11, bold=True, sb=6, sa=3, color=RGBColor(0x33, 0x44, 0x55))


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


def cap(t):
    return para(t, size=9, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6, color=RGBColor(0x33, 0x33, 0x33))


# ---------------- 封面 ----------------
para("", sa=18)
para("华中科技大学未来技术学院 · 创客训练营", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para("“创客竞赛作品结题评审”单元的初级认知任务", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6)
para("解答文档（任务 1）", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, sa=20)
table(["项目", "内容"], [
    ["团队 / 个体", f"{D.TEAM_FULL}　|　个体部分由 邵子中（U202511546，负责人）完成，团队部分为三人讨论共识"],
    ["团队成员", "邵子中（负责人）、李昊桐、姜亚楷"],
    ["选题名称", f"{D.PROJ} —— {D.TOPIC}"],
    ["能力领域", "欧盟《创业能力框架》“实际行动”领域：A 主动性 / B 计划与管理 / C 应对不确定性 / D 合作能力 / E 体验式学习"],
    ["数据区间", "2026-08-26（选题评审启动）— 2026-10-22（结题评审），全周期 8 周"],
    ["日期", D.FINAL_DATE],
], [3.2, 13.8], 10)

doc.add_page_break()
h1("任务 1　欧盟《创业能力框架》“实际行动”领域的认知与应用（15 分）")

h2("1.1　能力框架认知：概念匹配表（2 分）")
cap("表 1-1　五段描述与“实际行动”领域五项能力的匹配")
table(["描述", "对应能力", "匹配依据"], [
    ["描述 1（发现留存率低于预期后主动联系流失用户访谈，并在一周内完成新版本迭代）", "A　主动性",
     "核心动作是“不等指令、自己发现问题并主动发起行动”，落在主动性；其中“一周内完成迭代”另含计划与管理的成分，按最直接原则选 A"],
    ["描述 2（制定完整路线图，含里程碑、资源评估与风险预案，并每周用甘特图追踪偏差）", "B　计划与管理",
     "核心动作是“分解目标、设定节点、跟踪偏差”，是计划与管理的标准行为"],
    ["描述 3（合作方临时撤回支持时立即启动备选方案，48 小时内完成替代渠道对接与资源重配）", "C　应对不确定性",
     "核心动作是“计划外变化发生时的备选方案与资源重配”，落在应对不确定性"],
    ["描述 4（双周轮值 PM 制，用 RACI-V 动态调整分工，任务按时完成率从 72% 提升至 91%）", "D　合作能力",
     "核心动作是“用机制与角色分工提升协作效能”，落在合作能力"],
    ["描述 5（第一次测试失败后用 5Why 追溯根因，重构 MVP 方案，第二轮留存率提升 40%）", "E　体验式学习",
     "核心动作是“从失败中归因并把经验应用到下一轮”，落在体验式学习"],
], [4.8, 3.0, 9.2], 8.5)
para("匹配说明：描述 1 与描述 3 都含“主动应对”的成分。判断标准是“触发源”——描述 1 的触发源是团队自己在数据里发现的问题（主动性），"
          "描述 3 的触发源是外部合作方撤资（应对不确定性）。按此标准确定主选，避免两项归类混淆。", size=9.5, color=GREYT)

h2("1.2　个体及团队能力自评（3 分）")
h3("⑴ 个体自评（邵子中，基于选题评审 → 结题评审全过程）")
cap("表 1-2　个体自评（“实际行动”领域五项能力）")
table(["能力项", "我目前所处等级", "引用观测点原文（含等级）", "判断依据"], [
    ["主动性", "L4 级", "L4 观测点——“当遇到阻碍时，我能主动寻找替代方案并采取行动”",
     "可用性测试前两天只招到 3 人时，我没有等老师给建议：当天改成线下蹲点，把话术从“帮我做测试”换成“10 分钟帮你发现自己焊接的 2 个问题”，"
     "第二天招到 22 人。另外我主动提出把“状态显示”从卖点降级为说明书步骤（放弃一个看起来漂亮的卖点），这在团队内部是有争议的决定，"
     "但我拿着“25 分钟平均查询 1.6 次”的数据先做了小范围验证再推动。遇阻碍自己找替代方案并落地，自评 L4。"],
    ["计划与管理", "L3 级", "L4 观测点——“我能将复杂任务分解为可执行的步骤，并设定明确的时间节点”（本项对照 L4 描述自评为 L3）",
     "我把结题阶段拆成“温升改造 / 引导优化 / B 端交付 / 材料准备”四条线，各自设了完成时间与验收标准，这部分做到了 L4；"
     "但 8 小时连续工况测试被排在“方便的空档”而不是“真实的时长”，导致首轮测试虽然按时做完却漏掉了核心风险——"
     "说明我的任务分解是按“工作量”而不是按“风险”排的，暴露出计划能力上的短板，因此综合自评 L3。"],
    ["应对不确定性", "L4 级", "L4 观测点——“当计划外的变化发生时，我能调整策略并采取行动”",
     "温升 61.5℃ 越线当晚（10-15 21:40）判定触发熔断，冻结演示准备、把 2 天全部投到改造；同时把“安全优先于照度”写成决策原则，"
     "照度损失 9.3% 也接受。计划外变化发生时能定阈值、定备选、定时间窗，自评 L4。"],
    ["合作能力", "L4 级", "L4 观测点——“在团队协作中，我能主动与他人沟通信息，确保任务衔接顺畅”",
     "把财务监督交给姜亚楷轮值（避免“谁建模谁管钱”），并把自己从“建模”转为“模型固化 + 交棒”；"
     "发现温升改造与交付排期冲突后，主动把交付验收的 A 角色让给姜亚楷并同步接口标准。主动沟通、主动让位，自评 L4。"],
    ["体验式学习", "L4 级", "L4 观测点——“我能从失败中总结经验，并将其应用于后续行动”",
     "两次失败（任务完成率 50%、温升 61.5℃）都做了 4 层以上的 5Why，并且把结论变成了制度："
     "“态度数据/行为数据”的区分写进后续所有结论的标注要求，“双最测试标准（最长工况 + 最差环境）”写进每轮迭代验收清单。"
     "经验不只停留在反思文档里，而是改了流程，自评 L4。"],
], [2.2, 1.9, 4.0, 8.9], 8)

h3("⑵ 团队自评（三人讨论后共识）")
cap("表 1-3　团队自评（“实际行动”领域五项能力）")
table(["能力项", "团队整体等级", "引用观测点原文（含等级）", "团队判断依据"], [
    ["主动性", "L4 级", "L4 观测点——“当遇到阻碍时，我能主动寻找替代方案并采取行动”",
     "三项破局行动全部由成员自行发起、没有人等指派：招募替代方案（线下蹲点）、卖点降级（状态显示改说明书步骤）、"
     "B 端渠道开拓（通过实验室老师牵线）。团队在“遇到阻碍时能否自己找路”这一观测点上表现稳定，评 L4。"],
    ["计划与管理", "L3 级", "L4 观测点——“我能将复杂任务分解为可执行的步骤，并设定明确的时间节点”（团队自评低于该等级）",
     "团队能把大目标拆成任务卡（结题阶段 62 张），按时完成率 96% 也达标；但两项未达预期指标（任务完成率 78%<85%、"
     "单位变动成本 ¥43.0>¥40）都源于计划分解按“工作量”而非“风险/依赖”排序——把 8 小时工况测试排进空档"
     "就是典型的“排得开但排错了”。团队自评 L3，不因为完成率好看而调高。"],
    ["应对不确定性", "L4 级", "L4 观测点——“当计划外的变化发生时，我能调整策略并采取行动”",
     "预先把四条风险阈值写进计划（温升、订单、招募、试错成本），其中两条真实触发（温升、招募），均在 24 小时内启动备选方案，"
     "并留下含时间戳的决策记录。团队具备“有底线、有备选、留痕迹”的应变机制，评 L4。"],
    ["合作能力", "L4 级", "L4 观测点——“在团队协作中，我能主动与他人沟通信息，确保任务衔接顺畅”",
     "结题阶段用 RACI-V 明确 6 项任务并完成 3 处角色调整，把两项“灰色任务”（连续工况测试、引导优化）明确到人；"
     "任务按时完成率 91%→96%、决策响应时间 3.5h→1.8h、贡献值离散度 1.42→1.08。协作从“各管一摊”走向“按任务状态动态协同”，评 L4。"],
    ["体验式学习", "L4 级", "L4 观测点——“我能从失败中总结经验，并将其应用于后续行动”",
     "两条失败链都走完了“失败 → 归因 → 新认知 → 新指标”四步，且结论落成了可检查的制度（双最测试标准、"
     "行为指标优先原则、说明书引导检查项）；失败记录在协作工具中单列一节、未做删除。评 L4。"],
], [2.2, 1.9, 4.0, 8.9], 8)

h3("⑶ 个体与团队等级差异分析")
para("个体与团队在四项能力上同级（主动性 L4、应对不确定性 L4、合作能力 L4、体验式学习 L4），唯一差异出在“计划与管理”："
     "个体 L3、团队 L3（双方都低于 L4）。", size=10.5)
para("差异说明：这个“没有差异”本身就是结论。计划与管理是本轮唯一没有达到 L4 的能力——个人和团队都卡在同一处，"
     "说明它既不是某个人的短板，也不是协作分工能补的，而是**方法层面的共同缺陷**：我们习惯按“工作量”拆任务，"
     "不习惯按“风险与依赖”排顺序，所以 8 小时工况测试被排进方便的空档，两项未达预期指标都由此而来。"
     "相比之下，主动性、应对不确定性、合作能力、体验式学习四项之所以都在 L4，是因为它们都有可依赖的机制"
     "（主动寻找替代方案的习惯、熔断阈值表、RACI-V 与站会、5Why 与双最测试标准）。这提示下一步的重点不是"
     "“谁再努力一点”，而是给计划环节补一套机制——我们已经在结题后的规划里加了“关键路径与最长工况优先排期”规则。",
     size=10.5)

h2("1.3　核心工具一：“问题-行动-证据”三阶验证模型（4 分）")
for i, m in enumerate(D.MODEL3, 1):
    h3(f"案例{i}：{m['name']}")
    cap(f"表 1-4.{i}　三阶验证案例卡（{m['name'].split('：')[0]}）")
    table(["阶段", "内容", "证据要求与原始记录"], [
        ["① 问题", m["problem"], m["problem_ev"]],
        ["② 行动", m["action"], m["action_ev"]],
        ["③ 证据", m["evidence"], m["evidence_ev"]],
    ], [1.6, 8.6, 6.8], 8.5, row_fills={0: "FBEAE8", 1: "FDF6E3", 2: "E8F2EA"})

h2("1.4　核心工具二：双期对比分析与能力进化评估（3 分）")
h3("⑴ 双期关键指标对比表（1.5 分，6 项指标 / 覆盖 3 个类别）")
cap("表 1-5　中期 vs 结题关键指标对比")
table(["类别", "关键指标", "中期状态", "结题状态", "提升率", "变化归因（对应的关键行动）"],
      [list(c) for c in D.COMPARE], [1.5, 3.4, 1.6, 1.6, 1.3, 7.6], 8.2)
h3("⑵ 能力进化诊断（1.5 分）")
for q in D.EVOLVE:
    para(f"{q[0]}：{q[1]}", size=10.5, bold=True, sb=4, sa=2)
    para(q[2], size=10, indent=0.4)

h2("1.5　核心工具三：投入-产出效能核算（3 分）")
h3("⑴ 投入成本核算（1.5 分）")
cap("表 1-6　全周期资源投入核算")
rows = [[c[0], c[1], c[2], c[3]] for c in D.COST_IN]
rows.append(["总投入合计", f"¥{D.COST_TOTAL:,}（含外部资源估算价值 ¥3,060）", "—", f"现金 ¥5,310 + 外部资源估算 ¥3,060；人力机会成本 ¥18,000 另列"])
table(["成本类型", "具体项目", "金额 / 量化", "备注说明"], rows,
      [1.6, 6.2, 2.2, 7.0], 8.5, row_fills={9: "D9E2F3"})
para(D.CONV_NOTE, size=9, color=GREYT)
h3("⑵ 验证产出核算与效能计算（1.5 分）")
cap("表 1-7　全周期验证产出核算")
rows = [[o[0], o[1], o[2], o[3]] for o in D.OUT_PUT]
rows.append(["产出合计", f"{D.OUT_PUT_TOTAL} 项", "各项产出数量之和", "投入总成本（引自上表）¥" + f"{D.COST_TOTAL:,}"])
rows.append(["单位投入产出效能", f"{D.EFF_ALL:.2f} 项 / ¥100", f"产出合计 ÷ 投入总成本 × 100 = {D.OUT_PUT_TOTAL} ÷ {D.COST_TOTAL:,} × 100",
             f"若只按现金投入 ¥5,310 计，效能值 = {D.EFF_CASH:.2f} 项 / ¥100"])
table(["产出类型", "具体项目", "金额 / 量化", "备注说明（来源）"], rows,
      [1.6, 6.4, 2.2, 6.8], 8.2, row_fills={8: "E8F2EA", 9: "D9E2F3"})
h3("⑶ 效能分析")
for q, a in D.EFF_ANALYSIS:
    para(q, size=10.5, bold=True, sb=4, sa=2)
    para(a, size=10, indent=0.4)

para("", sa=8)
para("— 任务 1 结束 —", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("说明：本解答文档的团队部分（表 1-3、1-4、1-5、1-6、1-7）为三人讨论后的团队共识；个体部分（表 1-2）由邵子中独立完成。",
     size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)

f = os.path.join(OUT, "《“创客竞赛作品结题评审”单元的初级认知任务》解答文档（任务1）.docx")
doc.save(f)
print("saved:", f)
