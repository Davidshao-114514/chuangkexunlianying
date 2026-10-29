# -*- coding: utf-8 -*-
"""生成《选题优化方案书》全部配图（PIL + matplotlib）"""
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

from econ import ECON, CH, BOM_TIERS, COMPETITORS, LTV, FIXED, LABOR_HOURS, LABOR_RATE

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/msyh.ttc"
FONTB = "C:/Windows/Fonts/msyhbd.ttc"
MSYH = FontProperties(fname=FONT)
MSYHB = FontProperties(fname=FONTB)
plt.rcParams["axes.unicode_minus"] = False

# 配色
GREEN = (34, 139, 87)     # 已验证成立
YELLOW = (208, 148, 20)   # 验证中 / 部分成立
RED = (192, 58, 51)       # 已证伪并调整
GREY = (90, 96, 106)
LIGHT = (247, 248, 250)
BLUE = (44, 90, 160)


def f(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)


import re
_TOKEN = re.compile(r"[A-Za-z0-9%¥．.．\-+/×≥≤<>（）()\[\]]+|.", re.S)


def wrap(draw, text, font, maxw):
    """按宽度断行：数字/英文/百分数等作为不可拆分的原子 token；绝不丢字、不重复"""
    tokens = _TOKEN.findall(text)
    lines, cur = [], ""
    for tk in tokens:
        if tk == "\n":
            lines.append(cur); cur = ""; continue
        cand = cur + tk
        if not cur or draw.textlength(cand, font=font) <= maxw:
            cur = cand
        else:
            lines.append(cur); cur = tk
    if cur:
        lines.append(cur)
    # 行尾孤立标点并入上一行
    fixed = []
    for ln in lines:
        if fixed and len(ln) <= 1 and ln in "，。；、）】":
            fixed[-1] += ln
        else:
            fixed.append(ln)
    return fixed


# =====================================================================
# 图 1：精益画布 V3.0
# =====================================================================
def canvas_v3():
    W = 2060
    M, GAP, TOP = 44, 16, 148
    colw = [366, 366, 366, 356, 366]
    avail = W - 2 * M - GAP * 4
    scale = avail / sum(colw)
    colw = [int(c * scale) for c in colw]
    colw[-1] += avail - sum(colw)
    xs = [M]
    for w in colw[:-1]:
        xs.append(xs[-1] + w + GAP)

    cards = [
        (0, 0, 1, "问题 Problem", GREEN, [
            "① 焊点照明被手/烙铁遮挡（行为观察：平均 4.2 次「找光」/20 分钟焊接）",
            "② 台灯占桌面、灯臂僵直不可瞄准（68.25%，n=126）",
            "③ 廉价灯不稳偏斜 61.11%；专业灯 300 元+ 买不起 54.76%",
            "行为证据：13/15 次观察出现「灯头偏移后未复位继续焊」",
            "修订：「需要状态显示」已从痛点删除（实测仅 1.6 次查询）",
        ], "M7"),
        (1, 0, 1, "解决方案 Solution", GREEN, [
            "① 磁吸底座 + 万向柔臂（实测吸附 3.2kg ≥ 2.5kg）",
            "② 无级调光（SY7200A 恒流 + 20kHz PWM，镜头无频闪条纹）",
            "③ LED 状态灯 4 电量 + 2 充电（原 6 颗减为 4 颗）",
            "④ OLED 由「选配」降为「不推广的选配」；新增 NTC 过温提示",
            "修订：减灯珠省 ¥0.4/台，磁吸垫改双色注塑省 ¥1.5/台",
        ], "M9"),
        (2, 0, 1, "独特价值主张 UVP", YELLOW, [
            "给焊接者一双腾出来的手：磁吸固定解放双手、万向悬停指哪照哪、无级调光适配光环境",
            "百元内可得：主线 65 元（区间 59–69），实训套件可自组 49 元",
            "修订 ①：「状态可视」不再作为核心卖点（25 分钟焊接平均查询 1.6 次）",
            "修订 ②：定价由 59–79 元改为 59–69 元主推，PSM 最优价位 62 元",
        ], "M3"),
        (3, 0, 1, "不公平优势 Advantage", YELLOW, [
            "① 渠道关系：电工基地/社团「老带新」网络（每年 300+ 新生接触）",
            "② 实训课程捆绑：工具随课程耗材采买，B 端零获客成本",
            "③ CNIPA 检索（2026-09-25）未发现「磁吸+万向悬停+可换向磁吸位」同类实用新型",
            "修订：删去 V2.0「成熟供应链无断供」（实为执行进度，非壁垒）",
        ], "M6"),
        (4, 0, 1, "客户细分 Segment", YELLOW, [
            "① 主画像：实训课学生（课程强制焊接、每周 ≥3 次、实验室统一采买）——地推转化 34.9%",
            "② DIY 极客/创客社团（C 端，主推套件版）",
            "③ 研发/维修工程师：暂不投入获客资源（线上转化 5.2%）",
            "修订：早期采用者由「三类并列」收敛为「B 端实训 + C 端极客」双画像",
        ], "M8"),
        (0, 1, 3, "关键指标 Metrics", GREEN, [
            "北极星：意向金支付率（首单行为指标）≥ 30% —— 实测 32.3%；辅助：B 端批量续订 ≥2 校/学期、NPS ≥30（实测 30）、30 天留存 ≥40%",
            "修订 ①：原北极星「周活跃焊接时长」样机无联网能力、无采集手段，已替换",
            "修订 ②：原「留存率 45.2%（n=60 短期试点）」不再单列，改为 30 天留存观测项",
        ], "M4"),
        (3, 1, 2, "渠道 Channels", GREEN, [
            "① 实验室/实训场景地推：转化 34.9%，CAC ¥8.6；② B 端实训采买 10 台起：零获客成本（已有 20 台意向 = ¥1,180）",
            "③ 社团/创客空间宣讲 27.1%，CAC ¥11.5；④ 电商平台仅作品牌展示，不做付费投放",
            "修订：放弃「校园 KOL 投放」——实测自然增长 6.8%/周 ≠ 假设 15%，且该渠道 LTV/CAC = 0.83",
        ], "M5"),
        (0, 2, 3, "成本结构 Cost", RED, [
            "固定（一次性）：打样与工装 ¥3,200 + 注塑开模 ¥15,000 + 合规自测 ¥3,000 + 测试设备耗材 ¥1,800 = ¥23,000",
            "人力机会成本：3 人 × 240 人时 = 720 人时，按学生兼职 ¥25/人时折算 ¥18,000（记机会成本，不计现金支出）",
            "单位变动（小批量）：标准版 物料 ¥52.3 + 物流 ¥1.5 + 渠道 ¥1.95 + 售后 ¥1.95 = ¥57.7 → 单位贡献 ¥7.3（11.2%）",
            "修订 ①：原「整机 BOM ≤50 元」被实测证伪——小批量实际 ¥52.3，千片 ¥37.6，万片 ¥29.2",
            "修订 ②：原成本结构未拆物流/渠道/售后三项变动成本，也未计人力成本",
        ], "M1 · M2"),
        (3, 2, 2, "收入来源 Revenue", RED, [
            "四源结构：标准版 65 元、青春版 45 元（39–49）、实训套件版 49 元、B 端实训套装 59 元/台（10 台起）",
            "销量结构假设：B 端 30%/套件 25%/标准版 30%/青春版 15%，加权均价 ¥56.2",
            "小批量单位贡献 ¥7.97 → 保本 2,886 台；量产后 ¥18.67 → 保本 1,232 台（含人力 2,196 台）",
            "修订 ①：原「毛利 ≥40%」证伪（小批 11.2%/量产 33.8%），改为小批 ≥10%、量产 ≥30%、套件 ≥35%",
            "修订 ②：新增 B 端实训采买为主营收来源——零获客成本，且是达成量产规模的现实路径",
        ], "M2 · M8"),
    ]

    def card_lines(items, cw, fsz):
        fs = f(fsz)
        out = []
        for it in items:
            bold = it.startswith("修订") or it.startswith("修订 ①") or it.startswith("行为证据")
            ff = f(fsz, True) if bold else fs
            ls = wrap(d, it, ff, cw - 34)
            out.append((it, ff, ls, bold))
        return out

    img = Image.new("RGB", (W, 1600), "white")
    d = ImageDraw.Draw(img)

    # 先算各卡片所需高度
    need = {}
    for col, row, span, title, color, items, tag in cards:
        cw = sum(colw[col:col + span]) + GAP * (span - 1)
        fsz = 23 if span <= 1 else 24
        lines = card_lines(items, cw, fsz)
        h = 56 + 20 + sum(len(ls) * 31 + 5 for _, _, ls, _ in lines) + 14
        need[(col, row)] = h
    row_span = {0: (0, 1), 1: (2, 3), 2: (3, 4)}  # row -> (first col, last col)
    h_row = {}
    for r in range(3):
        h_row[r] = max(h for (c, rr), h in need.items() if rr == r)
        h_row[r] = max(h_row[r], 300 if r else 480)

    ys = [TOP]
    for r in (0, 1):
        ys.append(ys[-1] + h_row[r] + GAP)
    H = ys[2] + h_row[2] + 26 + 62 + 26
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    d.text((M, 30), "磁吸焊接辅助手电 · 精益画布 V3.0", font=f(50, True), fill=(20, 24, 32))
    d.text((M, 96), "1班C组 · 仿真跑不队   |   颜色编码：绿=已验证成立 · 黄=验证中/部分成立 · 红=已证伪并调整   |   【M#】= 修改依据编号（见正文表 19）",
           font=f(24), fill=GREY)

    for col, row, span, title, color, items, tag in cards:
        x = xs[col]
        cw = sum(colw[col:col + span]) + GAP * (span - 1)
        y = ys[row]
        h = h_row[row]
        fsz = 23 if span <= 1 else 24
        d.rounded_rectangle([x, y, x + cw, y + h], 14, fill=LIGHT, outline=color, width=4)
        d.rounded_rectangle([x, y, x + cw, y + 56], 14, fill=color)
        d.rectangle([x, y + 40, x + cw, y + 56], fill=color)
        tf = f(28, True) if d.textlength(title, font=f(28, True)) <= cw - 140 else f(24, True)
        d.text((x + 16, y + 13), title, font=tf, fill="white")
        if tag:
            tw = d.textlength("【" + tag + "】", font=f(23, True))
            d.text((x + cw - tw - 14, y + 16), "【" + tag + "】", font=f(23, True), fill="white")
        ty = y + 70
        for it, ff, ls, bold in card_lines(items, cw, fsz):
            col_ = (150, 34, 30) if bold else (40, 44, 52)
            for ln in ls:
                d.text((x + 17, ty), ln, font=ff, fill=col_)
                ty += 31
            ty += 5
        d.rectangle([x, y, x + cw, y + h], outline=color, width=4)

    y0 = ys[2] + h_row[2] + 26
    d.rounded_rectangle([M, y0, W - M, y0 + 62], 12, fill=(28, 34, 46))
    d.text((M + 20, y0 + 16),
           "逻辑闭环：问题 → 解决方案 → 独特价值主张 → 客户细分 → 渠道 → 收入来源 →（单位经济反算）→ 成本结构 → 保本销量 → 关键指标",
           font=f(25, True), fill="white")
    img.save(os.path.join(OUT, "图1_精益画布V3.0.png"))
    print(f"canvas ok  {W}x{H}  aspect={W/H:.2f}  行高={h_row}")

# =====================================================================
# 图 3：三代原型对比
# =====================================================================
def proto_compare():
    W, H = 2000, 1000
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 34), "原型三代演进对比（V1.0 → V2.0 → V3.0）", font=f(48, True), fill=(20, 24, 32))
    d.text((50, 100), "注：本图为结构演进示意（尺寸与参数为实测值）；每代实拍照片请插入正文 3.5 节对应位置",
           font=f(25), fill=GREY)
    items = [
        ("V1.0  概念验证（8 月上旬）", (150, 40, 40), [
            "形态：面包板 + 改造 49 元小夜灯 + 手缠胶带磁铁",
            "验证：磁吸固定可行、万向悬停可行",
            "实测：吸附 1.8kg（偏低）、灯头偏移后无复位提醒",
            "问题：无线调光、无状态显示、无外壳，无法演示",
            "成本：约 ¥36（无参考意义）"]),
        ("V2.0  工程样机（8 月下旬）", (200, 130, 20), [
            "形态：PCBA 打样（34 行 56 位号）+ 3D 打印外壳 + N42 磁吸座",
            "改进：SY7200A 恒流 + 20kHz PWM 无频闪；6 颗红色 LED 状态灯",
            "实测：吸附 3.2kg、3000 次弯折漂移 3.8°、灯板 52℃",
            "问题：OLED 宣传与实物 LED 不一致；外壳成本高；状态灯 6 颗冗余",
            "成本：BOM ¥50（预算值）"]),
        ("V3.0  迭代定稿（48 小时迭代后）", (34, 139, 87), [
            "形态：整机 + 硅胶磁吸垫（可换向）+ 万向柔臂标定 + NTC 过温提示",
            "改进：状态灯 6 颗 → 4 颗；OLED 降为不推广选配；磁吸垫改双色注塑",
            "新增：实训套件版（板 + 件，学生自组）形态验证；整机取下即手电演示",
            "实测：吸附 3.2kg、漂移 3.8°、52℃、无频闪条纹、查询覆盖 82%",
            "成本：小批量 BOM 实测 ¥52.3（比预算高 4.6%，已触发定价修订）"]),
    ]
    x = 50
    gap = 24
    w = (W - 100 - 2 * gap) // 3
    for i, (title, color, bullets) in enumerate(items):
        cx = 50 + i * (w + gap)
        d.rounded_rectangle([cx, 150, cx + w, H - 60], 16, fill=LIGHT, outline=color, width=5)
        d.rounded_rectangle([cx, 150, cx + w, 216], 16, fill=color)
        d.rectangle([cx, 196, cx + w, 216], fill=color)
        d.text((cx + 18, 168), title, font=f(28, True), fill="white")
        # 结构示意（简化方块 + 关键标注）
        bx = cx + w // 2
        top = 250
        d.rounded_rectangle([cx + 40, top, cx + w - 40, top + 74], 10, outline=color, width=4)
        label = ["裸板 / 改造小夜灯（无外壳）", "PCBA + 3D 打印外壳 + 磁吸座", "整机 + 万向柔臂 + 可换向磁吸垫 + NTC"][i]
        fsl = f(21)
        for j, ln in enumerate(wrap(d, label, fsl, w - 100)):
            d.text((cx + 52, top + 14 + j * 26), ln, font=fsl, fill=color)
        d.rounded_rectangle([cx + 40, top + 92, cx + w - 40, top + 148], 8, outline=GREY, width=3)
        note = ["吸附 1.8kg（不足）", "吸附 3.2kg · 漂移 3.8° · 52℃", "吸附 3.2kg · 漂移 3.8° · 52℃ · 无频闪"][i]
        for j, ln in enumerate(wrap(d, note, f(19), w - 100)):
            d.text((cx + 52, top + 102 + j * 24), ln, font=f(19), fill=GREY)
        ty = 470
        for b in bullets:
            lead_bold = b.startswith("改进") or b.startswith("实测") or b.startswith("成本")
            fs = f(23, True) if lead_bold else f(23)
            for ln in wrap(d, b, fs, w - 40):
                d.text((cx + 20, ty), ln, font=fs, fill=(30, 34, 42))
                ty += 33
            ty += 12
    # 箭头
    for i in range(2):
        x1 = 50 + (i + 1) * w + i * gap
        d.polygon([(x1 + 4, H // 2 - 12), (x1 + gap - 4, H // 2), (x1 + 4, H // 2 + 12)], fill=GREY)
    img.save(os.path.join(OUT, "图3_原型三代对比图.png"))
    print("proto ok")


# =====================================================================
# matplotlib 图
# =====================================================================
def radar_chart():
    labels = ["识别机会", "创造力", "愿景", "创意评估", "道德与可持续思维"]
    team_pre = [5, 4, 3, 3, 2]
    team_post = [5, 5, 4, 4, 3]
    me_pre = [4, 3, 3, 3, 2]
    me_post = [5, 4, 4, 4, 3]
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    ang += ang[:1]

    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.6), subplot_kw=dict(polar=True))
    for ax, (pre, post, t) in zip(axes, [(team_pre, team_post, "团队（仿真跑不队）"),
                                         (me_pre, me_post, "个体（邵子中）")]):
        a = ang
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(a[:-1])
        ax.set_xticklabels(labels, fontproperties=MSYH, fontsize=13)
        ax.set_ylim(0, 8)
        ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_yticklabels([f"L{i}" for i in range(1, 9)], fontproperties=MSYH, fontsize=9, color="#888")
        for v, c, lab in ((pre, "#8C97A8", "课前"), (post, "#227F57", "课后")):
            vv = v + v[:1]
            ax.plot(a, vv, color=c, linewidth=2.6, label=lab)
            ax.fill(a, vv, color=c, alpha=0.22)
        ax.set_title(t, fontproperties=MSYHB, fontsize=15, pad=22)
        ax.legend(loc="upper right", bbox_to_anchor=(1.18, 1.12), prop=MSYH, fontsize=11)
    fig.suptitle("能力发展雷达图（欧盟创业能力框架「想法与机会」领域 5 项能力）",
                 fontproperties=MSYHB, fontsize=17, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图2_能力发展雷达图.png"), dpi=190, bbox_inches="tight")
    print("radar ok")


def unit_econ_fig():
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.4))
    # 左：四款产品单位经济（量产后）
    rows = ECON["量产后（1k 片以上）"]["rows"]
    names = [r["name"] for r in rows]
    y = np.arange(len(rows))
    mat = [r["material"] for r in rows]
    oth = [r["var"] - r["material"] for r in rows]
    con = [r["contrib"] for r in rows]
    ax = axes[0]
    ax.barh(y, mat, color="#5B7DB1", label="物料成本")
    ax.barh(y, oth, left=mat, color="#A9B7CB", label="物流+渠道+售后")
    ax.barh(y, con, left=[m + o for m, o in zip(mat, oth)], color="#227F57", label="单位贡献")
    for i, (m_, o_, c_, p_) in enumerate(zip(mat, oth, con, [r["price"] for r in rows])):
        ax.text(m_ + o_ + c_ + 1.0, i, f"售价 {p_} 元 · 贡献 {c_} 元（{c_/p_*100:.1f}%）",
                va="center", fontproperties=MSYH, fontsize=10)
    ax.set_yticks(y); ax.set_yticklabels(names, fontproperties=MSYH, fontsize=12)
    ax.set_xlim(0, 100); ax.set_xlabel("元 / 台", fontproperties=MSYH, fontsize=11)
    ax.set_title("单位经济结构（量产后，1k 片以上）", fontproperties=MSYHB, fontsize=14)
    ax.legend(prop=MSYH, fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=3)
    ax.grid(axis="x", alpha=0.25)

    # 右：保本销量
    ax = axes[1]
    small = ECON["小批量（200 台）"]; bulk = ECON["量产后（1k 片以上）"]
    labels = ["小批量定价\n（单位贡献 ¥7.97）", "量产后定价\n（单位贡献 ¥18.67）"]
    be_cash = [small["be"], bulk["be"]]
    be_labor = [small["be_with_labor"], bulk["be_with_labor"]]
    x = np.arange(2); wd = 0.34
    b1 = ax.bar(x - wd / 2, be_cash, wd, color="#227F57", label="仅计现金固定成本 ¥23,000")
    b2 = ax.bar(x + wd / 2, be_labor, wd, color="#C0392F", label="含人力机会成本 ¥18,000")
    for rect, v in list(zip(b1, be_cash)) + list(zip(b2, be_labor)):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 60, f"{v:,} 台",
                ha="center", fontproperties=MSYH, fontsize=12)
    ax.axhline(3100, color="#D09414", linestyle="--", linewidth=2)
    ax.text(1.35, 3180, "3 年 SOM 预期 3,100 台", color="#A07410", fontproperties=MSYH, fontsize=11.5)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontproperties=MSYH, fontsize=11.5)
    ax.set_ylabel("盈亏平衡销量（台）", fontproperties=MSYH, fontsize=11)
    ax.set_title("盈亏平衡销量测算", fontproperties=MSYHB, fontsize=14)
    ax.set_ylim(0, 5900)
    ax.legend(prop=MSYH, fontsize=10.5)
    ax.grid(axis="y", alpha=0.25)
    fig.suptitle("算经济账：单位经济结构与盈亏平衡", fontproperties=MSYHB, fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图4_单位经济与盈亏平衡.png"), dpi=190, bbox_inches="tight")
    print("econ fig ok")


def competitor_fig():
    # 归一化 1-5 分：价格可达性(越便宜越高)、照度、光斑聚焦、瞄准自由度、空间占用
    data = {}
    lx = {c[0]: c[2] for c in COMPETITORS}
    spot = {c[0]: c[3] for c in COMPETITORS}
    free = {c[0]: c[4] for c in COMPETITORS}
    space = {c[0]: c[5] for c in COMPETITORS}
    price = {"传统台灯": 3.4, "廉价便携灯": 4.4, "专业工业灯": 1.6, "磁吸焊接辅助手电（本方案）": 4.0}
    for name in lx:
        data[name] = [price[name],
                      round(min(5, lx[name] / 1100 * 5), 1),
                      round(5 - (spot[name] - 6) / (18 - 6) * 4, 1),
                      free[name], space[name]]
    dims = ["价格可达性", "照度（20cm）", "光斑聚焦度", "瞄准自由度", "空间占用（5=零占位）"]
    x = np.arange(len(dims)); wd = 0.2
    fig, ax = plt.subplots(figsize=(15.5, 6.6))
    colors = ["#8C97A8", "#C9A227", "#5B7DB1", "#227F57"]
    for i, (name, vals) in enumerate(data.items()):
        bars = ax.bar(x + (i - 1.5) * wd, vals, wd, label=name, color=colors[i])
        for rect, v in zip(bars, vals):
            ax.text(rect.get_x() + rect.get_width() / 2, v + 0.08, f"{v}",
                    ha="center", fontproperties=MSYH, fontsize=9.5)
    raw = "；".join([f"{c[0]}：{c[2]} lux / 光斑 {c[3]} cm" for c in COMPETITORS])
    ax.set_xticks(x); ax.set_xticklabels(dims, fontproperties=MSYH, fontsize=12)
    ax.set_ylim(0, 6.0); ax.set_ylabel("归一化得分（1–5 分）", fontproperties=MSYH, fontsize=11)
    ax.set_title("竞品量化对比矩阵（实测值归一化，n=4 款 × 各测 3 次取均值）",
                 fontproperties=MSYHB, fontsize=15)
    ax.legend(prop=MSYH, fontsize=11, ncol=2)
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.0, -0.20, "实测原始值（手机照度计 App + 卷尺，距光源 20 cm）：" + raw,
            transform=ax.transAxes, fontproperties=MSYH, fontsize=10.5, color="#555")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图5_竞品量化对比.png"), dpi=190, bbox_inches="tight")
    print("comp fig ok")


def channel_fig():
    fig, ax = plt.subplots(figsize=(15.0, 6.0))
    names = [c["name"] for c in CH]
    rate = [c["rate"] * 100 for c in CH]
    cac = [c["cac"] for c in CH]
    x = np.arange(len(CH))
    bars = ax.bar(x, rate, 0.45, color=["#227F57", "#4E9B72", "#C0392F"], label="留资转化率（%）")
    for rect, v, c in zip(bars, rate, cac):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 0.9, f"{v:.1f}%",
                ha="center", fontproperties=MSYH, fontsize=13)
    ax.set_xticks(x); ax.set_xticklabels(names, fontproperties=MSYH, fontsize=12)
    ax.set_ylabel("留资转化率（%）", fontproperties=MSYH, fontsize=11)
    ax.set_ylim(0, 52)
    ax2 = ax.twinx()
    ax2.plot(x, cac, "o--", color="#2C5AA0", linewidth=2.4, markersize=9, label="单留资获客成本 CAC（元）")
    for i, v in enumerate(cac):
        ax2.text(i, v + 2.4, f"CAC ¥{v}", color="#2C5AA0", fontproperties=MSYH, fontsize=12,
                 ha="center", bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=1.6))
    ax2.axhline(LTV, color="#D09414", linestyle=":", linewidth=2.4)
    ax2.text(0.02, LTV + 1.4, f"LTV ¥{LTV}（量产后单位贡献 ×1.2 复购）",
             color="#A07410", fontproperties=MSYH, fontsize=11, ha="left",
             bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=1.6))
    ax2.set_ylabel("CAC / LTV（元）", fontproperties=MSYH, fontsize=11)
    ax2.set_ylim(0, 46)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, prop=MSYH, fontsize=11, loc="upper center")
    ax.set_title("三渠道并行获客测试：转化率与单客经济（LTV/CAC：地推 3.07 · 社团 2.30 · 线上 0.83）",
                 fontproperties=MSYHB, fontsize=14.5)
    ax.grid(axis="y", alpha=0.22)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图6_渠道转化与CAC.png"), dpi=190, bbox_inches="tight")
    print("channel fig ok")


def cost_value_fig():
    # (功能, 单位成本投入(元/台), 用户价值评分, 研发工时, 标签偏移(dx, dy))
    items = [
        ("磁吸底座机构", 10.0, 4.8, 40, (-30, 24)),
        ("万向柔性臂", 12.0, 4.7, 30, (10, 24)),
        ("无级调光（恒流+PWM）", 6.0, 4.5, 60, (-52, 26)),
        ("Type-C 充电与电池管理", 6.7, 4.2, 35, (24, 22)),
        ("NTC 过温提示", 0.5, 3.90, 16, (16, -36)),
        ("整机取下即手电（结构复用）", 0.6, 4.02, 6, (16, 22)),
        ("LED 电量/充电指示（4 颗）", 3.1, 3.40, 20, (0, -36)),
        ("环境感知自动调光（AI 落点）", 2.5, 3.62, 60, (18, 22)),
        ("OLED 状态屏（选配）", 5.0, 2.80, 45, (18, -30)),
        ("OPC 状态数据接口（预研）", 0.6, 2.52, 24, (18, -30)),
    ]
    fig, ax = plt.subplots(figsize=(15.2, 7.0))
    for name, cost, val, hours, off in items:
        color = "#227F57" if val >= 4.0 else ("#D09414" if val >= 3.3 else "#C0392F")
        ax.scatter(cost, val, s=hours * 16, color=color, alpha=0.65, edgecolors="white", linewidths=1.6)
        ha = "left" if off[0] > 12 else ("right" if off[0] < -12 else "center")
        ax.annotate(f"{name}\n({hours} 人时)", (cost, val), textcoords="offset points",
                    xytext=off, ha=ha, fontproperties=MSYH, fontsize=11)
    ax.axhline(3.5, color="#8C97A8", linestyle="--", linewidth=1.4)
    ax.axvline(4.0, color="#8C97A8", linestyle="--", linewidth=1.4)
    ax.text(0.2, 5.34, "低投入 · 高价值 → 必做", fontproperties=MSYH, fontsize=12, color="#227F57")
    ax.text(6.6, 5.34, "高投入 · 高价值 → 保核心（研发工时优先项）", fontproperties=MSYH, fontsize=12, color="#227F57")
    ax.text(0.2, 2.06, "低投入 · 低价值 → 观察/预研", fontproperties=MSYH, fontsize=12, color="#C0392F")
    ax.text(6.6, 2.06, "高投入 · 低价值 → 砍掉或降级", fontproperties=MSYH, fontsize=12, color="#C0392F")
    ax.set_xlabel("单位成本投入（元/台，含研发工时按 300 台摊薄）", fontproperties=MSYH, fontsize=12)
    ax.set_ylabel("用户价值评分（1–5 分，实测/访谈）", fontproperties=MSYH, fontsize=12)
    ax.set_xlim(-0.25, 14.3); ax.set_ylim(1.92, 5.55)
    ax.set_title("成本-价值平衡图（气泡面积 = 研发工时投入）", fontproperties=MSYHB, fontsize=15)
    ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图7_成本价值平衡图.png"), dpi=190, bbox_inches="tight")
    print("cost-value fig ok")


def feedback_fig():
    fig, ax = plt.subplots(figsize=(11.6, 4.9))
    srcs = ["陪审团", "教师补充点评", "团队互评记录"]
    p0 = [2, 1, 0]; p1 = [2, 2, 1]; p2 = [2, 1, 1]; p3 = [1, 1, 0]
    x = np.arange(len(srcs)); wd = 0.24
    for i, (vals, lab, col) in enumerate([(p0, "P0 致命", "#C0392F"), (p1, "P1 严重", "#D09414"),
                                          (p2, "P2 一般", "#5B7DB1"), (p3, "P3 优化建议", "#8C97A8")]):
        ax.bar(x + (i - 1.5) * wd, vals, wd, label=lab, color=col)
        for xi, v in zip(x + (i - 1.5) * wd, vals):
            if v:
                ax.text(xi, v + 0.05, str(v), ha="center", fontproperties=MSYH, fontsize=11)
    ax.set_xticks(x); ax.set_xticklabels(srcs, fontproperties=MSYH, fontsize=12.5)
    ax.set_ylabel("反馈条目数", fontproperties=MSYH, fontsize=11)
    ax.set_ylim(0, 3.0); ax.set_yticks([0, 1, 2, 3])
    ax.set_title("评审反馈来源与优先级分布（共 14 条：P0 3 条 · P1 5 条 · P2 4 条 · P3 2 条）",
                 fontproperties=MSYHB, fontsize=14)
    ax.legend(prop=MSYH, fontsize=11)
    ax.grid(axis="y", alpha=0.22)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图8_反馈来源与优先级分布.png"), dpi=190, bbox_inches="tight")
    print("feedback fig ok")


if __name__ == "__main__":
    canvas_v3()
    proto_compare()
    radar_chart()
    unit_econ_fig()
    competitor_fig()
    channel_fig()
    cost_value_fig()
    feedback_fig()
    print("ALL FIGS DONE ->", OUT)
