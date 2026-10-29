# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------- palette ----------------
C_DARK   = RGBColor(0x10, 0x2A, 0x43)
C_PRIM   = RGBColor(0x1F, 0x5F, 0x8B)
C_TEAL   = RGBColor(0x0F, 0x6E, 0x68)
C_ACCENT = RGBColor(0xE8, 0x79, 0x2B)
C_BG     = RGBColor(0xF4, 0xF6, 0xF8)
C_TEXT   = RGBColor(0x24, 0x32, 0x4C)
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY   = RGBColor(0x6B, 0x77, 0x85)
C_LGRAY  = RGBColor(0xE2, 0xE8, 0xEE)
C_RED    = RGBColor(0xC0, 0x39, 0x2B)
C_GREEN  = RGBColor(0x2E, 0x8B, 0x57)

FONT = "Microsoft YaHei"

SW, SH = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]

def add_slide():
    return prs.slides.add_slide(BLANK)

def rect(slide, x, y, w, h, fill, line=None, line_w=0.75, shadow=False, round_=False, radius=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE, x, y, w, h)
    if round_:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp

def set_font(run, size=14, bold=False, color=C_TEXT, name=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', name)

def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
            space_after=4, wrap=True, line_spacing=1.0):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for line in lines:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = line.get('align', align)
        para.space_after = Pt(line.get('space_after', space_after))
        para.space_before = Pt(line.get('space_before', 0))
        para.line_spacing = line.get('line_spacing', line_spacing)
        para.level = line.get('level', 0)
        for spec in line['runs']:
            r = para.add_run()
            r.text = spec[0]
            set_font(r, size=spec[1], bold=spec[2], color=spec[3])
    return tb

def multi_runs(line, size=14, bold=False, color=C_TEXT, highlight=None):
    """line: string -> one run"""
    return {'runs': [(line, size, bold, color if highlight is None else color)]}

# ============ reusable header for content pages ============
def content_header(slide, num, title, subtitle=None, accent=C_PRIM):
    rect(slide, 0, 0, SW, Inches(0.14), accent)
    # number badge
    b = rect(slide, Inches(0.55), Inches(0.45), Inches(1.0), Inches(0.62), accent, round_=True, radius=0.18)
    tf = b.text_frame
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = num
    set_font(r, 20, True, C_WHITE)
    textbox(slide, Inches(1.75), Inches(0.42), Inches(9.0), Inches(0.6),
            [{'runs': [(title, 27, True, C_DARK)]}])
    if subtitle:
        textbox(slide, Inches(1.78), Inches(1.02), Inches(11.0), Inches(0.4),
                [{'runs': [(subtitle, 13, False, C_GRAY)]}])
    return

def footer(slide, page, team="仿真实跑不队"):
    textbox(slide, Inches(0.55), Inches(7.15), Inches(6), Inches(0.3),
            [{'runs': [("磁吸焊接辅助手电 · " + team, 9, False, C_GRAY)]}])
    textbox(slide, Inches(12.3), Inches(7.15), Inches(0.6), Inches(0.3),
            [{'runs': [(str(page), 9, False, C_GRAY)], 'align': PP_ALIGN.RIGHT}])

def bullet(dots, size=13, color=C_TEXT, lead=None, lead_color=C_PRIM, space=6):
    runs = []
    if lead:
        runs.append((lead + "  ", size, True, lead_color))
    runs.append((dots, size, False, color))
    return {'runs': runs, 'space_after': space}

def statbox(slide, x, y, w, h, value, label, accent, sub=None):
    rect(slide, x, y, w, h, C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    rect(slide, x, y, w, Inches(0.11), accent)
    textbox(slide, x + Inches(0.15), y + Inches(0.22), w - Inches(0.3), Inches(0.6),
            [{'runs': [(value, 30, True, accent)]}])
    ly = y + Inches(0.82)
    textbox(slide, x + Inches(0.15), ly, w - Inches(0.3), h - Inches(0.9),
            [{'runs': [(label, 12, True, C_TEXT)]}])
    if sub:
        textbox(slide, x + Inches(0.15), ly + Inches(0.34), w - Inches(0.3), h - Inches(1.2),
                [{'runs': [(sub, 10, False, C_GRAY)]}])

# ================= SLIDE 1 — 封面 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_DARK)
# accent graphic
rect(s, Inches(0), Inches(6.9), SW, Inches(0.6), C_ACCENT)
rect(s, Inches(0.8), Inches(1.5), Inches(0.14), Inches(2.4), C_ACCENT)
textbox(s, Inches(1.2), Inches(1.45), Inches(11), Inches(1.0),
        [{'runs': [("创客竞赛选题验证 · 选题答辩", 16, False, RGBColor(0x9C,0xB3,0xC9))]}])
textbox(s, Inches(1.2), Inches(2.05), Inches(11.5), Inches(1.6),
        [{'runs': [("磁吸焊接辅助手电", 46, True, C_WHITE)]}])
textbox(s, Inches(1.2), Inches(2.95), Inches(11.5), Inches(0.6),
        [{'runs': [("一吸即用 · 指哪照哪 —— 给焊接者一双腾出来的手", 20, False, C_ACCENT)]}])
textbox(s, Inches(1.2), Inches(3.75), Inches(11.5), Inches(0.6),
        [{'runs': [("1班C组 · 仿真实跑不队", 16, True, RGBColor(0xD6,0xE2,0xEC))]}])
textbox(s, Inches(1.2), Inches(4.35), Inches(11.5), Inches(0.9),
        [{'runs': [("核心成员：邵子中（负责人）  ·  李昊桐  ·  姜亚楷", 14, False, RGBColor(0x9C,0xB3,0xC9))]}])
textbox(s, Inches(1.2), Inches(5.0), Inches(11.5), Inches(0.9),
        [{'runs': [("验证对象：焊接工位 · 高频手工焊接 / 焊点检查场景", 13, False, RGBColor(0x9C,0xB3,0xC9))]}])
textbox(s, Inches(11.7), Inches(5.85), Inches(1.05), Inches(0.4),
        [{'runs': [("V2.0", 14, True, RGBColor(0x9C,0xB3,0xC9))], 'align': PP_ALIGN.RIGHT}])

# ================= SLIDE 2 — 目录 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
rect(s, 0, 0, Inches(0.22), SH, C_DARK)
content_header(s, "目录", "CONTENTS 内容结构", None, C_ACCENT)
items = [
    ("01", "选题背景", "目标用户 · 量化痛点 · 竞品对比（3+，量化差异）"),
    ("02", "价值假设", "核心价值主张 · 五大待验证假设"),
    ("03", "精益画布", "九大模块 · 逻辑连线 · 颜色编码"),
    ("04", "MVP 验证", "验证设计 · 量化成功指标 · 5W2H 实施"),
    ("05", "增长潜力", "市场空间 · 增长假设 · 商业落地"),
    ("06", "实施规划", "成本 · 周期 · 风险 · 下一步行动"),
    ("07", "Q&A 预判", "三大最尖锐问题 · 关键回答"),
    ("08", "AI评价与团队分析", "评价摘要 · 逐条回应（认同/已执行/存疑）"),
]
y = Inches(1.45)
for num, t, d in items:
    rect(s, Inches(1.0), y, Inches(11.3), Inches(0.62), C_WHITE, line=C_LGRAY, line_w=0.75, round_=True, radius=0.12)
    textbox(s, Inches(1.25), y + Inches(0.11), Inches(0.8), Inches(0.5),
            [{'runs': [(num, 18, True, C_ACCENT)]}])
    textbox(s, Inches(2.05), y + Inches(0.08), Inches(3.0), Inches(0.5),
            [{'runs': [(t, 16, True, C_DARK)]}])
    textbox(s, Inches(5.1), y + Inches(0.14), Inches(7.0), Inches(0.5),
            [{'runs': [(d, 11.5, False, C_GRAY)]}])
    y = y + Inches(0.69)
footer(s, 2)

# ================= SLIDE 3 — 选题背景：目标用户 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "01", "选题背景：我们的目标用户", "目标用户画像与高频刚需场景")
roles = [
    ("高校电子类专业学生", "课程实训、毕设核心场景，高频电路焊接与调试。"),
    ("DIY 极客", "热衷自制硬件，享受动手组装，对焊接工具需求高频。"),
    ("研发 / 维修工程师", "原型开发与硬件调试，追求高精度、高稳定性焊接照明。"),
]
y = Inches(1.5)
for i, (t, d) in enumerate(roles):
    rect(s, Inches(0.55), y, Inches(5.9), Inches(1.15), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(1.15), C_PRIM if i != 1 else C_TEAL)
    textbox(s, Inches(0.85), y + Inches(0.16), Inches(5.4), Inches(0.5),
            [{'runs': [(t, 16, True, C_PRIM)]}])
    textbox(s, Inches(0.85), y + Inches(0.6), Inches(5.4), Inches(0.5),
            [{'runs': [(d, 12, False, C_TEXT)]}])
    y = y + Inches(1.28)

textbox(s, Inches(0.55), Inches(5.15), Inches(11), Inches(0.5),
        [{'runs': [("高频、刚需、三维场景交集，周使用频率 3 次以上", 14, True, C_ACCENT)]}])
stats = [
    ("84.13%", "每周焊接 ≥3 次", "高频作业人群"),
    ("76.98%", "依赖精细补光", "焊接微小贴片强烈依赖精准照度"),
    ("71.43%", "工位空间受限", "操作台狭小，传统灯具挤占空间"),
    ("100%", "需解放双手", "双手协同，无法手持灯具"),
]
x = Inches(0.55)
for i, (v, l, s2) in enumerate(stats):
    statbox(s, x, Inches(5.6), Inches(2.85), Inches(1.4), v, l, C_ACCENT if i != 3 else C_PRIM, s2)
    x = x + Inches(2.95)
footer(s, 3)

# ================= SLIDE 4 — 选题背景：量化痛点 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "01", "选题背景：核心痛点（126 份问卷量化支撑）", "真实焊接场景三大核心壁垒 · 数据来自问卷与沉浸式实测")
rows = [
    ("传统台灯", "68.25%", "体积庞大占用操作台核心空间，灯臂僵硬、角度受限，无法灵活聚焦微小焊点"),
    ("平价灯具", "61.11%", "支架单薄刚度不足，高频震动易致光源偏移；灯罩聚光差、光线发散"),
    ("专业光源", "54.76%", "动辄数百上千元，远超学生与业余爱好者预算，与非高频场景严重不匹配"),
]
y = Inches(1.55)
for t, pct, desc in rows:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(0.95), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(0.95), C_ACCENT if t == "传统台灯" else (C_PRIM if t == "平价灯具" else C_TEAL))
    textbox(s, Inches(0.9), y + Inches(0.1), Inches(2.0), Inches(0.7),
            [{'runs': [(t, 15, True, C_DARK)]}])
    textbox(s, Inches(2.9), y + Inches(0.08), Inches(2.0), Inches(0.7),
            [{'runs': [(pct, 26, True, C_ACCENT)]}])
    textbox(s, Inches(4.9), y + Inches(0.16), Inches(7.6), Inches(0.7),
            [{'runs': [(desc, 12, False, C_TEXT)]}])
    y = y + Inches(1.08)

# 沉浸式实测失败率
rect(s, Inches(0.55), Inches(4.85), Inches(12.2), Inches(1.5), C_DARK, round_=True, radius=0.08)
textbox(s, Inches(0.85), Inches(5.0), Inches(11), Inches(0.4),
        [{'runs': [("沉浸式实测：无照明 → 不同照明下的焊接失败率对比", 14, True, C_WHITE)]}])
seq = [
    ("无灯光", "50%"),
    ("传统台灯", "30%"),
    ("磁吸手电", "20%"),
]
x = Inches(0.9)
for name, v in seq:
    rect(s, x, Inches(5.5), Inches(2.2), Inches(0.7), C_ACCENT if name == "磁吸手电" else RGBColor(0x2B,0x4E,0x6E), round_=True, radius=0.15)
    textbox(s, x, Inches(5.58), Inches(2.2), Inches(0.5),
            [{'runs': [(name + "   ", 12, True, C_WHITE), (v, 17, True, C_WHITE)], 'align': PP_ALIGN.CENTER}])
    x = x + Inches(2.6)
textbox(s, Inches(8.4), Inches(5.55), Inches(4.1), Inches(0.6),
        [{'runs': [("手电失败率显著降低 30 个百分点 → 有效证明补光价值", 11.5, True, RGBColor(0xF0,0xC9,0x8A))]}])
footer(s, 4)

# ================= SLIDE 5 — 选题背景：竞品对比 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "01", "选题背景：竞品对比（量化差异）", "4 款方案横向对比 · 四大核心维度量化打分")
headers = ["产品", "价格带", "万向磁吸", "无级调光", "状态显示", "空间占用", "综合"]
rows = [
    ["传统台灯", "60–200元", "差", "差", "无", "高（占台面）", "★★"],
    ["廉价便携灯", "20–49元", "差", "少档位", "无", "中（易倾倒）", "★★"],
    ["专业工业灯", "300元+", "优", "有", "无", "高（占地）", "★★★"],
    ["磁吸焊接手电", "59–79元", "优", "无级", "LED+OLED", "零占地", "★★★★★"],
]
colw = [Inches(2.3), Inches(1.8), Inches(1.5), Inches(1.5), Inches(2.3), Inches(2.0), Inches(1.1)]
tbl = s.shapes.add_table(len(rows)+1, len(headers), Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.4)).table
for i, txt in enumerate(headers):
    tbl.cell(0, i).text = txt
    tbl.cell(0, i).fill.solid(); tbl.cell(0, i).fill.fore_color.rgb = C_DARK
    for rr in tbl.cell(0, i).text_frame.paragraphs[0].runs:
        set_font(rr, 12.5, True, C_WHITE)
for r, row in enumerate(rows):
    for c, txt in enumerate(row):
        tbl.cell(r+1, c).text = txt
        tbl.cell(r+1, c).fill.solid()
        tbl.cell(r+1, c).fill.fore_color.rgb = C_WHITE if r != 3 else RGBColor(0xFD,0xF0,0xE0)
        for rr in tbl.cell(r+1, c).text_frame.paragraphs[0].runs:
            if c == 0:
                set_font(rr, 12.5, True, C_PRIM if r != 3 else C_ACCENT)
            elif c == len(headers)-1:
                set_font(rr, 13, True, C_ACCENT)
            else:
                set_font(rr, 12, False, C_TEXT)
# note
rect(s, Inches(0.55), Inches(4.98), Inches(12.2), Inches(1.75), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.08)
bg = rect(s, Inches(0.55), Inches(4.98), Inches(0.12), Inches(1.75), C_ACCENT)
textbox(s, Inches(0.9), Inches(5.08), Inches(11.6), Inches(0.4),
        [{'runs': [("市场机会： ", 13.5, True, C_ACCENT),
                   ("现有方案无法兼顾「万向磁吸、无级调光、状态可视、低成本」四大核心需求，市场存在明显空白。", 13.5, True, C_TEXT)]}])
textbox(s, Inches(0.9), Inches(5.5), Inches(11.6), Inches(0.35),
        [{'runs': [("综合评分依据（量化）：", 11.5, True, C_PRIM),
                   (" 万向磁吸 × 无级调光 × 状态显示 × 空间占用 四项可量化事实加权 —— 仅磁吸焊接手电四项全覆盖 → 满分", 11.5, False, C_TEXT)]}])
textbox(s, Inches(0.9), Inches(5.85), Inches(11.6), Inches(0.35),
        [{'runs': [("差异化组合：", 11.5, True, C_PRIM),
                   (" 强磁吸附 + 360°悬停 + 无级调光 + LED 状态（OLED 选配），以 59–79 元普惠定价（对比专业灯 300 元+）切入。", 11.5, False, C_TEXT)]}])
textbox(s, Inches(0.9), Inches(6.2), Inches(11.6), Inches(0.35),
        [{'runs': [("护城河主张：", 11.5, True, C_TEAL),
                   (" 价格分层（49/79 元）＋ 高校/创客教育生态 ＋ 焊接工位标准数据接口（OPC 生态对接）。", 11.5, False, C_TEXT)]}])
footer(s, 5)

# ================= SLIDE 6 — 价值假设 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "02", "价值假设：核心价值主张与待验证假设", "从“创意是否值得做”到“证据闭环”的关键假设清单")
rect(s, Inches(0.55), Inches(1.5), Inches(12.2), Inches(1.15), C_DARK, round_=True, radius=0.08)
textbox(s, Inches(0.9), Inches(1.62), Inches(11.6), Inches(0.5),
        [{'runs': [("核心价值主张：给焊接者一双腾出来的手", 18, True, C_WHITE)]}])
textbox(s, Inches(0.9), Inches(2.12), Inches(11.6), Inches(0.5),
        [{'runs': [("磁吸固定解放双手 · 万向悬停指哪照哪 · 无级调光适配光环境 · 目标零售 59–79 元（对比专业灯 300 元+）", 13, False, RGBColor(0xE9,0xF1,0xF7))]}])
# 宣传口径声明（观点1 对齐）
rect(s, Inches(0.55), Inches(2.7), Inches(12.2), Inches(0.54), C_WHITE, line=C_ACCENT, line_w=1.25, round_=True, radius=0.12)
textbox(s, Inches(0.85), Inches(2.78), Inches(11.6), Inches(0.4),
        [{'runs': [("口径声明（V2.0 对齐）：LED 状态显示＝量产标配；OLED＝可选扩展模块（H1 排针预留）——宣传口径与实物一致，消除“表里不一”质疑。", 12, True, C_ACCENT)]}])
assum = [
    ("假设 1 · 最高优先", "6 颗 LED 状态灯（4 电量+2 充电）能覆盖用户 80% 状态查询需求", "在无屏样机 vs OLED 外接版 20 人 A/B 对比测试下成立"),
    ("假设 2", "用户愿意为“温度过热提醒”支付 +15 元", "在 59–79 元目标价位区间内成立"),
    ("假设 3", "“青春版（¥39–49 无屏版）”能覆盖 20% 以上价格敏感用户", "在与标准版同时展示时成立"),
    ("假设 4", "2600mAh 高配版（+¥8）有 ≥20% 用户选择", "在双版本同时售卖的条件下成立"),
    ("假设 5", "柔性臂 3000 次弯折后角度漂移仍 <5°", "在实验室疲劳测试条件下成立"),
]
y = Inches(3.3)
for i, (t, content, cond) in enumerate(assum):
    hl = C_ACCENT if i == 0 else C_PRIM
    rect(s, Inches(0.55), y, Inches(12.2), Inches(0.68), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(0.68), hl)
    textbox(s, Inches(0.85), y + Inches(0.05), Inches(2.6), Inches(0.5),
            [{'runs': [(t, 12, True, hl)]}])
    textbox(s, Inches(3.4), y + Inches(0.02), Inches(9.2), Inches(0.5),
            [{'runs': [(content, 11, True, C_TEXT)]}])
    textbox(s, Inches(3.4), y + Inches(0.36), Inches(9.2), Inches(0.32),
            [{'runs': [("成立条件： " + cond, 9.5, False, C_GRAY)]}])
    y = y + Inches(0.76)
footer(s, 6)

# ================= SLIDE 7 — 精益画布 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "03", "精益画布：九大模块 · 逻辑连线 · 颜色编码", "一页看清问题—方案—优势—利润的闭环")
cw, ch = Inches(3.9), Inches(1.55)
gx, gy = Inches(0.17), Inches(0.15)
x0, y0 = Inches(0.55), Inches(1.45)
cells = [
    ("问题 Problem", "#C0392B", ["84.13% 高频焊接", "76.98% 依赖精细补光", "100% 需双手", "三类灯具各有短板"]),
    ("客户细分 Segment", "#1F5F8B", ["高校电子专业学生", "DIY 极客", "研发/维修工程师"]),
    ("独特价值主张 UVP", "#E8792B", ["磁吸固定解放双手", "万向悬停指哪照哪", "无级调光适配光环境", "59–79 普惠定价"]),
    ("解决方案 Solution", "#0F6E68", ["强力磁吸+360°悬停", "高显指OSRAM LED", "无级调光(20kHz无频闪)", "LED状态(OLED选配)"]),
    ("不公平优势 Advantage", "#6B4C93", ["成熟供应链无断供", "双版本价格分层", "创客教育深度属性"]),
    ("关键指标 Metrics", "#2E8B57", ["购买意愿 ≥60%", "高频作业 84.13%", "用户留存 45.2%"]),
    ("渠道 Channels", "#C08428", ["网络电商", "微商/社群裂变", "创客教育/高校渠道"]),
    ("成本结构 Cost", "#5A626E", ["BOM ¥25–35", "OLED +¥5 高配 +¥8", "小批量外壳/柔性臂"]),
    ("收入来源 Revenue", "#1F8B8B", ["标准版 59–79", "青春版 39–49 高配版", "配件/扩展模块"]),
]
pos = {}
i = 0
for r in range(3):
    for c in range(3):
        title, hexc, lines = cells[i]
        ccol = RGBColor(int(hexc[1:3],16), int(hexc[3:5],16), int(hexc[5:7],16))
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        pos[(r,c)] = (x, y)
        box = rect(s, x, y, cw, ch, C_WHITE, line=ccol, line_w=1.25, round_=True, radius=0.06)
        textbox(s, x + Inches(0.15), y + Inches(0.12), cw - Inches(0.3), Inches(0.4),
                [{'runs': [(title, 12.5, True, ccol)]}])
        rect(s, x, y, Inches(0.08), ch, ccol)
        tb = textbox(s, x + Inches(0.15), y + Inches(0.46), cw - Inches(0.3), ch - Inches(0.55),
                     [{'runs': [(ln, 9.5, False, C_TEXT)], 'space_after': 2} for ln in lines])
        i += 1
# logical connection arrows (color-coded): problem->uvp->solution; uvp->advantage->metrics->revenue
def center(idx, side):
    x, y = pos[idx]
    if side == "R": return (x + cw, y + ch/2)
    if side == "L": return (x, y + ch/2)
    if side == "T": return (x + cw/2, y)
    if side == "B": return (x + cw/2, y + ch)
def arrow(slide, a, b, color, w=Inches(0.045)):
    ax, ay = a; bx, by = b
    if abs(bx-ax) < Emu(1) or abs(by-ay) < Emu(1):
        return
    x = min(ax, bx); y = min(ay, by)
    if abs(by-ay) < Emu(1):
        rect(slide, x, ay - w/2, bx-ax if bx>ax else ax-bx, w, color)
    else:
        rect(slide, ax - w/2, y, w, by-ay if by>ay else ay-by, color)
arrow(s, center((0,0),"R"), center((0,2),"L"), C_ACCENT)           # 问题 -> 价值主张
arrow(s, center((0,2),"B"), center((1,0),"R"), C_PRIM)             # 价值主张 -> 解决方案
arrow(s, center((0,0),"B"), center((1,0),"T"), C_PRIM)             # 问题 -> 解决方案
arrow(s, center((0,2),"B"), center((1,1),"T"), C_TEAL)             # 价值主张 -> 优势
arrow(s, center((1,0),"R"), center((1,1),"L"), C_TEAL)             # 解决方案 -> 优势
arrow(s, center((1,1),"B"), center((2,0),"T"), C_GREEN)            # 优势 -> 渠道
arrow(s, center((1,0),"B"), center((2,1),"T"), C_GRAY)             # 方案 -> 成本
arrow(s, center((1,1),"R"), center((1,2),"L"), C_GREEN)            # 优势 -> 关键指标
arrow(s, center((1,2),"B"), center((2,2),"T"), C_TEAL)              # 指标 -> 收入
# legend
lg = rect(s, Inches(0.55), Inches(6.45), Inches(12.2), Inches(0.55), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.15)
textbox(s, Inches(0.8), Inches(6.55), Inches(11.9), Inches(0.4),
        [{'runs': [("颜色编码：", 11, True, C_DARK),
                   ("红=问题  蓝=客户  橙=价值主张  绿=方案  紫=优势  绿=关键指标  金=渠道  灰=成本  青=利润   | 逻辑连线：问题→价值主张→方案/优势→关键指标→收入", 9.5, False, C_GRAY)]}])
footer(s, 7)

# ================= SLIDE 8 — MVP 验证设计 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "04", "MVP 验证：验证设计与量化指标", "20 人 × 25 分钟真实焊接 A/B 对比 + 虚拟支付问卷")
left = [
    ("MVP 形态", "物理装置样机 A/B 对比 + 虚拟支付问卷。A 组＝现有无屏样机（LED 状态灯）；B 组＝同款样机 + OLED 扩展模块（H1 排针外接），两组外观一致避免偏见。"),
    ("验证目标", "① 假设 1：LED 灯 vs OLED 在真实焊接中状态查询效率是否等价；② 假设 2：59–79 元价格带的购买意愿。"),
    ("测试对象", "与目标用户画像一致的 20 人：DIY 极客 4、课程实训生 4、研发工程师 4、焊接初学者 8（考察非技术用户）。"),
    ("测试场景", "电工基地实验室真实焊台，连续焊接 25 分钟（20 颗 0603 电阻），环境光按“下午 3 点靠窗”模拟；随机打断询问“现在电量/档位”。"),
]
y = Inches(1.5)
for t, d in left:
    rect(s, Inches(0.55), y, Inches(6.4), Inches(1.0), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    textbox(s, Inches(0.8), y + Inches(0.08), Inches(6), Inches(0.35),
            [{'runs': [(t, 13.5, True, C_PRIM)]}])
    textbox(s, Inches(0.8), y + Inches(0.4), Inches(6), Inches(0.6),
            [{'runs': [(d, 11, False, C_TEXT)]}])
    y = y + Inches(1.13)

# success/fail
rect(s, Inches(7.25), Inches(1.5), Inches(5.5), Inches(2.15), C_WHITE, line=C_GREEN, line_w=1.25, round_=True, radius=0.08)
textbox(s, Inches(7.5), Inches(1.62), Inches(5), Inches(0.4),
        [{'runs': [("✅ 成功标准（任一成立）", 14, True, C_GREEN)]}])
for i, t in enumerate(["≥70% 测试者 25 分钟状态查询 ≤2 次且 ≤5 秒/次（A/B 差异 <10%）",
                     "≥60% 愿意购买（≤59 元档 ≥40%）",
                     "A 组主观评分 ≥4/5"]):
    textbox(s, Inches(7.5), Inches(2.05 + i*0.3), Inches(5.05), Inches(0.35),
            [{'runs': [(f"•  {t}", 10.5, False, C_TEXT)]}])
rect(s, Inches(7.25), Inches(3.8), Inches(5.5), Inches(1.55), C_WHITE, line=C_RED, line_w=1.25, round_=True, radius=0.08)
textbox(s, Inches(7.5), Inches(3.9), Inches(5), Inches(0.4),
        [{'runs': [("✘ 失败标准", 13.5, True, C_RED)]}])
for i, t in enumerate(["A 组查询效率显著低于 B 组（差异 ≥30%）或主观评分 <3/5",
                     "购买意愿 <40%；满足其一即判假设不成立",
                     "→ 转入“集成 OLED 版”或“降价版”路线"]):
    textbox(s, Inches(7.5), Inches(4.28 + i*0.3), Inches(5.05), Inches(0.35),
            [{'runs': [(f"•  {t}", 10.5, False, C_TEXT)]}])

# quantified metric highlight
rect(s, Inches(0.55), Inches(6.05), Inches(12.2), Inches(0.9), C_TEAL, round_=True, radius=0.08)
textbox(s, Inches(0.85), Inches(6.15), Inches(11.8), Inches(0.4),
        [{'runs': [("量化核心指标：", 14, True, C_WHITE)]}])
textbox(s, Inches(0.85), Inches(6.5), Inches(11.8), Inches(0.4),
        [{'runs': [("状态查询 ≤2 次 / 每次 ≤5 秒 · 购买意愿 ≥60% · 59 元档占比 ≥40% · A/B 差异 <10%", 13, True, RGBColor(0xE6,0xF4,0xF2))]}])
footer(s, 8)

# ================= SLIDE 9 — MVP 5W2H 实施 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "04", "MVP 验证：5W2H 实施规划", "6 天 × 约 300 元，用最小成本验证两大核心假设")
rows5w = [
    ("Why", "为什么做", "证明“LED 替换 OLED”成立（假设1）并锁定价格带（假设2），为最终决策提供证据。"),
    ("What", "做什么", "20 人×25 分钟真实焊接 A/B 对比测试 + 虚拟支付问卷（两版展示 39/59/79 元档）。"),
    ("Who", "谁来做", "邵子中（主持与数据）、李昊桐（样机调校）、姜亚楷（招募与场景）；对象＝画像一致的 20 名测试者。"),
    ("When", "何时完成", "D1–2 招募与问卷设计；D3–4 集中测试（每天 10 人）；D5 数据统计；D6 结论与报告。"),
    ("Where", "在哪做", "电工基地实验室焊台（真实使用环境，非演示室）。"),
    ("How", "如何做（≥3 步）", "① 随机分组 A/B 各 10 人测状态查询效率；② 交换组别重测一次并完成 25 分钟计时；③ 虚拟支付三档卡片统计意愿；④ 汇总数据对照成功/失败标准出结论。"),
    ("How much", "投入产出", "成本 ≈300 元（OLED ¥20、礼品 ¥150、布耗 ¥50、杂项 ¥80）；时间 6 天；产出 20 份有效测试记录。"),
]
y = Inches(1.5)
for k, t, d in rows5w:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(0.72), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
    rect(s, Inches(0.55), y, Inches(1.35), Inches(0.72), C_PRIM)
    textbox(s, Inches(0.62), y + Inches(0.13), Inches(1.2), Inches(0.5),
            [{'runs': [(k, 14, True, C_WHITE)]}])
    textbox(s, Inches(2.05), y + Inches(0.08), Inches(1.7), Inches(0.5),
            [{'runs': [(t, 12.5, True, C_TEXT)]}])
    textbox(s, Inches(3.8), y + Inches(0.1), Inches(8.8), Inches(0.6),
            [{'runs': [(d, 11, False, C_TEXT)]}])
    y = y + Inches(0.8)
footer(s, 9)

# ================= SLIDE 10 — 增长潜力 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "05", "增长潜力：市场空间与增长假设", "高频刚需 × 普惠定价 × 社群裂变")
statbox(s, Inches(0.55), Inches(1.5), Inches(3.9), Inches(1.6), "45.2%", "用户留存率", C_GREEN, "短期试点实测，超出 40% 预设目标，验证高粘性。")
statbox(s, Inches(4.7), Inches(1.5), Inches(3.9), Inches(1.6), "84.13%", "高频刚需占比", C_PRIM, "每周焊接 ≥3 次，刚需属性显著，使用粘性强。")
statbox(s, Inches(8.85), Inches(1.5), Inches(3.9), Inches(1.6), "300万+", "潜在用户基数", C_ACCENT, "三类用户 × 年新增学生群体，覆盖基数大。")

rect(s, Inches(0.55), Inches(3.35), Inches(12.2), Inches(1.15), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.10)
textbox(s, Inches(0.85), Inches(3.45), Inches(11.6), Inches(0.4),
        [{'runs': [("增长逻辑：卓越体验 + 极致性价比 → 口碑与社群裂变", 15, True, C_DARK)]}])
textbox(s, Inches(0.85), Inches(3.9), Inches(11.6), Inches(0.5),
        [{'runs': [("低单价高频刚需 · 三类用户全覆盖 · DIY 社区晒图传播性强 · 网络电商+社群双渠道", 12, False, C_TEXT)]}])

rect(s, Inches(0.55), Inches(4.7), Inches(12.2), Inches(2.0), C_DARK, round_=True, radius=0.08)
textbox(s, Inches(0.85), Inches(4.82), Inches(11.6), Inches(0.4),
        [{'runs': [("蓝海市场与商业落地", 15, True, C_ACCENT)]}])
for i, t in enumerate([
    "精准填补平价焊接照明细分赛道空白，差异化竞争优势强。",
    "硬件结构简洁，量产成本可控，盈利模式清晰，具备快速商业化复制条件。",
    "竞争评审权重：实用性 40%（最高）、安全性 20% → 本方案在关键维度优势明显。"]):
    textbox(s, Inches(0.85), Inches(5.25 + i*0.4), Inches(11.6), Inches(0.4),
            [{'runs': [(f"•  {t}", 12, False, RGBColor(0xD6,0xE2,0xEC))]}])
# 数据来源标注（观点3 证据可信度）
rect(s, Inches(0.85), Inches(6.42), Inches(11.6), Inches(0.24), C_WHITE, line=None, round_=True, radius=0.2)
textbox(s, Inches(1.0), Inches(6.46), Inches(11.4), Inches(0.2),
        [{'runs': [("数据来源：45.2%=2026 年暑期短期试点实测（n=60） · 84.13%=126 份用户问卷 · 300万+=三类用户×年新增学生群体估算", 9.5, False, RGBColor(0x9C,0xB3,0xC9))]}])
footer(s, 10)

# ================= SLIDE 11 — 实施规划 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "06", "实施规划：成本 / 周期 / 风险与下一步", "以“证据闭环”状态参赛的项目推进路线")
left = [
    ("成本与产品结构", [
        "BOM ¥25–35；整机目标价 59–79 元（零售）",
        "标准版 LED 状态标配 + OLED 选配模块（+¥5）",
        "青春版 ¥39–49 无屏版；高配版 2600mAh +¥8",
        "补装 NTC 过温提示（BOM +¥0.5）"]),
    ("周期与里程碑", [
        "MVP 验证 6 天（D1–6）",
        "验证结论后锁定“LED 标配+OLED 选配”双配置",
        "答辩前完成无屏 vs OLED 对比演示展板",
        "套件化作为深度性演示环节保留"]),
    ("风险与应对", [
        "宣传（OLED）与样机（LED）不一致 → 口径对齐",
        "小批量外壳/柔性臂成本高于预估 → 压缩 BOM/降级",
        "大厂 3 个月可仿制 → 靠创客教育深度性与垂直生态",
        "3C 认证成本 → 合规前置，分阶段推进"]),
]
y = Inches(1.5)
for t, items in left:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(1.5), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.08)
    textbox(s, Inches(0.85), y + Inches(0.1), Inches(11.6), Inches(0.4),
            [{'runs': [(t, 14, True, C_PRIM)]}])
    yy = y + Inches(0.45)
    for it in items:
        textbox(s, Inches(1.0), yy, Inches(11.5), Inches(0.32),
                [{'runs': [(f"•  {it}", 11, False, C_TEXT)]}])
        yy = yy + Inches(0.26)
    y = y + Inches(1.62)
footer(s, 11)

# ================= SLIDE 12 — 创新方法应用 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "补", "创新方法应用：SCAMPER × 六顶思考帽", "两种工具交叉验证，定位结构性缺陷并给出低成本修复路径")
# SCAMPER
rect(s, Inches(0.55), Inches(1.5), Inches(6.05), Inches(5.1), C_WHITE, line=C_PRIM, line_w=1.25, round_=True, radius=0.06)
textbox(s, Inches(0.85), Inches(1.62), Inches(5.5), Inches(0.4),
        [{'runs': [("SCAMPER 系统审查", 15, True, C_PRIM)]}])
sca = [
    ("S 替代", "OSRAM+20kHz PWM 显指/无频闪优先，不冒进替代"),
    ("C 合并", "腕带收纳 + 磁吸充电座（零风险采纳）"),
    ("A 适配", "结构件全部采用成熟供应链，无断供风险"),
    ("M 调整", "双版本策略（标准版+青春版）直接采纳"),
    ("P 改变用途", "整机取下即手电，第二用途作宣传卖点"),
    ("E 消除", "🔴 最大薄弱点：机载 LED 替代 OLED（待验证）"),
    ("R 重组/逆向", "参赛版改“自制套件”强化深度性"),
]
yy = Inches(2.18)
for k, v in sca:
    hl = C_RED if "E " in k else C_TEXT
    textbox(s, Inches(0.85), yy, Inches(5.55), Inches(0.35),
            [{'runs': [(k + "： ", 11.5, True, C_PRIM), (v, 10.5, False, hl)]}])
    yy = yy + Inches(0.62)
# hats
rect(s, Inches(6.85), Inches(1.5), Inches(5.95), Inches(5.1), C_WHITE, line=C_ACCENT, line_w=1.25, round_=True, radius=0.06)
textbox(s, Inches(7.15), Inches(1.62), Inches(5.4), Inches(0.4),
        [{'runs': [("六顶思考帽：角色综合评估", 15, True, C_ACCENT)]}])
hats = [
    ("白帽 · 事实", "问卷 126 份：三痛点 68.25%/61.11%/54.76%，实测失败率 50%→20%"),
    ("红帽 · 直觉", "“产品能卖，但 OLED 没了，总感觉不踏实”"),
    ("黄帽 · 乐观", "磁吸+万向悬停是真实差异点，竞品无对应形态"),
    ("黑帽 · 悲观", "🔴 头号风险：宣传与实物不符，答辩会被当场质疑"),
    ("绿帽 · 创造", "OLED 改选配模块；NTC 过温提示替代热电偶；双 SKU 分层"),
    ("蓝帽 · 总结", "决策：先补证再定稿，调整后推进（证据闭环）"),
]
yy = Inches(2.18)
for k, v in hats:
    hl = C_RED if "黑帽" in k else C_TEXT
    textbox(s, Inches(7.15), yy, Inches(5.45), Inches(0.35),
            [{'runs': [(k + "： ", 11.5, True, C_ACCENT), (v, 10.5, False, hl)]}])
    yy = yy + Inches(0.62)
footer(s, 12)

# ================= SLIDE 13 — Q&A 预判 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "07", "Q&A 预判：三大最尖锐问题", "主动暴露 · 以证据闭环回应潜在质疑")
qa = [
    ("评委：你宣传 OLED 状态显示，为什么样机用的是 LED？",
     "回应：这是我们在验证中主动发现并优化的点——LED 状态灯（4 电量+2 充电）明确覆盖核心状态查询，OLED 已改作“选配扩展模块”（H1 排针预留），标配成本更低。已规划 20 人 A/B 测试（假设 1），用数据证明 LED 能否覆盖 80% 查询需求，让劣势变成可讲解的迭代设计。"),
    ("评委：59 元守住成本吗？它不就是一个磁吸台灯，凭什么卖这个价？",
     "回应：BOM ¥25–35，双版本分层（青春版 39–49 / 标准版 59–79）覆盖价格敏感人群；磁吸→万向悬停→无级调光→状态显示的差异化组合是竞品没有的。痛点有问卷与实测双重证据（失败率 50%→20%），定价由证据支撑而非拍脑袋。"),
    ("评委：大厂 3 个月就能仿制，你们的壁垒在哪？",
     "回应：我们靠两件事——① 面向高校与创客教育的深度属性（自制套件版强化动手属性，纳入演示环节）；② 焊接工位数字化生态（与“AI+OPC”主题相衔接，中期扩展标准数据接口，上报实验/产线管理系统），构建从单品到生态的纵深，而非仅依赖单一硬件。"),
]
y = Inches(1.5)
for t, a in qa:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(1.62), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.08)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(1.62), C_ACCENT)
    textbox(s, Inches(0.85), y + Inches(0.1), Inches(11.6), Inches(0.45),
            [{'runs': [(t, 13, True, C_DARK)]}])
    textbox(s, Inches(0.85), y + Inches(0.58), Inches(11.6), Inches(0.95),
            [{'runs': [(a, 11, False, C_TEXT)]}])
    y = y + Inches(1.75)
footer(s, 13)

# ================= SLIDE 14 — AI评价与团队分析（1）=============
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "08", "AI 评价与团队分析：评价摘要", "DeepSeek-V4 外部视角 · 提问日期 2026-08-28 · 三大最具代表性观点")
# 工具说明条
rect(s, Inches(0.55), Inches(1.45), Inches(12.2), Inches(0.5), C_DARK, round_=True, radius=0.10)
textbox(s, Inches(0.85), Inches(1.53), Inches(11.6), Inches(0.35),
        [{'runs': [("AI 工具：DeepSeek-V4（deepseek/deepseek-v4-flash-vision-exp）  ·  评价对象：PPT V1.0 完整核心内容  ·  评价维度：需求真实性 / 方案可行性 / 竞争差异化 / 逻辑自洽性 / 风险与漏洞 / 证据可信度", 11, True, C_WHITE)]}])
qv = [
    ("观点 ① 逻辑自洽性 / 风险与漏洞", C_RED,
     "“宣传口径（OLED）与实物（LED）不一致，精益画布方案层与价值主张层未对齐，这是方案最脆弱之处。”"),
    ("观点 ② 竞争差异化", C_ACCENT,
     "“竞品对比综合星级为团队主观自评，未用实测指标量化；‘市场空白’建立在定性判断上，‘不公平优势/护城河’不够可验证。”"),
    ("观点 ③ 方案可行性", C_PRIM,
     "“20 人样本（A/B 各 10 人）对验证‘差异 <10%’的等价性统计功效不足；MVP 执行难度或低估。”"),
]
y = Inches(2.15)
for t, c, q in qv:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(1.4), C_WHITE, line=c, line_w=1.25, round_=True, radius=0.08)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(1.4), c)
    textbox(s, Inches(0.85), y + Inches(0.12), Inches(11.6), Inches(0.4),
            [{'runs': [(t, 14, True, c)]}])
    textbox(s, Inches(0.85), y + Inches(0.5), Inches(11.6), Inches(0.75),
            [{'runs': [(q, 12, False, C_TEXT)]}])
    y = y + Inches(1.5)
# 小结
rect(s, Inches(0.55), Inches(6.6), Inches(12.2), Inches(0.45), C_TEAL, round_=True, radius=0.2)
textbox(s, Inches(0.85), Inches(6.67), Inches(11.6), Inches(0.32),
        [{'runs': [("团队处理原则：AI 是“外部视角的镜子”，以认同 / 已执行 / 存疑三层机制批判性吸收，而非全盘接受或全盘否定。", 11.5, True, C_WHITE)]}])
footer(s, 14)

# ================= SLIDE 15 — AI评价与团队分析（2）=============
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "09", "AI 评价与团队分析：逐条回应", "认同 / 已执行 / 存疑 —— 批判性吸收 AI 反馈")
resp = [
    ("观点 ① 逻辑自洽 · 宣传与实物一致", C_RED,
     [("认同", "完全认同。这正是我们在 SCAMPER E 维度与六帽黑帽中自查出的头号风险；AI 从外部再次确认，形成“团队自查 + AI 印证”双重复核。"),
      ("已执行", "统一宣传口径为“LED 标配 + OLED 选配”；精益画布解决方案栏同步对齐；并把“待验证假设”前置标注为未验证状态，避免以“价值验证”自居。"),
      ("存疑", "无分歧。")]),
    ("观点 ② 竞争差异化 · 护城河", C_ACCENT,
     [("认同", "认同“综合星级”形式不够严谨、空白结论偏定性。"),
      ("已执行", "在竞品对比页补充“综合评分依据（量化）”；用失败率 50%→20% 与 79 元 vs 300 元+ 价差作为差异化落点，并新增三层护城河主张。"),
      ("存疑", "对“护城河不足”保留：我们主张小米式“价分层 + 教育生态 + OPC 生态接口”竞争策略，大厂模仿成本高、回报低，故保留“不公平优势”定位并进一步明确为三层。")]),
    ("观点 ③ 方案可行性 · 样本量", C_PRIM,
     [("认同", "承认 MVP 阶段样本偏小、统计功效有限，这是“最小成本验证”的固有权衡。"),
      ("已执行", "将 MVP 定位改为“低成本的早期方向性证据 + 明确退路”，补上失败退路（转入集成 OLED 版 / 降价版），而非宣称“已验证”。"),
      ("存疑", "对“执行难度被低估”不完全认同：已按 5W2H 拆分为三人分工，并在 V2.0 追加“若招募不足 20 人，采用 5 人/组×4 场”的备选样本方案作缓冲。")]),
]
y = Inches(1.5)
for t, c, items in resp:
    rect(s, Inches(0.55), y, Inches(12.2), Inches(1.8), C_WHITE, line=c, line_w=1.25, round_=True, radius=0.08)
    rect(s, Inches(0.55), y, Inches(0.12), Inches(1.8), c)
    textbox(s, Inches(0.85), y + Inches(0.1), Inches(11.6), Inches(0.35),
            [{'runs': [(t, 13.5, True, c)]}])
    yy = y + Inches(0.48)
    for tag, body in items:
        tagcol = C_GREEN if tag == "认同" else (C_ACCENT if tag == "已执行" else C_PRIM)
        textbox(s, Inches(0.85), yy, Inches(0.9), Inches(0.3),
                [{'runs': [("【" + tag + "】", 10.5, True, tagcol)]}])
        textbox(s, Inches(1.8), yy, Inches(10.8), Inches(0.62),
                [{'runs': [(body, 10.5, False, C_TEXT)], 'space_after': 1}])
        yy = yy + Inches(0.44)
    y = y + Inches(1.9)
footer(s, 15)

# ================= SLIDE 16 — 总结 + Q&A 感谢 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_DARK)
rect(s, Inches(0), Inches(6.9), SW, Inches(0.6), C_ACCENT)
textbox(s, Inches(1.2), Inches(1.2), Inches(11), Inches(1.0),
        [{'runs': [("项目总结", 16, False, RGBColor(0x9C,0xB3,0xC9))]}])
textbox(s, Inches(1.2), Inches(1.55), Inches(11.5), Inches(0.9),
        [{'runs': [("磁吸焊接辅助手电 —— 从“创意值得做”到“证据闭环”", 24, True, C_WHITE)]}])
summ = [
    ("精准定位", "直击焊接作业中的照明盲区与双手受限痛点，以数据定义需求。"),
    ("创新方案", "独创“强磁快拆 + 万向悬停 + 无级调光 + 状态显示”组合。"),
    ("价值验证", "问卷 + 沉浸式实测双重证据，失败率 50%→20%，答辩以证据闭环参赛。"),
    ("未来展望", "围绕焊接场景扩展测温、防护、辅助定位，构建一体化智能作业生态。"),
]
y = Inches(2.55)
for t, d in summ:
    rect(s, Inches(1.0), y, Inches(11.3), Inches(0.78), RGBColor(0x18,0x36,0x52), round_=True, radius=0.10)
    textbox(s, Inches(1.3), y + Inches(0.12), Inches(2.0), Inches(0.5),
            [{'runs': [(t, 15, True, C_ACCENT)]}])
    textbox(s, Inches(3.4), y + Inches(0.14), Inches(8.6), Inches(0.55),
            [{'runs': [(d, 11.5, False, RGBColor(0xD6,0xE2,0xEC))]}])
    y = y + Inches(0.9)
textbox(s, Inches(1.2), Inches(6.25), Inches(11.5), Inches(0.9),
        [{'runs': [("感谢聆听  ·  Q&A", 26, True, C_WHITE)]}])
textbox(s, Inches(1.2), Inches(6.6), Inches(11.5), Inches(0.5),
        [{'runs': [("欢迎各位评委随时提问，共同探讨与交流", 13, False, RGBColor(0x9C,0xB3,0xC9))]}])

# ================= SLIDE 15 — 附录 =================
s = add_slide()
rect(s, 0, 0, SW, SH, C_BG)
content_header(s, "附", "附录：方法流程与数据支撑", "附录不计入正页 · 含验证方法与基础数据")
cols = [
    ("验证流程", ["选题论证 → 需求调研", "SCAMPER + 六帽评估", "待验证假设清单", "MVP A/B 对比验证", "结论：调整后推进"]),
    ("数据来源", ["问卷 126 份", "沉浸式实测（三照明对照）", "竞品价格带走查", "20 人 A/B 测试（规划）", "短期试点留存数据"]),
    ("关键数据", ["高频作业 84.13%", "精细补光 76.98%", "痛点 68.25%/61.11%/54.76%", "失败率 50%→20%", "留存率 45.2%"]),
    ("团队分工", ["邵子中：主持、蓝帽、数据", "李昊桐：白帽/黑帽、样机调校", "姜亚楷：黄帽/绿帽、招募场景", "绿帽环节三人共同（姜主导）", "——"]),
]
x = Inches(0.55)
for t, items in cols:
    rect(s, x, Inches(1.5), Inches(2.95), Inches(5.0), C_WHITE, line=C_LGRAY, line_w=1, round_=True, radius=0.06)
    textbox(s, x + Inches(0.15), Inches(1.62), Inches(2.6), Inches(0.4),
            [{'runs': [(t, 14, True, C_PRIM)]}])
    rect(s, x, Inches(1.5), Inches(2.95), Inches(0.05), C_ACCENT)
    yy = Inches(2.1)
    for it in items:
        textbox(s, x + Inches(0.15), yy, Inches(2.6), Inches(0.6),
                [{'runs': [(f"•  {it}", 11, False, C_TEXT)]}])
        yy = yy + Inches(0.66)
    x = x + Inches(3.05)
footer(s, "附录")

out = r"C:\Users\Lenovo\Desktop\仿真实跑不队_选题答辩项目V2\仿真实跑不队_磁吸焊接辅助手电_选题答辩PPT_V2.0.pptx"
prs.save(out)
print("SAVED", out, len(prs.slides.__iter__.__self__._sldIdLst))
