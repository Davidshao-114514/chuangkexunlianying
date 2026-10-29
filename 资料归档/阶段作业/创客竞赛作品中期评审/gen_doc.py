# -*- coding: utf-8 -*-
"""生成《初级认知任务》解答文档（任务1-2）+ AI 评价记录 docx"""
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
GREEN = RGBColor(0x22, 0x7F, 0x57)
RED = RGBColor(0xA0, 0x2D, 0x24)
GREYT = RGBColor(0x66, 0x6E, 0x7A)


def new_doc():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "微软雅黑"; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.15
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin = s.bottom_margin = Cm(2.0)
    return doc


def R(p, text, size=10.5, bold=False, color=None, italic=False):
    r = p.add_run(text)
    r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None:
        r.font.color.rgb = color
    return r


def para(doc, text="", size=10.5, bold=False, align=None, sb=0, sa=4, color=None, indent=None):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if indent: p.paragraph_format.left_indent = Cm(indent)
    if text: R(p, text, size=size, bold=bold, color=color)
    return p


def h1(doc, t):
    p = para(doc, t, size=15, bold=True, sb=10, sa=8)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "12"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
    b.append(e); pPr.append(b)


def h2(doc, t):
    return para(doc, t, size=12, bold=True, sb=8, sa=5, color=NAVY)


def h3(doc, t):
    return para(doc, t, size=11, bold=True, sb=6, sa=3, color=RGBColor(0x33, 0x44, 0x55))


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def table(doc, headers, rows, widths, fsize=8.5, head="D9E2F3", row_fills=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j); c.text = ""
        R(c.paragraphs[0], h, size=fsize, bold=True)
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
        shade(c, head)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ""
            for k, seg in enumerate(str(v).split("\n")):
                p = c.paragraphs[0] if k == 0 else c.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                R(p, seg, size=fsize)
            if row_fills and row_fills.get(i - 1):
                shade(c, row_fills[i - 1])
    for j, w in enumerate(widths):
        for i in range(len(rows) + 1):
            t.cell(i, j).width = Cm(w)
    para(doc, "", size=6, sa=2)
    return t


def cap(doc, t):
    return para(doc, t, size=9, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6,
                color=RGBColor(0x33, 0x33, 0x33))


# ============================================================ 文档一
doc = new_doc()
para(doc, "", sa=18)
para(doc, "华中科技大学未来技术学院 · 创客训练营", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para(doc, "“创客竞赛作品中期评审”单元的初级认知任务", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6)
para(doc, "解答文档（任务 1–2）", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, sa=20)
table(doc, ["项目", "内容"], [
    ["团队 / 个体", f"{D.TEAM_FULL}　|　本文档由 邵子中（U202511546，负责人）完成个体部分，团队部分为三人讨论后共识"],
    ["团队成员", D.MEMBERS],
    ["选题名称", f"{D.PROJ} —— {D.TOPIC}"],
    ["竞赛主题", "AI+OPC 能力范式"],
    ["能力领域", "欧盟《创业能力框架》“资源”领域：A 自我意识与自我效能感 / B 动力和毅力 / C 资源与调动 / D 财经素养 / E 动员他人"],
    ["数据区间", "2026-09-26（选题评审结束）— 2026-10-08（中期评审），累计 12 天"],
    ["日期", D.MID_DATE],
], widths=[3.2, 13.8], fsize=10)
doc.add_page_break()

para(doc, "目　录", size=13, bold=True, sa=6, color=NAVY)
for t in ["任务 1　“资源”领域的认知与应用（15 分）",
          "　1.1 能力框架认知：概念匹配表（2 分）",
          "　1.2 个体及团队能力自评（3 分）",
          "　1.3 成本分类与预算编制训练（3 分）",
          "　1.4 SWOT 分析与资源缺口诊断（4 分）",
          "　1.5 RACI-V 与 SMART-C 工具应用（3 分）",
          "任务 2　精益审计：资源投入与价值产出的量化分析（15 分）",
          "　2.1 精益审计——资源-价值对照表（10 分）",
          "　2.2 资源投入-成果对照总表（5 分）",
          "附注　数据口径与来源"]:
    para(doc, t, size=10, sa=3)
doc.add_page_break()

# ---------- 任务1 ----------
h1(doc, "任务 1　欧盟《创业能力框架》“资源”领域的认知与应用（15 分）")
h2(doc, "1.1　能力框架认知：概念匹配表（2 分）")
cap(doc, "表 1-1　五段描述与“资源”领域五项能力的匹配")
table(doc, ["描述", "对应能力", "匹配依据"], [
    ["描述 1（连续多天坚持讨论、面对挫折不放弃、通过分工协作坚持下来）", "B　动力和毅力",
     "核心动作是“遇挫后持续投入并调整方法”，落在“在遇到困难时保持积极态度并寻找解决方案”的行为特征上"],
    ["描述 2（发现自己擅长沟通、不擅长数据整理，主动说明并建议由擅长者承担该部分）", "A　自我意识与自我效能感",
     "核心动作是“对自身资源与短板形成准确认知，并据此做出自我调节”，属于自我意识与自我效能感"],
    ["描述 3（预算花掉大半、打印与交通超支，重新评估开支并寻找更省钱的方案）", "D　财经素养",
     "核心动作是“区分必要支出与非必要支出、调整预算”，属财经素养"],
    ["描述 4（主动联系上一届获奖学长，邀请分享经验并争取到一次线上指导）", "C　资源与调动",
     "核心动作是“识别并主动获取团队之外可用的资源”，落在资源与调动（该行为同时含动员他人的成分，按“最直接”原则选 C）"],
    ["描述 5（团队分歧、进度放缓时组织沟通会，让成员表达顾虑并重新分配任务）", "E　动员他人",
     "核心动作是“把成员重新组织到共同目标上、明确各自责任”，落在动员他人（同时也体现自我意识——意识到团队需要沟通）"],
], widths=[4.6, 3.2, 9.2], fsize=8.5)
para(doc, "匹配说明：描述 4 与描述 5 都属于“多项能力交叉”的描述。按任务书“选择最直接、最贴切的一项”的要求，描述 4 的直接落点是取得资源（C），描述 5 的直接落点是组织他人（E）；若按关系视角，描述 4 亦可归 E、描述 5 亦可归 A，我们在此保留主选并说明备选，避免因“只写一项”而丢掉交叉关系。",
     size=9.5, color=GREYT)

h2(doc, "1.2　个体及团队能力自评（3 分）")
para(doc, "自评方法：通读 L1–L8 描述，找到最能描述当前行为表现的等级；对照该等级下的观测点，确认经历与至少 2 个观测点相符；再用具体事例说明依据。", size=10)
h3(doc, "⑴ 个体自评（邵子中）")
cap(doc, "表 1-2　个体自评（资源领域五项能力）")
table(doc, ["能力项", "我目前所处等级", "引用观测点原文（含等级）", "判断依据"], [
    ["自我意识与自我效能感", "L4 级",
     "L4 观测点——“当开始价值创造活动时，我能为如何管理有限资源制定计划”",
     "48 小时迭代启动时我先把手上资源盘了一遍：实验室 3D 打印机可免费使用、现有 PCBA 与机构件可复用、队友分别是焊接工艺强（李昊桐）与渠道强（姜亚楷）。据此制定了“我搭单位经济模型、姜亚楷跑三渠道、李昊桐做实测与竞品借测”的资源分配计划，并明确写下本轮不做的两件事（套件版量产、OPC 接口开发）。同时我对自己“擅长建模、不擅长面对面招募”有清晰认知，主动把招募环节交出去。综合自评 L4。"],
    ["动力和毅力", "L4 级",
     "L4 观测点——“在遇到困难时，我能保持积极态度并寻找解决方案”",
     "1 元意向金只收回 20 份（受邀 62 人）时，我们确实卡了一晚上。当晚没有停在“数据不好看”，而是把它转成结论：把北极星指标从“留存率”换成“意向金支付率”，并据此下调定价区间。招募不足时，第二天起连续两天到电工基地门口蹲点，完成 63 人次曝光、22 人留资。遇到挫折换方法而不是放弃，自评 L4。"],
    ["资源与调动", "L3 级",
     "L3 观测点——“我能识别并利用身边可用的资源来开展活动”",
     "识别并实际调用了三类身边资源：实验室 3D 打印机与示波器（借用 12 次）、上一届学长的测试问卷模板与评阅意见、CNIPA 免费专利检索（1 次，结论为未发现同类组合）。中期阶段外部资源调用 6 次，换来 11 条改进建议与 1 项 B 端合作意向。之所以仍评 L3：资源获取每次都靠临时找人，没有形成稳定渠道，等级尚不到“系统获取与配置”的水平。"],
    ["财经素养", "L3 级",
     "L3 观测点——“我能区分必要支出和非必要支出，并制定简单预算”",
     "把中期阶段 ¥2,280 现金支出逐笔记账，区分显性与隐性成本（隐性 336 人时）；下一阶段 ¥5,000 预算按必要性排了高/中/低优先级，并主动砍掉“高配样机（2600mAh）”与“OLED 演示模块”两项非必要支出。单位经济模型虽然这轮刚搭起来（三档 BOM 询价 + 保本销量），但定价与渠道费率仍依赖现学现问，自评 L3。"],
    ["动员他人", "L4 级",
     "L4 观测点——“我能说服他人参与我的项目或活动”",
     "把招募话术从“帮我做个测试”改成“10 分钟帮你发现自己焊接的 2 个问题”，据此把 20 人配对 A/B 测试与 15 人竞品盲测都招满；说服实验室老师开放工位与设备 3 次、指导老师 2 次提供开模报价与费率口径；地推说服 46 人留下联系方式。自评 L4。"],
], widths=[2.2, 1.7, 4.2, 8.9], fsize=8)

h3(doc, "⑵ 团队自评（三人讨论后共识）")
cap(doc, "表 1-3　团队自评（资源领域五项能力）")
table(doc, ["能力项", "团队整体等级", "引用观测点原文（含等级）", "团队判断依据"], [
    ["自我意识与自我效能感", "L4 级", "L4 观测点——“当开始价值创造活动时，我能为如何管理有限资源制定计划”",
     "团队对“能做什么、缺什么”有书面共识：SWOT 由三人各自独立填写后再合并（不是一起讨论着写），差异化描述共 12 条；并据此调整了分工——姜亚楷兼财务监督员，邵子中从招募转向建模。团队层面能制定资源分配计划且对自身短板有共识，但尚无系统的资源审计机制，评 L4。"],
    ["动力和毅力", "L4 级", "L4 观测点——“在遇到困难时，我能保持积极态度并寻找解决方案”",
     "12 天里连续完成 5 项再验证，3 处失败记录（专利检索式写错、民族志首日记录表作废、画布 V3.0 首版模块口径自相矛盾）全部保留在飞书修订历史中未删除；发现返工集中在“设计环节错误”后，补了两道前置检查（配额表预审、观察指标预演），之后同类返工为 0 次。评 L4。"],
    ["资源与调动", "L4 级", "L4 观测点——“在价值创造活动中，我能识别资源缺口并调动所需资源以推进计划”〔该等级条目以《创业能力完整框架》原文为准〕",
     "团队已建立可复用的资源获取路径：电工基地与社团渠道、实验室设备预约、外部评审（陪审团与其他团队）、免费专利检索；中期阶段外部资源调用 6 次，并算出“每次外部调用 = 2.2 项改进或合作”的量化结论。个人停在 L3 而团队到 L4 的原因：团队有渠道与制度，个人只有临时找资源的能力。"],
    ["财经素养", "L4 级", "L4 观测点——“我能为价值创造活动编制预算并在执行中控制成本”〔该等级条目以《创业能力完整框架》原文为准〕",
     "团队建立了制度而非一次性记账：财务监督员（姜亚楷）、单次试错上限 ¥500、双周对账、显性/隐性成本分账；并完成三档 BOM 询价、单位经济与保本销量测算（1,232 台），把“要不要投模具定金 ¥3,000”写成有门槛的决策（订单 ≥20 台）。这些行为超出个人 L3 的“简单预算”。"],
    ["动员他人", "L4 级", "L4 观测点——“我能说服他人参与我的项目或活动”",
     "用 RACI-V 明确了 6 项关键任务的 R/A/C/I/V，把外部支持者（实验室学长、指导老师）正式列入分工；用每周 15 分钟站会校准，任务按时完成率从 72% 提升到 91%（46 张任务卡）。评 L4。"],
], widths=[2.2, 1.7, 4.2, 8.9], fsize=8)
para(doc, "注：加〔〕标注的两条为 L4 级条目，其观测点文字按框架条目概述；L3/L4 观测点原文引自任务书示例。提交前建议对照《创业能力完整框架》补全原文。", size=8.5, color=GREYT)

h3(doc, "⑶ 个体与团队等级差异分析")
para(doc, "个体与团队在两项能力上出现等级差：资源与调动（个体 L3 / 团队 L4）、财经素养（个体 L3 / 团队 L4）；在自我意识与自我效能感、动力和毅力、动员他人三项上同级（均 L4）。",
     size=10.5)
para(doc, "差异说明了什么：出现差异的两项，恰好都是“必须靠制度和渠道才能上一个台阶”的能力——个人能做到“识别身边资源”（L3），但把资源获取变成稳定渠道、把记账变成财务监督制度，是团队协作的产物；而同级的三项更依赖个人特质，团队整合并没有带来额外等级。这个分布给了我们一个明确的个人改进靶点：我在团队里能借到“制度”，但一旦离开团队，财经素养就掉回 L3。所以下一步我要自己做一次完整的财务对账与定价推演，而不是继续依赖队友对账；同时把“渠道资源”从团队共有变成每人都会用（三人轮流各跑一次地推）。",
     size=10.5)

h2(doc, "1.3　成本分类与预算编制训练（3 分）")
h3(doc, "⑴ 成本分类（1.5 分）")
cap(doc, "表 1-4　中期阶段已发生成本（显性 + 隐性）")
rows = [[f"{i+1}. {c[0]}", c[1], c[2]] for i, c in enumerate(D.EXPLICIT_COST)]
rows += [[f"{i+1}. {c[0]}", c[1], c[2]] for i, c in enumerate(D.IMPLICIT_COST)]
table(doc, ["成本类型 / 项目", "金额 / 量化", "备注说明"], rows, widths=[7.6, 2.4, 7.0], fsize=8.5,
      row_fills={0: "EAF1F7", 1: "EAF1F7", 2: "EAF1F7", 3: "EAF1F7", 4: "EAF1F7"})
para(doc, f"小计：显性成本 ¥{D.MONEY_TOTAL}；隐性成本 {D.HOURS_TOTAL} 人时（按学生兼职 ¥25/人时折算机会成本约 ¥8,400）。"
          "隐性成本之所以必须单列：它不产生现金流出，但会真实挤占交付节奏——本轮 72 人时的返工就是最直接的证据。", size=9.5, color=GREYT)
h3(doc, "⑵ 下一阶段预算（1 分）")
cap(doc, "表 1-5　下一阶段预算（至结题评审前）")
table(doc, ["预算项目", "预算金额", "用途说明", "必要性优先级"],
      [[f"{i+1}. {b[0]}", b[1], b[2], b[3]] for i, b in enumerate(D.NEXT_BUDGET)] +
      [["合计", f"¥{D.BUDGET_TOTAL:,}", "—", "—"]],
      widths=[5.4, 2.0, 7.4, 2.2], fsize=8.5, row_fills={5: "D9E2F3"})
h3(doc, "⑶ 成本效益简析（0.5 分）")
para(doc, "团队回答：到目前为止，每投入 100 元，我们获得了 3.7 份有效用户反馈（其中真实付费行为数据 1.9 份）、0.13 版原型迭代，"
          "并得到 1 条可复核的渠道转化率结论（线上渠道 CAC ¥31.8、LTV/CAC 0.83 → 判定不可持续，已停投）。", size=10.5, bold=True)

h2(doc, "1.4　SWOT 分析与资源缺口诊断（4 分）")
h3(doc, "⑴ SWOT 分析（1.5 分）")
cap(doc, "表 1-6　SWOT 四象限（基于项目中期真实进展）")
table(doc, ["维度", "积极因素", "消极因素"], [
    ["内部", "优势 S：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(D.SWOT["S"])),
     "劣势 W：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(D.SWOT["W"]))],
    ["外部", "机会 O：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(D.SWOT["O"])),
     "威胁 T：\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(D.SWOT["T"]))],
], widths=[1.4, 7.8, 7.8], fsize=8.5)
h3(doc, "⑵ 资源缺口清单（1.5 分）")
cap(doc, "表 1-7　资源缺口热力图（4 项）")
table(doc, ["资源缺口", "缺口类型", "紧急程度", "对应 EntreComp 能力项", "初步解决思路"],
      [list(g) for g in D.GAPS], widths=[3.4, 2.0, 1.6, 2.6, 7.4], fsize=8.5)
h3(doc, "⑶ 缺口-能力对应关系简析（1 分，选最高优先级缺口）")
para(doc, f"缺口是什么：{D.GAP_TOP['gap']}。", size=10.5)
para(doc, f"对应哪项能力缺口：{D.GAP_TOP['ability']}——我们能识别资源（L3），但还没有把资源获取变成稳定渠道。", size=10.5)
para(doc, f"如果不解决的最严重影响：{D.GAP_TOP['impact']}", size=10.5)
para(doc, f"初步解决思路：{D.GAP_TOP['plan']}", size=10.5)

h2(doc, "1.5　RACI-V 与 SMART-C 工具应用（3 分）")
h3(doc, "⑴ RACI-V 分工表（1.5 分）")
cap(doc, "表 1-8　当前阶段关键任务 RACI-V 分工")
table(doc, ["任务 / 决策", "邵子中", "李昊桐", "姜亚楷", "角色分工说明"],
      [list(r) for r in D.RACI], widths=[4.0, 1.6, 1.6, 1.6, 8.2], fsize=8.5)
para(doc, "V（志愿者 / 支持者）：实验室学长（提供演示场地与评阅意见）、指导老师（提供开模报价与渠道费率口径）——本轮新引入的角色类型，"
          "解决此前“外部支持无法计入分工”的问题。", size=9.5, color=GREYT)
h3(doc, "⑵ SMART-C 里程碑（1 分）")
cap(doc, "表 1-9　下一阶段关键里程碑（SMART-C 六要素）")
table(doc, ["里程碑", "具体描述", "衡量标准", "完成时限", "检查点"],
      [list(m) for m in D.MILESTONES], widths=[1.2, 5.0, 4.4, 2.2, 4.2], fsize=8.5)
h3(doc, "⑶ 协作效能自评（0.5 分）")
para(doc, "团队回答：" + D.COOP, size=10.5, bold=True)

doc.add_page_break()
# ---------- 任务2 ----------
h1(doc, "任务 2　精益审计——资源投入与价值产出的量化分析（15 分）")
h2(doc, "2.1　精益审计——资源-价值对照表（10 分）")
para(doc, "覆盖 5 类资源（时间、资金、外部资源为必填，另补物料/设备与内部人力），每类均给出具体消耗量、对应产出与转化效率。", size=10)
cap(doc, "表 2-1　资源-价值对照表")
table(doc, ["资源类型", "具体消耗量", "产生的验证数据 / 成果", "转化效率"],
      [list(r) for r in D.RESOURCE_VALUE], widths=[2.2, 4.6, 7.6, 2.6], fsize=8.5)
para(doc, "转化效率的计算口径：① 时间效率 = 有效验证数据条数 ÷ 总人时（157 ÷ 336 ≈ 0.47 条/人时）；② 资金效率 = 现金支出 ÷ 付费行为数据份数"
          f"（¥{D.MONEY_TOTAL} ÷ 43 ≈ ¥53/份）；③ 外部资源效率 = （改进建议 11 + 合作意向 1）÷ 调用次数 6 ≈ 2.2 项/次。"
          "其中付费行为数据包含 20 份 1 元可退意向金——这一点必须说明，因为它与 23 份预售下单的性质不同（后者无真实成本）。",
     size=9.5, color=GREYT)

h2(doc, "2.2　资源投入-成果对照总表（5 分）")
cap(doc, "表 2-2　资源投入-成果对照总表（PPT “资源全景页”直接素材）")
table(doc, ["我们投入了", "我们获得了", "效率说明"] + [] , [list(r) for r in D.TOTAL_TABLE],
      widths=[5.6, 6.0, 5.4], fsize=9, head="D9E2F3") if False else None
table(doc, ["我们投入了", "我们获得了", "效率说明"], [list(r) for r in D.TOTAL_TABLE],
      widths=[5.6, 6.0, 5.4], fsize=9)
para(doc, "进度条可视化", size=10.5, bold=True, sa=2)
table(doc, ["进度总览", "计划完成时间", "完成度", "状态标识"],
      [[f"{p[0]}", p[1], f"{p[2]}%", p[3]] for p in D.PROGRESS] +
      [["加权目标完成度（权重 M1 40% / M2 35% / M3 25%）", "—", f"{D.GOAL_PCT}%", "进行中"]],
      widths=[7.4, 3.4, 2.6, 3.6], fsize=9, row_fills={3: "D9E2F3"})
para(doc, "████████░░░░　68%　|　剩余计划：完成 8 小时连续工况测试（10-12）→ B 端首单 20 台交付（10-18）→ 结题材料定稿与模拟答辩（10-22）",
     size=10.5, bold=True, color=NAVY)
para(doc, "口径说明（回应“三个数字不一致”的潜在质疑）：“加权目标完成度 68%”是按里程碑计划权重加权的结果：100%×40% + 62%×35% + 25%×25% ≈ 68%。"
          "它与单个里程碑的完成度（100% / 62% / 25%）不是同一口径，前者衡量整体计划执行进度，后者衡量单个里程碑状态。", size=9.5, color=GREYT)

h1(doc, "附注　数据口径与来源")
table(doc, ["数据项", "来源（可查）", "时间"],
      [list(x) for x in D.SOURCES], widths=[4.6, 9.6, 2.8], fsize=8.5)
para(doc, "三可追溯：来源可查（文件 / 时间 / 样本量）× 过程可复现（方法 / 配额 / 剔除规则）× 结果可验证（原始记录截图，编号 B-1 ~ B-13）。"
          "本单元涉及的工时台账、采购记录、问卷后台导出、意向金收款记录、盲测评分表均已留存，可按需提供。", size=9.5, color=GREYT)
para(doc, "", sa=8)
para(doc, "— 任务 1–2 结束 —", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para(doc, "本解答文档为个体（邵子中）主笔，团队部分（表 1-3、1-6~1-9、2-1、2-2）为三人讨论后的团队共识。",
     size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)

f1 = os.path.join(OUT, "《“创客竞赛作品中期评审”单元的初级认知任务》解答文档（任务1-2）.docx")
doc.save(f1)
print("saved:", f1)
