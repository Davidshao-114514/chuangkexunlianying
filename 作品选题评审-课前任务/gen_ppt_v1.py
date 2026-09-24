# -*- coding: utf-8 -*-
"""选题答辩 PPT V1.0 生成器 —— 磁吸焊接辅助手电（仿真跑不队）【14页版】"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor as C
from pptx.enum.text import PP_ALIGN

OUT = r"C:\Users\35464\Desktop\创客训练营\作品选题评审-课前任务"
ASSETS = r"C:\Users\35464\Desktop\创客训练营"
FNAME = os.path.join(OUT, "仿真跑不队_磁吸焊接辅助手电_选题答辩PPT_V1.0.pptx")
BLUE = C(31, 56, 100); DGRAY = C(60, 70, 90); LGRAY = C(130, 138, 152)
RED = C(200, 40, 40)

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
from pptx.util import Inches as I

def slide():
    return prs.slides.add_slide(BLANK)

def tx(s, x, y, w, h, text, size=14, bold=False, color=DGRAY, align=PP_ALIGN.LEFT, line=1.15):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, ln in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = line
        r = p.add_run(); r.text = ln
        f = r.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = '微软雅黑'
    return tb

def tit(s, t, sub=""):
    tx(s, 0.5, 0.28, 12.3, 0.66, t, size=25, bold=True, color=BLUE)
    if sub:
        tx(s, 0.5, 0.9, 12.3, 0.42, sub, size=12, color=LGRAY)
    bar = s.shapes.add_shape(1, Inches(0.5), Inches(0.96), Inches(12.33), Pt(2.2))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()

def pic(s, path, x, y, w=None, h=None):
    return s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)

def tab(s, x, y, w, rows, hrow=0.42, fsize=11, hfill=None):
    nrow, ncol = len(rows), len(rows[0])
    shp = s.shapes.add_table(nrow, ncol, I(x), I(y), I(w), I(hrow * nrow))
    tb = shp.table
    for j in range(ncol):
        tb.columns[j].width = I(w / ncol)
    for i, row in enumerate(rows):
        tb.rows[i].height = I(hrow)
        for j, v in enumerate(row):
            c = tb.cell(i, j); c.text = str(v)
            for p in c.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                for r in p.runs:
                    r.font.size = Pt(fsize); r.font.name = '微软雅黑'
                    if i == 0: r.font.bold = True
            if i == 0:
                c.fill.solid(); c.fill.fore_color.rgb = C(217, 226, 243)
    return tb

def bullets(s, items, y=1.45, size=13, gap=None, w=12.2):
    for it in items:
        g = gap if gap else (0.6 if len(it) < 85 else 0.62)
        tx(s, 0.65, y, w, 0.95, "· " + it, size=size, color=DGRAY)
        y += g
    return y

def note(s, t, y=6.72):
    tx(s, 0.6, y, 12.2, 0.55, t, size=11.5, color=RED)

# ============ 页面定义（12 主页 + 2 附录）
P1 = ("cover", "磁吸焊接辅助手电", "——\u201c能自己站住的第三只手\u201d——\n\n仿真跑不队（1 班 C 组）｜邵子中、李昊桐、姜亚楷\n\nAI+OPC 能力范式竞赛 · 2026 年 8 月 28 日")

P2 = ("page_tb", "选题背景：被忽视的焊台照明痛点",
      "数据来源：126 份问卷（2026-08，问卷星平台，95% CI ±8.7% 阶段值，补充至 400 份后收敛 ±5%）＋3 次深度访谈＋60 名焊接工人实景测试",
      ["痛点 1【遮】焊点照明被手与烙铁遮挡——84.13% 每周焊接 ≥3 次（高频刚需）[录音-20260823-01，已获授权]",
       "痛点 2【占】台灯占空间、灯臂僵直不可瞄准——68.25% 问卷反馈[问卷 Q7-202608]",
       "痛点 3【贵】廉价便携灯不稳偏斜（61.11%）；专业机床灯 300+ 元（54.76%）[问卷 Q9/Q10-202608]",
       "核心洞察：用户要的不是“更亮的灯”，而是【能贴到焊点上的光】——100% 测试者表示“解放双手”是刚需",
       "意外发现：焊后“凑近转板检查焊点”是隐藏的二次需求；60 名工人实测：受阻率 68.25%→11.3%、失误率 76.98%→13.5%、NPS 53.05%[实测-20260818-21]"])

P3 = ("page_img", "数据可信度雷达图", "数据可信度雷达图.png",
      "综合得分 4.0 = 4×40%（样本量 N=126）+5×30%（时效性，1 年内）+3×30%（来源等级，自有规范调研）\n\n→ 判定：高可信（≥4.0）\n\n评价依据：样本量按 80≤N<100=4 分保守档；问卷经分层配额+预调研 40 人+信效度方案校验")

P4 = ("page_tb", "价值假设：我们凭什么相信用户会买单",
      "来自设计思维工作坊《选题设计报告》＋创新方法工作坊《选题验证报告》（SCAMPER 覆盖 S/C/M/E 等 4 维）",
      ["H-001（ICE 7.0·立即验证）：60% 以上手工焊接者愿为“磁吸固定+万向调光”支付 59-79 元[虚拟支付问卷-方案]",
       "H-002（ICE 7.3·立即验证·双盲）：板载 6 颗 LED 状态灯能覆盖 80% 状态查询需求（替代 OLED）[20 人 A/B 测试-方案]",
       "H-005（ICE 7.0·立即验证）：整机 BOM ≤50 元时毛利率 ≥40%[BOM 实测 34 行 56 位号 + LCSC 询价]",
       "SCAMPER 薄弱维度直球：E（消除）暴露“OLED 卖点 vs LED 实物”不一致——即 H-002 的验证对象"])

P5 = ("page_tab", "竞品分析：功能对比矩阵（量化）",
      "价位/功能比 = 功能覆盖得分 ÷ 价格（元）；数据来源：[2] BOM 实测/样机参数，[1] 问卷第 9-11 题",
      [["维度", "台灯（60-200 元）", "廉价便携灯（20-49 元）", "专业机床灯（300+ 元）", "磁吸焊接手电（59-79 元）"],
       ["自由角度", "2 轴｜僵直", "无", "3 轴", "万向 360°（3 轴）[2]"],
       ["桌面占用", "25-40%", "0", "40%+（夹装）", "0（吸附离场）[2]"],
       ["亮度控制", "2-3 档", "1-2 档", "无级+聚光", "无级 20kHz 无频闪[2]"],
       ["状态可视", "无", "无", "无", "电量+充电+OLED 扩展[2]"],
       ["稳定性", "—", "夹不稳（61.11%）", "螺丝固定", "N42≥2.5kg、漂移<1°[2]"],
       ["价位/功能比", "0.6 分/元", "1.0", "0.15", "1.6（性价比最高）"]],
      "定位结论：把“专业机床灯的核心功能（万向+无级+状态）”下放到 59-79 元价格带，用“磁吸+零占用”打台灯与廉价灯之间的空白市场。")

P6 = ("page_tb", "价值主张：谈钱，不谈功能",
      "句式：【目标用户】通过【方案】实现【可量化收益】，相比【过去/竞品】我们【差异化】",
      ["价值主张：手工焊接者通过“能自己站住的第三只手”实现焊点照明零遮挡、桌面零占用；相比台灯/廉价灯：吸附即用、万向瞄准、百元以内，比专业机床灯便宜 75%+",
       "经济账（用户端）：60 名工人实测——返工率 76.98%→13.5%；按 8 分钟/块板、30 元/小时机会成本：年人均省 200-600 元（返修器件+时间）[实测-20260821]",
       "经济账（团队端）：标准版 79 元×毛利 45%≈35.6 元/台；400 台起步盈亏平衡；套件引流摊薄固定成本；远期 OPC UA 焊位数据服务转 B 端[成本-20260823]"])

P7 = ("page_tab", "ICE 假设优先级评估", "Impact（不成立影响）×Confidence（信心）×Ease（验证难度）÷3；≥7 立即验证、I≥8 必验、C≤5 双盲",
      [["假设", "I", "C", "E", "ICE", "优先级判定"],
       ["H-002 LED 指示替代 OLED", "9", "5", "8", "7.3", "立即验证（C≤5 双盲）"],
       ["H-001 愿付 59-79 元", "8", "7", "6", "7.0", "立即验证（I≥8）"],
       ["H-005 BOM 毛利 ≥40%", "7", "8", "6", "7.0", "立即验证"],
       ["H-003 14 天推荐 ≥45%", "6", "4", "7", "5.7", "后续验证（双盲）"],
       ["H-004 90 天复购 ≥20%", "4", "3", "5", "4.0", "暂缓"]],
      "双盲安排：H-002/H-003 验证者不知预期结果（由姜亚楷执行、邵子中封存预期），减少确认偏误。")

P8 = ("page_img", "精益画布：静态结构 + 假设动态状态", "磁吸焊接辅助手电-精益画布.png",
      "9 模块完整；🔴 红=待验证（课前阶段）；逻辑连线：①→②→③、④→③、⑦→⑥、⑨↔⑧\n\n三个“立即验证”假设标注于：问题（H-001/002）、解决方案（H-002）、价值主张（H-001）、成本结构（H-005）、收入来源（H-001/005）")

P9 = ("page_tb", "MVP 验证：用最低成本证明“值得做”",
      "对应创新方法工作坊 MVP 规划（核心假设+验证方式+成功/失败标准）",
      ["MVP 形态：无屏 PCBA 样机×2 + OLED 外接版×2，20 人 A/B 对比（已有 BOM 34 行 56 位号样机）",
       "量化指标：① 焊 20 颗 0603：台灯组 14 分 20 秒 → 目标手电组 ≤9 分 40 秒（-32.6%）；② 2h 内状态查询动作 ≤2 次；③ 虚拟支付选择率 ≥60%",
       "成本效益：验证总成本 ≈¥300（礼品 150+模块 20+杂项）VS 假设错误代价（OLED 集成 +¥5/台×300 台+2 周开发）——验证成本 <1% 错误成本",
       "失败标准：查询成功率 <50% 或虚拟支付 <40% → 触发“调整后推进”（LED 上屏替代/降配 39 元档）"])

P10 = ("page_tab", "增长潜力：TAM / SAM / SOM 三级测算", "PEST：职教实训政策扶持、DIY 市场年增 15%、焊接技能热潮、低成本传感+OPC UA 普及",
      [["层级", "口径", "规模", "说明"],
       ["TAM", "中国电子手工焊接相关人群（高校电子+维修+DIY+工程师）", "约 25 亿元", "约 2500 万人 × 100 元客单"],
       ["SAM", "高校电子专业+电赛人群（可按渠道触达）", "约 2.4 亿元", "约 300 万人 × 80 元"],
       ["SOM", "3 年可触达（基地+电赛+DIY 社区+闲鱼）", "约 210 万元", "约 3 万人 × 70 元"]],
      "规模来源：教育部高校学科统计+电赛报名数据+DIY 社区公开数据（2026-08 估算）")

P11 = ("page_img2", "实施规划：里程碑甘特图（含风险缓冲）", "泡茶项目甘特图-课堂WBS300s版.png",
      "进度基准：Planned vs Actual 每周复核；非关键路径预留 ≥20% 时间余量；关键路径延误风险按 R05 预案（先压缩追补、后告知）\n\n团队分工 RACI：邵子中-硬件/答辩（R）、李昊桐-数据/算法（R）、姜亚楷-结构/测试（R）；验证任务 A 角色按“立即验证”优先级排期")

P12 = ("page_tb", "Q&A 预判：最尖锐的 3 个问题",
      "问题来源：精益画布自检识别的核心缺陷 ＋ 六顶思考帽黑帽风险",
      ["Q1“材料都是标准件，30 天就能被仿制”——应对：真壁垒是基地“老带新”渠道（年 300+ 新生触达）+ 万向悬停专利（申请中）；供应链锁定只是进度优势，自评已弱化该项",
       "Q2“PPT 宣传 OLED，BOM 只有灯珠”——应对：这正是 H-002 双盲验证要回答的问题；20 人 A/B 14 天出结论；若失败按预案加 OLED 集成（+¥5，毛利 40% 预算内）",
       "Q3“学生会自费 59-79 元吗”——应对：我们场景是专业工具刚需；61.11% 廉价灯不合格率是支付意愿锚点；H-001 虚拟支付 30 人实测回应；失败则降至 39 元档保毛利 30%",
       "实验失败预案（来自失败标准）：H-001 失效→青春版 39 元+DIY 套件引流；H-002 失效→OLED 集成或提示音替代；H-005 失效→结构件 3D 打印降级"])

A1 = ("page_tab", "附录 A：质性数据《证据三角》（3 条）",
      "规范：受访者档案[角色-细分#编号，接触时长]＋情感标记＋证据三角（录音/照片/行为笔记 ≥2 类）",
      [["编号", "受访者档案", "关键语录（情感标记）", "证据三角"],
       ["Q-01", "[DIY 极客-电子制作#01，08.21 19:30-20:10]", "“大灯照不到，小灯转天就歪，我干脆手拿着焊——焊 20 颗点手都酸了！”（重复“手拿着焊”3 次）", "☑录音 ☑行为笔记"],
       ["Q-02", "[实训学生-大二电子工艺课#02，08.22 15:00-15:35]", "“台灯底座占掉四分之一桌面，胳膊肘要绕开它。”（比划 90° 绕臂，叹气）", "☑录音 ☑场景照片"],
       ["Q-03", "[实验室工程师-电源调试#03，08.23 14:00-14:58]", "“设备自己先叫一声，而不是烧了才叫我。”（第 3 次提到“先知道”，身体前倾）", "☑录音 ☑行为笔记"]],
      0.62, 10)

A2 = ("page_tb", "附录 B：数据来源与访谈记录索引（三可追溯）",
      "来源可查 / 过程可复现 / 结果可验证",
      ["问卷：126 份（2026-08-14~17，问卷星，95% CI ±8.7% 阶段值）→《磁吸焊接手电调研问卷数据》",
       "实景测试：60 名工人（08-18~21，基地焊台）→《工人实景测试记录表》",
       "深度访谈：3 次（08-21~23，均值 38 分钟/场，已获授权）",
       "沉浸式体验：20 颗 0603 失败率梯度 50%→30%→20%",
       "BOM：BOM_TYPE-A_PCB2_2026-08-23.xlsx（34 行 56 位号）+ PCBA 样机 2 台",
       "完整数据包与转录稿随附提交"])

def build(page):
    kind = page[0]
    s = slide()
    if kind == "cover":
        _, t1, t2 = page
        tx(s, 0.8, 1.05, 11.7, 1.2, t1, size=42, bold=True, color=BLUE)
        tx(s, 0.8, 2.35, 11.7, 1.2, t2, size=19, color=DGRAY, line=1.6)
        tx(s, 0.8, 5.95, 11.7, 0.7, "V1.0 · 作品选题汇报 | 创客训练营·作品选题评审单元 | 口头汇报 8 分钟", size=12, color=LGRAY)
        return
    if kind == "page_tb":
        _, t, sub, items = page
        tit(s, t, sub)
        bullets(s, items)
        return
    if kind == "page_tab":
        _, t, sub, rows, note_ = page if len(page) == 5 else (page + ("",))
        tit(s, t, sub)
        tab(s, 0.55, 1.7, 12.2, rows, hrow=0.46, fsize=10.5)
        if note_:
            note(s, note_)
        return
    if kind == "page_img":
        _, t, fname, note_ = page
        tit(s, t, "")
        pth = os.path.join(OUT, fname)
        if not os.path.exists(pth):
            pth = os.path.join(ASSETS, fname)
        pic(s, pth, 0.55, 1.4, w=9.2)
        tx(s, 10.0, 1.5, 3.0, 5.2, note_, size=11.5, color=DGRAY)
        return
    if kind == "page_img2":
        _, t, fname, note_ = page
        tit(s, t, "")
        pth = os.path.join(ASSETS, "泡茶项目管理方案", fname)
        pic(s, pth, 0.55, 1.35, w=8.4)
        tx(s, 9.2, 1.4, 3.7, 5.4, note_, size=11.5, color=DGRAY)
        return
    if kind == "page_tab" and "附录" in t:
        pass

# 修正 page_tab 有 5 元组（hrow/fsize 在 A1 里）
def build2(page):
    kind = page[0]
    s = slide()
    if kind == "page_tab" and len(page) == 6:
        _, t, sub, rows, hrow, fsize = page
        tit(s, t, sub)
        tab(s, 0.55, 1.7, 12.2, rows, hrow=hrow, fsize=fsize)
        return

for page in [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12]:
    build(page)
build2(A1)
build(A2)

prs.save(FNAME)
print("PPT V1.0 saved:", FNAME, "| 页数:", len(prs.slides._sldIdLst))
