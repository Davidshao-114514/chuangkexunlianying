# -*- coding: utf-8 -*-
"""生成结题汇报 PPT V1.0（python-pptx）"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import data2 as D

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


def setrun(r, text, size=14, bold=False, color=DARK):
    r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = FONT
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {}); rPr.append(ea)
    ea.set("typeface", FONT)


def tb(slide, x, y, w, h, text, size=14, bold=False, color=DARK, align=PP_ALIGN.LEFT, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    for i, ln in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = spacing
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
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW); self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    def page(self, kicker, title, sub=None):
        s = self.prs.slides.add_slide(self.blank)
        self.n += 1
        rect(s, 0, 0, SW, 0.16, NAVY)
        tb(s, 0.55, 0.32, 10.4, 0.5, title, size=24, bold=True, color=NAVY)
        if kicker:
            tb(s, 0.55, 0.86, 9.6, 0.3, f"EntreComp「实际行动」映射：{kicker}", size=11.5, bold=True, color=GREEN)
        if sub:
            tb(s, 0.55, 1.16, 12.2, 0.34, sub, size=11, color=GREY)
        tb(s, 0.55, 7.09, 8.0, 0.26, f"{D.TEAM} · {D.PROJ} · 结题汇报", size=9, color=GREY)
        tb(s, 11.6, 7.09, 1.2, 0.26, str(self.n), size=10, bold=True, color=NAVY, align=PP_ALIGN.RIGHT)
        return s

    def table(self, s, x, y, w, headers, rows, colw, fsize=11, rowh=0.4, headh=0.4, row_fills=None):
        t = s.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y),
                               Inches(w), Inches(headh + rowh * len(rows))).table
        t.first_row = True
        total = sum(colw)
        for j, cw in enumerate(colw):
            t.columns[j].width = Emu(int(Inches(w) * cw / total))
        t.rows[0].height = Inches(headh)
        for i in range(len(rows)):
            t.rows[i + 1].height = Inches(rowh)
        for j, h in enumerate(headers):
            c = t.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = NAVY
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.02)
            c.text_frame.word_wrap = True
            p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            setrun(p.add_run(), h, size=fsize, bold=True, color=WHITE)
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                c = t.cell(i + 1, j)
                fill = LIGHT if i % 2 == 0 else WHITE
                if row_fills and row_fills.get(i):
                    fill = row_fills[i]
                c.fill.solid(); c.fill.fore_color.rgb = fill
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.02)
                tf = c.text_frame; tf.word_wrap = True
                for k, seg in enumerate(str(v).split("\n")):
                    p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                    p.alignment = PP_ALIGN.LEFT
                    setrun(p.add_run(), seg, size=fsize, color=DARK)
        return t

    def img(self, s, name, x, y, w=None, h=None):
        kw = {}
        if w: kw["width"] = Inches(w)
        if h: kw["height"] = Inches(h)
        return s.shapes.add_picture(os.path.join(OUT, name), Inches(x), Inches(y), **kw)

    def bullets(self, s, x, y, w, items, size=12.5, gap=0.08):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(5.4))
        tf = box.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
        first = True
        for it in items:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            if isinstance(it, tuple):
                lead, rest = it
                p.line_spacing = 1.18; p.space_after = Pt(int(gap * 72))
                setrun(p.add_run(), lead, size=size, bold=True, color=NAVY)
                setrun(p.add_run(), rest, size=size, color=DARK)
            else:
                p.line_spacing = 1.18; p.space_after = Pt(int(gap * 72))
                setrun(p.add_run(), "● ", size=size * 0.8, bold=True, color=GREEN)
                setrun(p.add_run(), it, size=size, color=DARK)
        return box

    def note(self, s, lines):
        s.notes_slide.notes_text_frame.text = "\n".join(lines)

    def build(self):
        # P1 封面
        s = self.prs.slides.add_slide(self.blank); self.n = 1
        rect(s, 0, 0, SW, SH, NAVY)
        rect(s, 0, 3.02, SW, 0.06, GREEN)
        tb(s, 1.0, 1.52, 11.3, 0.6, "创客竞赛作品结题汇报", size=38, bold=True, color=WHITE)
        tb(s, 1.0, 2.22, 11.3, 0.5, f"{D.PROJ} —— {D.TOPIC}", size=19, color=RGBColor(0xC9, 0xD6, 0xE6))
        tb(s, 1.0, 3.36, 11.3, 1.9,
           f"团队名称：{D.TEAM_FULL}\n"
           f"成员与角色（RACI-V）：邵子中 — 负责人 / 经济模型·固件·材料统筹（A）\n"
           f"　　　　　　　　　　　　李昊桐 — 焊接工艺·实测与可靠性（R）　姜亚楷 — B 端对接·财务监督（R）\n"
           f"汇报日期：{D.FINAL_DATE}　|　版本：结题汇报 PPT V1.0", size=14.5, color=WHITE, spacing=1.5)
        tb(s, 1.0, 5.72, 11.3, 0.9,
           "本次汇报以「实际行动」领域五项能力为线索，回答三个问题：\n"
           "① 从选题到结题经历了哪些关键挑战　② 采取了什么行动、动用了什么资源　③ 产生了什么可验证的成果与认知变化",
           size=12.5, color=RGBColor(0x9F, 0xB4, 0xCE), spacing=1.35)

        # P2 价值验证全景图 A
        s = self.page("计划与管理", "价值验证全景图（一）：三阶段核心指标轨迹",
                      "选题 → 中期 → 结题三节点连续变化 + 计划目标线（数据均可追溯至原始记录）")
        self.img(s, "图A_三阶段指标轨迹.png", 0.55, 1.62, w=12.2)
        rows = [["中期 vs 结题", "有效验证数据 157 → 312（＋98.7%）；任务完成率 50% → 78%（＋56%）；意向金支付率 32.3% → 37.3%"],
                ["计划 vs 实际", "达标 3 项（任务按时完成率 96%≥95%、温升 49℃≤60℃、NPS 42≥40）；未达 2 项（任务完成率 78%<85%、单位变动成本 ¥43.0>¥40）"],
                ["团队均值 vs 最优值", "任务完成率均值 78% vs 最优 92%（差 14pp）；单位变动成本均值 ¥43.0 vs 最优 ¥39.6（差 ¥3.4）；完成率均值 96% vs 最优 100%（差 4pp）"]]
        self.table(s, 0.55, 5.02, 12.2, ["三类对比", "关键数据（本期必须呈现）"], rows,
                   colw=[2.4, 9.8], fsize=10.5, rowh=0.58, headh=0.4)
        tb(s, 0.55, 6.92, 12.2, 0.3, "每项指标的验证方式与原始记录编号见本页附录（E-01 ~ E-14）。", size=10, color=GREY)
        self.note(s, ["仪表盘数据来源：中期汇报第 8 页仪表盘（2026-10-06）+ 结题阶段测试记录（2026-10-20）",
                      "三阶段并列呈现的目的：让评委看到趋势而非终点"])

        # P3 价值验证全景图 B
        s = self.page("计划与管理 + 体验式学习", "价值验证全景图（二）：计划 vs 实际、均值 vs 最优",
                      "执行偏差与能力分布——两项未达预期指标不回避")
        self.img(s, "图B_计划与实际对比.png", 1.87, 1.52, w=9.6)
        rows = [[p[0], p[1], p[2], p[3], p[4], p[5]] for p in D.PLAN_DEV]
        self.table(s, 0.55, 5.02, 12.2, ["指标", "计划（结题目标）", "实际", "偏差", "判定", "偏差归因"], rows,
                   colw=[2.4, 2.1, 1.4, 1.2, 1.9, 3.2], fsize=10, rowh=0.32, headh=0.34,
                   row_fills={0: RGBColor(0xFB, 0xE4, 0xE2), 1: RGBColor(0xFB, 0xE4, 0xE2)})
        self.note(s, ["未达预期两项均已给出归因与改进计划（见体验式学习页与可持续转化页）",
                      "决策说明：基于任务完成率未达标 → 决策为“先补引导，不加硬件功能”，避免用堆功能掩盖体验问题"])

        # P4 主动性 A
        s = self.page("主动性", "主动性——破局行动证明（一）：挑战识别与主动行动", None)
        ini = D.INITIATIVE
        tb(s, 0.55, 1.6, 5.9, 0.34, "① 挑战识别：三个关键障碍", size=13, bold=True, color=NAVY)
        self.bullets(s, 0.55, 2.02, 5.9, ini["obstacle"], size=11.5)
        tb(s, 6.75, 1.6, 6.0, 0.34, "② 主动行动：三项非常规措施", size=13, bold=True, color=NAVY)
        self.bullets(s, 6.75, 2.02, 6.0, ini["action"], size=11.5)
        rect(s, 0.55, 5.1, 12.2, 1.72, LIGHT)
        tb(s, 0.75, 5.2, 11.8, 1.5,
           "③ 行动成果（量化）：\n" + "\n".join(f"　· {x}" for x in ini["result"]) +
           "\n证据：招募登记表与测试记录（E-08）、迭代日志 No.14–No.17（E-01）、B 端交付验收单（E-10）",
           size=11.5, color=DARK, spacing=1.3)
        self.note(s, ["主动性的关键不是“加班”，而是不等指派、自己找替代路径：三项行动全部由团队成员自行发起"])

        # P5 主动性 B
        s = self.page("主动性", "主动性——破局行动证明（二）：行动前后的量化改变", None)
        rows = [["用户测试招募人数（2 天内）", "3 人", "22 人", "＋633%", "线下蹲点 + “10 分钟帮你发现 2 个问题”话术"],
                ["用户任务完成率", "50%", "78%", "＋28pp", "硅胶垫丝印档位刻度 + 说明书改“3 步开工卡”"],
                ["状态显示相关成本（状态灯）", "6 颗", "4 颗", "−¥0.4/台", "把被高估的卖点降级为说明书步骤，腾出成本与 20 人时"],
                ["B 端订单（首单）", "0 台", "22 台", "＋¥1,298 收入", "通过实验室老师牵线，以“实训课批量工具清单”方式对接"],
                ["千片 BOM 报价", "¥52.3（小批）", "¥37.6（千片）", "−28.1%", "B 端订单达成投模门槛后锁定注塑报价"]]
        self.table(s, 0.55, 1.72, 12.2, ["指标", "行动前", "行动后", "变化", "对应的主动行动"], rows,
                   colw=[3.0, 1.7, 1.7, 1.9, 4.5], fsize=10.5, rowh=0.62, headh=0.4)
        tb(s, 0.55, 5.3, 12.2, 1.4,
           "证据链：\n"
           "· 过程性：招募登记表与现场照片、迭代日志 No.14–No.17（含每日动作与时间戳）\n"
           "· 结果性：可用性测试观察记录（13 人次）、B 端交付验收单（22 台）、LCSC 与机构件千片报价单\n"
           "· 认知性：“被高估的卖点要敢于降级”这一洞察写入认知迭代日志第 6 条", size=11, color=DARK, spacing=1.3)
        self.note(s, ["“状态显示从卖点降级”是本轮最反直觉的主动决策：放弃一个看起来漂亮的卖点，换回成本与用户体验"])

        # P6 应对不确定性 A
        s = self.page("应对不确定性", "应对不确定性——风险熔断机制（一）：预设底线", 
                      "四条风险阈值在中期就写进计划，不是事后补写")
        rows = [[r[0], r[1], r[2], r[3]] for r in D.RISK]
        self.table(s, 0.55, 1.7, 12.2, ["风险项", "预设阈值（底线）", "是否触发", "触发后执行的备选方案"], rows,
                   colw=[2.1, 2.3, 2.4, 5.4], fsize=10.5, rowh=1.0, headh=0.42,
                   row_fills={0: RGBColor(0xFB, 0xE4, 0xE2), 2: RGBColor(0xFD, 0xF3, 0xDC)})
        rect(s, 0.55, 6.2, 12.2, 0.62, LIGHT)
        tb(s, 0.75, 6.3, 11.8, 0.5,
           "熔断规则：任一阈值触发即日冻结该条线的工作、24 小时内出备选方案；决策记录必须在协作工具中留时间戳，不允许口头决策。",
           size=11, bold=True, color=NAVY)
        self.note(s, ["风险阈值的设定依据：温升 60℃ 来自锂电与手部安全边界；单次试错 ¥500 来自 MVC 原则的 5 倍上限",
                      "两条触发记录均为真实事件，不是预案演练"])

        # P7 应对不确定性 B
        s = self.page("应对不确定性", "应对不确定性——风险熔断机制（二）：触发、执行与效果（含时间戳证据链）",
                      "以温升越线为主线，展示“预警 → 决策 → 回升”的完整链条")
        rows = [["预警（10-15 18:30）", "8 小时工况第 6 小时温升 61.5℃（超阈值 1.5℃）", "热电偶连续记录表第 12 个记录点（E-07）"],
                ["决策（10-15 21:40）", "判定触发安全熔断：当日冻结演示准备，集中 2 天改造；确定“安全优先于照度”原则", "熔断决策会议记录（含 21:40 时间戳，E-02）"],
                ["执行（10-16 ~ 10-18）", "驱动电流降 10%、铝基板 1.0→1.6mm、涂导热硅脂；同步复核用户对照度变化的接受度", "改造实物照片、改造清单、照度实测表"],
                ["效果（10-19 复测）", "8 小时工况最高温升 49℃（优于阈值 11℃）；照度 860→780 lux（−9.3%），12/13 人认为照度足够", "复测记录曲线（E-07）、可用性测试记录（E-08）"]]
        self.table(s, 0.55, 1.72, 12.2, ["环节（含时间戳）", "实际发生的事", "证据"], rows,
                   colw=[2.6, 5.8, 3.8], fsize=10.5, rowh=1.02, headh=0.4)
        tb(s, 0.55, 6.25, 12.2, 0.6,
           "熔断代价与收益：代价 = 2 天工期 + ¥210 物料；收益 = 避免了“连续 8 小时后外壳烫手”这一类致命安全质疑，"
           "并换来 8 小时工况 49℃ 的硬证据（安全性在评审中占 20% 权重）。", size=11, bold=True, color=NAVY)
        self.note(s, ["时间戳证据链：18:30 记录 → 21:40 决策 → 10-16~18 执行 → 10-19 复测，四个节点均可追溯到原始文件"])

        # P8 体验式学习 A
        s = self.page("体验式学习", "体验式学习——认知迭代图谱（一）：从失败到新认知的完整路径",
                      "两条链均为真实失败，不是“成长故事”")
        self.img(s, "图D_认知迭代图谱.png", 0.55, 1.6, w=12.2)
        self.note(s, ["图谱的四个环节缺一不可：失败事件（做了什么）→ 归因（为什么）→ 新认知（学到了什么）→ 新指标（改进了什么）",
                      "两条链的根因都落在方法层面而非资源层面，这是我们本轮最重要的自我诊断"])

        # P9 体验式学习 B
        s = self.page("体验式学习", "体验式学习——认知迭代图谱（二）：5Why 归因与新指标结果", None)
        rows = [[w[0], w[1]] for w in D.WHY5]
        self.table(s, 0.55, 1.68, 7.4, ["环节", "内容"], rows, colw=[1.5, 5.9], fsize=10, rowh=0.72, headh=0.38)
        tb(s, 8.15, 1.68, 4.6, 0.32, "三条关键认知升级", size=12.5, bold=True, color=NAVY)
        self.bullets(s, 8.15, 2.06, 4.6, [
            "态度 ≠ 行为：问卷 71.3% vs 意向金 37.3%，39→34 个百分点的落差让我们把指标换成行为口径",
            "功能跑通 ≠ 用户会用：验收标准从“功能状态”改为“用户行为指标”，任务完成率成为核心指标",
            "测试必须逼近真实工况：建立“最长工况（8 小时）+ 最差环境（下午 3 点靠窗）”双最测试标准",
        ], size=10.5)
        rect(s, 0.55, 5.62, 12.2, 1.2, LIGHT)
        tb(s, 0.75, 5.72, 11.8, 1.0,
           "新指标结果（可验证）：连续工况温升 61.5℃ → 49℃（优于阈值 11℃）｜任务完成率 50% → 78%（＋28pp）｜"
           "该步骤失败率 58.3% → 7.7%｜新增“双最测试标准”已写入后续每轮迭代的验收清单\n"
           "证据：5Why 原始记录（E-12）、认知迭代日志 9 条（E-13）、温升复测表（E-07）、可用性测试记录（E-08）",
           size=10.5, color=DARK, spacing=1.3)
        self.note(s, ["认知跃迁声明（每位成员一份，含量化偏差率）见结题报告第三章 3.4"])

        # P10 合作能力 A
        s = self.page("合作能力", "合作能力——敏捷协作看板（一）：RACI-V 动态分工与调整", 
                      "标注与中期相比的调整内容及调整原因")
        rows = [[r[0], r[1], r[2], r[3], r[5]] for r in D.RACI_V2]
        self.table(s, 0.55, 1.7, 12.2, ["任务 / 决策", "邵子中", "李昊桐", "姜亚楷", "与中期相比的调整及原因"], rows,
                   colw=[2.7, 1.0, 1.0, 1.0, 6.5], fsize=9.5, rowh=0.68, headh=0.4)
        tb(s, 0.55, 6.05, 12.2, 0.8,
           "V（志愿者 / 支持者）：实验室老师（连续工况测试的场地与安全指导）、上一届学长（模拟答辩评阅）。\n"
           "三处关键调整：B 端对接由姜亚楷接手（主渠道变化）；连续工况测试与引导优化两项任务从“灰色任务”明确到人；"
           "财务监督改为轮值，避免“谁建模谁管钱”。", size=10.5, color=DARK, spacing=1.3)
        self.note(s, ["动态调整的依据是任务状态看板：每周两日站会时按卡点重新分配 R，而非按原计划固守"])

        # P11 合作能力 B
        s = self.page("合作能力", "合作能力——敏捷协作看板（二）：成员贡献值与协作效能进化", None)
        self.img(s, "图C_贡献值.png", 0.55, 1.62, w=7.5)
        rows = [["任务难度系数", c[1], c[2], c[3], c[4]] for c in D.CONTRIB]
        self.table(s, 8.25, 1.62, 4.5, ["成员", "难度", "质量", "协作", "贡献值"], rows,
                   colw=[1.3, 0.8, 0.8, 0.8, 0.9], fsize=9.5, rowh=0.5, headh=0.36)
        self.table(s, 8.25, 3.45, 4.5, ["协作效能指标", "中期", "结题", "变化"],
                   [[e[0].split("（")[0], e[1], e[2], e[3]] for e in D.EFF_EVO],
                   colw=[2.2, 0.8, 0.8, 1.0], fsize=9, rowh=0.46, headh=0.36)
        rect(s, 0.55, 6.08, 12.2, 0.78, LIGHT)
        tb(s, 0.75, 6.18, 11.8, 0.6,
           "贡献值 = 任务难度系数 × 完成质量 × 协作系数。三人贡献值离散度（最高/最低）由中期 1.42 降至 1.08，"
           "差异缩小 24%——这是“轮值 PM + 卡点当日上报”机制的直接结果。", size=10.5, bold=True, color=NAVY)
        self.note(s, ["贡献值口径公开透明：难度系数由三人共同评定（1–5），完成质量取任务验收通过率，协作系数取互评均值"])

        # P12 资源杠杆率 A
        s = self.page("计划与管理", "计划与管理——资源杠杆率（一）：投入-产出效能核算",
                      "全周期投入、三类验证产出与效能值")
        rows = [[c[0], c[1], c[2]] for c in D.COST_IN] + [["总投入合计", f"¥{D.COST_TOTAL:,}（含外部资源估算价值）", "现金 ¥5,310 + 外部资源估值 ¥3,060"]]
        self.table(s, 0.55, 1.68, 6.1, ["成本类型", "具体项目", "金额 / 量化"], rows,
                   colw=[1.3, 3.4, 1.4], fsize=8.5, rowh=0.44, headh=0.36, row_fills={9: RGBColor(0xD9, 0xE2, 0xF3)})
        rows2 = [[o[0], o[1], o[2]] for o in D.OUT_PUT] + [["产出合计", "各类产出数量之和", f"{D.OUT_PUT_TOTAL} 项"]]
        self.table(s, 6.85, 1.68, 5.9, ["产出类型", "具体项目", "量化"], rows2,
                   colw=[1.3, 3.2, 1.4], fsize=8.5, rowh=0.44, headh=0.36, row_fills={8: RGBColor(0xE6, 0xF2, 0xEA)})
        rect(s, 0.55, 5.62, 12.2, 1.24, LIGHT)
        tb(s, 0.75, 5.72, 11.8, 1.05,
           f"效能值计算：产出合计 {D.OUT_PUT_TOTAL} 项 ÷ 投入总成本 ¥{D.COST_TOTAL:,} × 100 = "
           f"{D.EFF_ALL:.2f} 项 / ¥100（含外部资源估算）；若只按现金投入 ¥5,310 计 = {D.EFF_CASH:.2f} 项 / ¥100\n"
           f"折算标准：经费为实际现金支出；工时按实际投入记录（全周期 {D.HOURS_TOTAL} 人时）；外部资源按校外市场价估算；"
           f"人力机会成本 ¥18,000 单独列示不计入现金投入。\n"
           "资源杠杆率：外部资源估值 ¥3,060 ÷ 获取它投入的 46 人时（折 ¥1,150）= 2.7 倍", size=10.5, color=DARK, spacing=1.3)
        self.note(s, ["产出计数口径：同一份问卷在“用户验证数据”只计 1 项，避免重复计数",
                      f"投入总成本 ¥{D.COST_TOTAL:,} = 现金 ¥5,310 + 外部资源估值 ¥3,060"])

        # P13 资源杠杆率 B
        s = self.page("计划与管理 + 主动性", "计划与管理——资源杠杆率（二）：关键资源置换案例与方法论", None)
        rows = [[r[0], r[1], r[2], r[3], r[4]] for r in D.RESOURCE_LEVER]
        self.table(s, 0.55, 1.7, 12.2, ["置换案例", "我们付出的（能力 / 时间）", "我们换到的（资源）", "杠杆率", "关键说明"], rows,
                   colw=[1.9, 2.9, 3.2, 0.9, 3.3], fsize=9.5, rowh=1.0, headh=0.4)
        rect(s, 0.55, 5.28, 12.2, 1.42, LIGHT)
        tb(s, 0.75, 5.38, 11.8, 1.25, D.LEVER_METHOD, size=11, color=DARK, spacing=1.35)
        self.note(s, ["杠杆率 = 置换获得资源的市场估值 ÷ 团队为此投入的成本（按 ¥25/人时折算）",
                      "最强案例：6 人时自学专利检索（¥150）替代市场价 ¥1,500 的代理检索，杠杆率 10.0"])

        # P14 可持续转化 A
        s = self.page("计划与管理 + 主动性", "可持续转化规划（一）：路径 A 项目延续规划",
                      "本作品已完成功能闭环与 22 台小批量试制交付，选择“项目延续”路径")
        rows = [[p[0], p[1], p[2], p[3]] for p in D.SUSTAIN]
        self.table(s, 0.55, 1.7, 12.2, ["规划维度", "核心内容", "行动能力映射", "证据呈现形式"], rows,
                   colw=[1.9, 6.8, 1.7, 1.8], fsize=10, rowh=1.12, headh=0.4)
        tb(s, 0.55, 6.05, 12.2, 0.85,
           "转化方向：市场化（C 端小批量 + B 端实训采买并行）+ 学术化（结构点申请实用新型专利 1 项）。\n"
           "关键判断依据：量产定价口径下保本销量 1,232 台 < 3 年 SOM 预期 3,100 台，商业闭环成立；B 端零获客成本是达成规模的关键路径。",
           size=10.5, color=DARK, spacing=1.3)
        self.note(s, ["路径选择依据：功能闭环完成 + 已有真实订单 → 属“成品/准成品”团队，故走路径 A"])

        # P15 可持续转化 B
        s = self.page("应对不确定性", "可持续转化规划（二）：关键资源依赖与替代方案", "每项依赖都配替代方案，体现风险意识")
        rows = [[d[0], d[1], d[2]] for d in D.SUSTAIN_DEP]
        self.table(s, 0.55, 1.72, 12.2, ["关键资源依赖", "主要来源", "替代方案（若中断）"], rows,
                   colw=[3.0, 4.0, 5.2], fsize=10.5, rowh=1.06, headh=0.42)
        tb(s, 0.55, 6.35, 12.2, 0.55,
           "风险意识说明：四项依赖中有两项（资金、渠道关系）是我们无法单独控制的，因此替代方案都指向“缩小规模但不断供”的降级路径，"
           "而不是“等资源到位再行动”。", size=10.5, bold=True, color=NAVY)
        self.note(s, ["替代方案的共同原则：先保住交付与验证能力，再谈规模"])

        # P16 三阶问答预判
        s = self.page("应对不确定性 + 体验式学习", "三阶问答预判页：3 个最尖锐问题与应对话术",
                      "问题全部来自项目自身薄弱环节（任务完成率未达标、数据可追溯性、验证方法论）")
        rows = [[f"{i+1}　{q[0]}", q[1], q[2], q[3]] for i, q in enumerate(D.QA3)]
        self.table(s, 0.55, 1.7, 12.2, ["# / 类型", "预判问题", "应对话术（含数据与证据）", "对应能力"],
                   rows, colw=[1.5, 2.9, 6.6, 1.2], fsize=9.5, rowh=1.6, headh=0.4)
        tb(s, 0.55, 6.75, 12.2, 0.4,
           "创业者三问自检结论：关键假设 = H-001（付费意愿，行为口径）；最低成本验证 = 1 元可退意向金（¥360 / 48h）；"
           "数据决策 = 行为口径 37.3% → 维持小批量 + 转 B 端放量。", size=10, color=GREY)
        self.note(s, ["三个问题分别对应“结果挑战 / 过程质疑 / 认知追问”，避免安全型问题"])

        # P17 三类核心证据索引
        s = self.page("体验式学习 + 合作能力", "三类核心证据索引页：过程性 / 结果性 / 认知性",
                      "结果性证据中 E-07 / E-09 / E-10 可追溯至原始记录")
        rows = []
        for kind, key, label in [("过程性证据（≥5 项）", "process", None),
                                 ("结果性证据（≥3 项，含可追溯原始记录）", "result", None),
                                 ("认知性证据（≥2 项）", "cognition", None)]:
            for i, e in enumerate(D.EVIDENCE[key]):
                rows.append([kind if i == 0 else "", e[0], e[1], e[2]])
        self.table(s, 0.55, 1.58, 12.2, ["证据类型", "证据名称", "说明 / 可追溯性", "编号"], rows,
                   colw=[2.6, 4.0, 4.6, 0.9], fsize=9, rowh=0.325, headh=0.34)
        tb(s, 0.55, 6.62, 12.2, 0.4,
           "可追溯至原始记录的关键验证数据：E-07 8 小时温升连续记录表、E-09 意向金收款记录、E-10 B 端交付验收单。",
           size=10, bold=True, color=NAVY)
        self.note(s, ["三类证据的划分依据：过程性 = 记录“怎么做的”；结果性 = 记录“产生了什么”；认知性 = 记录“学到了什么”"])

        # P18 附录
        s = self.page("—", "附录：证据清单、数据来源与三可追溯说明", "本页不计入正页页数")
        rows = [["工作用时台账（720 人时，分三阶段）", "飞书表格 + 每周站会记录", "2026-08-26 — 10-22"],
                ["现金支出记录（¥5,310）", "采购订单、打样结算单、打印发票", "2026-08-26 — 10-22"],
                ["外部资源估值（¥3,060）", "校外共享工坊与仪器租赁公开报价、咨询市场价", "2026-10-18"],
                ["8 小时连续工况温升记录（E-07）", "热电偶逐 30 分钟记录表（16 个点）", "2026-10-15 / 10-19"],
                ["可用性测试观察记录（E-08）", "现场观察表 13 人次（含失败步骤标注）", "2026-10-06 / 10-20"],
                ["1 元意向金收款记录（E-09）", "微信收款明细 + 邀请名单 + 退款记录", "2026-09-25 / 10-20"],
                ["B 端交付验收单（E-10）", "采购方签字验收单 + 交付清单 22 台", "2026-10-20"],
                ["BOM 三档询价（E-11）", "LCSC 批量价页面 + 3 家机构件报价单", "2026-09-25 起 30 天有效"],
                ["照片与视频证据（E-15）", "V1.0–V4.0 原型实拍、温升改造前后、演示录屏 3 分 40 秒", "2026-08 — 10"]]
        self.table(s, 0.55, 1.7, 12.2, ["数据 / 记录项", "来源（可查）", "采集时间"], rows,
                   colw=[4.4, 5.6, 2.2], fsize=10, rowh=0.5, headh=0.4)
        tb(s, 0.55, 6.85, 12.2, 0.4,
           "三可追溯：来源可查（文件 / 时间 / 样本量）× 过程可复现（方法 / 配额 / 剔除规则）× 结果可验证（原始记录与截图）。",
           size=10.5, bold=True, color=NAVY)
        return self.prs

    def save(self, name):
        path = os.path.join(OUT, name)
        self.prs.save(path)
        print("saved:", path)
        return path


if __name__ == "__main__":
    d = Deck(); d.build(); d.save(f"{D.TEAM}_{D.PROJ}_结题汇报PPT_V1.0.pptx")
