# -*- coding: utf-8 -*-
"""生成《作品演示测试表》（含演示方案、测试数据与迭代规划说明）"""
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
st.font.name = "微软雅黑"; st.font.size = Pt(9.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
st.paragraph_format.space_after = Pt(3); st.paragraph_format.line_spacing = 1.06
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.5); sec.top_margin = sec.bottom_margin = Cm(1.5)


def R(p, t, size=9.5, bold=False, color=None):
    r = p.add_run(t); r.font.name = "微软雅黑"; r.font.size = Pt(size); r.font.bold = bold
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    if color is not None: r.font.color.rgb = color
    return r


def para(t="", size=9.5, bold=False, align=None, sb=0, sa=3, color=None):
    p = doc.add_paragraph()
    if align: p.alignment = align
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    if t: R(p, t, size=size, bold=bold, color=color)
    return p


def h1(t):
    p = para(t, size=13.5, bold=True, sb=8, sa=5)
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "10"); e.set(qn("w:space"), "3"); e.set(qn("w:color"), "2C5AA0")
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
    para("", size=5, sa=1)


para("创客训练营 · “创客竞赛作品结题评审”单元", size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREYT)
para("作品演示测试表", size=17, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=6)
para(f"{D.TEAM_FULL}　|　{D.PROJ} —— {D.TOPIC}　|　{D.FINAL_DATE}", size=10.5,
     align=WD_ALIGN_PARAGRAPH.CENTER, sa=8)

h1("一、作品基本信息与演示方式确认")
table(["项目", "内容"], [
    ["团队 / 作品名称", f"{D.TEAM_FULL}　/　{D.PROJ}"],
    ["成员与角色", "邵子中（负责人，经济模型/固件/材料）：演示主讲与数据说明；李昊桐（结构/实测）：实物操作与安全测试说明；姜亚楷（渠道/财务）：答辩与测试表递交"],
    ["作品开发阶段", "准成品：核心功能闭环完整（磁吸固定—万向悬停—无级调光—状态指示—过温保护），已完成 22 台小批量试制与 B 端交付、8 小时连续工况复测（2 台）与同批 20 台一致性抽检；量产工艺与长周期使用数据按下方第五节迭代计划推进"],
    ["演示方式", "实物演示（非 MVP 替代演示）。现场演示时间 5 分钟内；无需《MVP 阶段演示替代说明》，迭代规划见本表第五节"],
    ["核心价值主张", "给焊接者一双腾出来的手：磁吸固定解放双手、万向悬停指哪照哪、无级调光适配光环境，百元内可得（主线 65 元）"],
], [3.4, 14.6], 9)
para(D.MVP_NOTE, size=8.5, color=GREYT)

h1("二、演示内容与流程（8 步 / ≤5 分钟，可复现）")
table(["#", "环节（时长）", "操作说明"], [list(x) for x in D.DEMO_FLOW], [0.8, 3.4, 13.8], 9)
para(D.DEMO_ALT, size=8.5, color=GREYT)

h1("三、演示测试数据记录表（现场逐项记录）")
table(["测试项", "判定标准", "测量方法（可复现）", "实测值", "结论"],
      [list(x) for x in D.DEMO_TEST], [2.6, 2.2, 6.2, 2.2, 1.8], 9,
      row_fills={i: "E8F2EA" for i in range(len(D.DEMO_TEST))})
para("数据可追溯说明：吸附力与光斑数据来自结题阶段实物实测（2026-10-19/20，弹簧秤 3 次取均值、卷尺与秒表各 5 次）；"
     "温升来自 8 小时连续工况连续记录表（E-07，16 个记录点）；状态查询耗时来自可用性测试 13 人次的现场观察记录（E-08）；"
     "续航来自满电连续点亮计时测试。以上原始记录随报告附录提交，现场可提供原件核对。", size=8.5, color=GREYT)

h1("四、测试条件与环境说明")
table(["项目", "说明"], [
    ["演示环境", "评委席前展示台（金属台面或磁性底板），环境光按常规教室照明；若演示台非金属材质，团队自带铁质底板（30×20cm）"],
    ["所需配置时间", "约 10 分钟（含设备就位、铁板固定、样机充电状态确认），低于 30 分钟门槛"],
    ["安全措施", "低压供电（18650 + Type-C，DW01 过充过放保护）；NTC 过温提示演示使用热风枪模拟，由李昊桐持握并保持 20cm 安全距离；桌面上不放置易燃物"],
    ["演示备用件", "V4.0 整机 2 台（1 台演示、1 台备用）+ V2.0 样机 1 台（对比用）；备用电池 2 节；弹簧秤/量角器/热电偶各 1 套"],
    ["不可控风险与对策", "若现场演示台无法固定或用例失败：立即切换备用机；若两台均失败，改播 3 分 40 秒演示录屏并现场做吸附力与调光两项动手环节"],
], [3.4, 14.6], 9)

h1("五、迭代规划（从当前阶段到完整量产原型）")
table(["阶段", "核心验证目标", "关键里程碑", "预期完成时间"],
      [["阶段一（结题后 1 个月）", "长周期使用可靠性：22 台交付样机回收 30 天使用日志，验证失效模式与温升稳定性",
        "回收 ≥25 份使用日志；任务完成率 ≥85%（“3 步开工卡”随首单发货后）", "2026-11-20"],
       ["阶段二（结题后 3 个月）", "量产工艺可行性：注塑外壳与双色注塑磁吸垫的小批量良率",
        "200 台试产良率 ≥95%；单位变动成本 ≤¥40（物流集包协议落地）", "2027-01-20"],
       ["阶段三（结题后 6–12 个月）", "规模与商业化闭环：B 端实训课采买放量至保本销量",
        "累计销量 ≥1,232 台（量产定价保本点）；B 端占比 ≥45%", "2027-06-30"]],
      [3.4, 6.4, 6.2, 2.0], 9)

h1("六、团队签字与评委记录区")
table(["团队确认", "邵子中：______　　李昊桐：______　　姜亚楷：______　　日期：2026 年 10 月 22 日"],
      [["现场演示记录", "评委意见：\n\n\n\n签字：________________　　日期：____________"]],
      [17.6], 9)

f = os.path.join(OUT, "仿真跑不队_磁吸焊接辅助手电_作品演示测试表.docx")
doc.save(f)
print("saved:", f)
