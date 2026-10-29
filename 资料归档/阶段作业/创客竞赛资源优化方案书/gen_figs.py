# -*- coding: utf-8 -*-
"""《资源优化方案书》全部配图（PIL 画布 + matplotlib 图表）"""
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

import data_res as D

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/msyh.ttc"
FONTB = "C:/Windows/Fonts/msyhbd.ttc"
MSYH = FontProperties(fname=FONT)
MSYHB = FontProperties(fname=FONTB)
plt.rcParams["axes.unicode_minus"] = False

GREEN = "#228B57"
YELLOW = "#D09414"
RED = "#C03A33"
CV = {"绿": GREEN, "黄": YELLOW, "红": RED}
GREY = "#5A606A"
LIGHT = "#F7F8FA"
BLUE = "#2C5AA0"
PURPLE = "#6C4C9E"


def f(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)


import re
_TOKEN = re.compile(r"[A-Za-z0-9%¥．.\-+/×≥≤<>（）()\[\]]+|.", re.S)


def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for tk in _TOKEN.findall(text):
        if tk == "\n":
            lines.append(cur); cur = ""; continue
        cand = cur + tk
        if not cur or draw.textlength(cand, font=font) <= maxw:
            cur = cand
        else:
            lines.append(cur); cur = tk
    if cur:
        lines.append(cur)
    fixed = []
    for ln in lines:
        if fixed and len(ln) <= 1 and ln in "，。；、）】":
            fixed[-1] += ln
        else:
            fixed.append(ln)
    return fixed


# =====================================================================
# 图 1：精益画布 V4.0
# =====================================================================
def canvas_v4():
    W, M, GAP = 2060, 40, 14
    avail = W - 2 * M - GAP * 4
    cw = avail / 5
    ft, fb = f(25, True), f(19)
    LAYOUT = [   # (块名, 列, 行, 跨列)
        ("问题 Problem", 0, 0, 1), ("解决方案 Solution", 1, 0, 1), ("独特价值主张 UVP", 2, 0, 1),
        ("不公平优势 Advantage", 3, 0, 1), ("客户细分 Segment", 4, 0, 1),
        ("关键指标 Metrics", 0, 1, 2), ("渠道 Channels", 2, 1, 3),
        ("成本结构 Cost", 0, 2, 3), ("收入来源 Revenue", 3, 2, 2),
    ]
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    # 计算每块高度
    heights = {}
    for name, col, row, span in LAYOUT:
        color, bullets = D.CANVAS_V4[name]
        w = cw * span + GAP * (span - 1)
        h = 46
        for b in bullets:
            h += len(wrap(probe, b, fb, w - 30)) * 28 + 8
        heights[name] = h + 16
    row_h = [max(heights[n] for n, c, r, s in LAYOUT if r == rr) for rr in range(3)]
    TOP = 152
    H = TOP + sum(row_h) + GAP * 2 + 60
    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 112], fill=BLUE)
    dr.text((M, 26), "磁吸焊接辅助手电 · 精益画布 V4.0", font=f(40, True), fill=(255, 255, 255))
    dr.text((M, 74), "“资源”领域迭代验证后版本　|　绿 = 已验证　黄 = 验证中 / 部分成立　红 = 已证伪并调整　|　括号内为缺陷编号或验证数据",
            font=f(21), fill=(226, 234, 246))
    ys = [TOP]
    for r in range(2):
        ys.append(ys[-1] + row_h[r] + GAP)
    for name, col, row, span in LAYOUT:
        cname, bullets = D.CANVAS_V4[name]
        color = CV[cname]
        x = M + col * (cw + GAP)
        w = cw * span + GAP * (span - 1)
        y, h = ys[row], row_h[row]
        dr.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(252, 253, 255), outline=(206, 213, 224), width=2)
        dr.rounded_rectangle([x, y, x + w, y + 42], radius=10, fill=color)
        dr.rectangle([x, y + 30, x + w, y + 42], fill=color)
        dr.text((x + 14, y + 9), name, font=ft, fill=(255, 255, 255))
        yy = y + 50
        for b in bullets:
            for ln in wrap(dr, b, fb, w - 30):
                dr.text((x + 15, yy), ln, font=fb, fill=(38, 44, 56))
                yy += 28
            yy += 8
    dr.text((M, H - 44), "版本：V4.0（基于 V3.0 完成 9 处实质性修订，逐处依据见方案书表 12）", font=f(20), fill=GREY)
    p = os.path.join(OUT, "图1_精益画布V4.0.png")
    img.save(p, dpi=(200, 200))
    print("saved", p, img.size)


# =====================================================================
# 图 2：缺陷优先级 × 五维归类
# =====================================================================
def fig_defects():
    dims = D.DIMENSIONS
    prios = ["P0", "P1", "P2", "P3"]
    colors = {"P0": "#C03A33", "P1": "#D09414", "P2": "#7A9CC6", "P3": "#9AA4B2"}
    mat = {d: {p: 0 for p in prios} for d in dims}
    for _, _, _, dim, prio, _, _ in D.DEFECTS:
        mat[dim][prio] += 1
    fig, ax = plt.subplots(figsize=(9.2, 4.4), dpi=200)
    x = np.arange(len(dims))
    bottom = np.zeros(len(dims))
    for p in prios:
        vals = np.array([mat[d][p] for d in dims], dtype=float)
        ax.bar(x, vals, 0.56, bottom=bottom, label=p, color=colors[p], edgecolor="white", linewidth=1.2)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v > 0:
                ax.text(xi, b + v / 2, f"{int(v)}", ha="center", va="center", color="white",
                        fontproperties=MSYHB, fontsize=11)
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels([f"{d}" for d in dims], fontproperties=MSYHB, fontsize=12)
    ax.set_ylabel("缺陷条数", fontproperties=MSYH, fontsize=11)
    ax.set_title(f"关键缺陷清单：五维资源管理模型归类 × P0–P3 优先级（共 {len(D.DEFECTS)} 条）",
                 fontproperties=MSYHB, fontsize=13, pad=12)
    ax.legend(prop=MSYH, fontsize=10, ncol=4, loc="upper right", frameon=False)
    ax.set_ylim(0, bottom.max() + 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", ls=":", color="#CCCCCC")
    ax.set_axisbelow(True)
    for xi, d in enumerate(dims):
        ax.text(xi, -0.42, f"{d}", ha="center", fontproperties=MSYH, fontsize=8.5, color=GREY_HEX)
    fig.tight_layout()
    p = os.path.join(OUT, "图2_缺陷五维与优先级分布.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


GREY_HEX = "#5A606A"


# =====================================================================
# 图 3：资源投入结构（瀑布）与全成本摊薄
# =====================================================================
def fig_resource_waterfall():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.3), dpi=200,
                                   gridspec_kw={"width_ratios": [1.25, 1]})
    labels = ["现金支出\n（显性）", "人力机会成本\n（隐性）", "= 资源总投入", "外部关系\n（零现金）"]
    vals = [D.CASH_SPENT, D.LABOR_COST, D.TOTAL_RESOURCE_COST, 1700]
    kind = ["bar", "bar", "total", "ghost"]
    cum = 0
    for i, (lb, v, k) in enumerate(zip(labels, vals, kind)):
        if k == "bar":
            ax1.bar(i, v, 0.55, color="#2C5AA0" if i == 0 else "#6C4C9E", edgecolor="white")
            ax1.text(i, v + 300, f"¥{v:,.0f}", ha="center", fontproperties=MSYHB, fontsize=11)
            ax1.text(i, v / 2, f"{v / D.TOTAL_RESOURCE_COST * 100:.1f}%", ha="center", color="white",
                     fontproperties=MSYHB, fontsize=11)
            cum += v
        elif k == "total":
            ax1.bar(i, cum, 0.55, color="#22303F", edgecolor="white")
            ax1.text(i, cum + 300, f"¥{cum:,.0f}", ha="center", fontproperties=MSYHB, fontsize=11)
        else:
            ax1.bar(i, v, 0.55, color="#C9D3DF", edgecolor="#8E9AA8", hatch="//")
            ax1.text(i, v + 300, "等值 ¥1,700", ha="center", fontproperties=MSYH, fontsize=10, color=GREY_HEX)
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, fontproperties=MSYH, fontsize=9.5)
    ax1.set_ylabel("金额（元）", fontproperties=MSYH, fontsize=10.5)
    ax1.set_title("资源投入结构：隐性成本占 78.7%（本轮折算）", fontproperties=MSYHB, fontsize=12.5, pad=10)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(axis="y", ls=":", color="#CCCCCC"); ax1.set_axisbelow(True)

    stages = ["中期口径\n157 条", "调整期\n176 条", "本轮末\n218 条"]
    per = [D.COST_PER_DATA, D.MID_ADJ_COST / D.MID_ADJ_DATA, D.NOW_COST / D.NOW_DATA]
    ax2.plot(range(3), per, "-o", color=RED, lw=2.4, ms=8, label="全成本 / 条数据")
    for i, v in enumerate(per):
        ax2.annotate(f"¥{v:.1f}", (i, v), textcoords="offset points", xytext=(0, 10),
                     ha="center", fontproperties=MSYHB, fontsize=11, color=RED)
    ax2.axhline(50, ls="--", color=GREEN, lw=1.6)
    ax2.text(2.05, 50.6, "目标 ≤¥50", ha="right", fontproperties=MSYH, fontsize=9.5, color=GREEN)
    ax2.set_xticks(range(3)); ax2.set_xticklabels(stages, fontproperties=MSYH, fontsize=9.5)
    ax2.set_ylabel("元 / 条有效验证数据", fontproperties=MSYH, fontsize=10.5)
    ax2.set_title("资源北极星：全成本 / 条数据（增量成本 ¥11.8 / 条）", fontproperties=MSYHB, fontsize=12.5, pad=10)
    ax2.set_ylim(40, 76)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", ls=":", color="#CCCCCC"); ax2.set_axisbelow(True)
    fig.tight_layout()
    p = os.path.join(OUT, "图3_资源投入与效率.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# =====================================================================
# 图 4：资源缺口影响-修复成本四象限
# =====================================================================
def fig_gap_quadrant():
    fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=200)
    xs = [c / 1000 for c in D.GAP_COST_DIFF]      # 千元
    ys = [g[2] for g in D.GAPS]
    names = [g[0] for g in D.GAPS]
    acts = ["重配资源（组合式获客 + B 端）", "设投模门槛（暂不投入）", "立即做（设专职 R）", "降级为观测项"]
    ax.axvline(1.5, ls="--", color="#9AA4B2", lw=1.2)
    ax.axhline(3.5, ls="--", color="#9AA4B2", lw=1.2)
    ax.add_patch(plt.Rectangle((0, 3.5), 1.5, 2.0, color="#FBEAE8", zorder=0))
    ax.add_patch(plt.Rectangle((1.5, 3.5), 2.6, 2.0, color="#FDF3E0", zorder=0))
    ax.add_patch(plt.Rectangle((0, 1.2), 1.5, 2.3, color="#EAF4EE", zorder=0))
    colors = ["#C03A33", "#D09414", "#228B57", "#9AA4B2"]
    for i, (x, y, n, a, c) in enumerate(zip(xs, ys, names, acts, colors)):
        ax.scatter(x, y, s=760, color=c, zorder=3, edgecolor="white", linewidth=2)
        ax.text(x, y, f"G-{i+1}", color="white", ha="center", va="center", fontproperties=MSYHB, fontsize=12, zorder=4)
        ax.annotate(f"{n.split(' ')[1] if ' ' in n else n}\n→ {a}", (x, y), textcoords="offset points",
                    xytext=((16, -30) if i == 0 else (16, 12) if i == 1 else (16, -28) if i == 2 else (16, -26)),
                    fontproperties=MSYH, fontsize=9.5, color="#333333")
    ax.set_xlabel("修复成本（千元，含工时折价 ¥25/人时）", fontproperties=MSYH, fontsize=11)
    ax.set_ylabel("对项目成功的影响严重性（1–5）", fontproperties=MSYH, fontsize=11)
    ax.set_title("资源缺口影响-修复成本四象限（P0 优先级重排依据）", fontproperties=MSYHB, fontsize=13, pad=12)
    ax.set_xlim(-0.35, 4.3); ax.set_ylim(1.15, 5.95)
    ax.text(0.05, 5.62, "高影响 · 低成本 → 立即做", fontproperties=MSYHB, fontsize=10, color=RED)
    ax.text(1.65, 5.62, "高影响 · 高成本 → 设门槛", fontproperties=MSYHB, fontsize=10, color="#B8820F")
    ax.text(0.05, 1.28, "低影响 · 低成本 → 顺手做", fontproperties=MSYHB, fontsize=10, color=GREEN)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    p = os.path.join(OUT, "图4_资源缺口四象限.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# =====================================================================
# 图 5：创新核算仪表盘（基准 → 调整 → 当前）
# =====================================================================
def fig_dashboard():
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 5.6), dpi=200)
    xs = [0, 1, 2]
    for ax, (name, vals, target, tlabel) in zip(axes.ravel(), D.DASH_NUM):
        up_good = "CAC" not in name and "成本" not in name
        col = "#228B57" if ((vals[-1] >= vals[0]) == up_good) else "#D09414"
        ax.plot(xs, vals, "-o", color=col, lw=2.2, ms=7)
        for i, v in enumerate(vals):
            ax.annotate(f"{v:,.1f}" if v < 100 else f"{v:,.0f}", (i, v), textcoords="offset points",
                        xytext=(0, 9), ha="center", fontproperties=MSYHB, fontsize=9.5, color=col)
        lo, hi = min(vals + [target]), max(vals + [target])
        pad = (hi - lo) * 0.45 + (1.2 if hi - lo < 3 else 0.6)
        ax.set_ylim(lo - pad, hi + pad)
        ax.axhline(target, ls="--", color="#9AA4B2", lw=1.4)
        ax.text(0.02, target, tlabel, transform=ax.get_yaxis_transform(), va="bottom",
                fontproperties=MSYH, fontsize=8.6, color="#5A606A")
        ax.set_xticks(xs); ax.set_xticklabels(D.DASH_STAGES, fontproperties=MSYH, fontsize=9.5)
        ax.set_title(name, fontproperties=MSYHB, fontsize=11.5, pad=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", ls=":", color="#DDDDDD"); ax.set_axisbelow(True)
    fig.suptitle("更新后的创新核算仪表盘：基准 → 调整 → 当前（虚线为阈值 / 目标）",
                 fontproperties=MSYHB, fontsize=13.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    p = os.path.join(OUT, "图5_创新核算仪表盘.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# =====================================================================
# 图 6：渠道资源效率与资源组合增值
# =====================================================================
def fig_channels():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.2), dpi=200,
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    ch = ["实验室地推", "社团宣讲", "线上投放", "B 端采买"]
    imp = [63, 48, 210, 20]
    lead = [22, 13, 11, 20]
    cac = [7.4, 11.5, 31.8, 0]
    x = np.arange(len(ch))
    ax1.bar(x - 0.2, imp, 0.4, color="#C9D3DF", label="曝光人数", edgecolor="white")
    ax1.bar(x + 0.2, lead, 0.4, color=BLUE, label="留资 / 意向数", edgecolor="white")
    ax1.set_xticks(x); ax1.set_xticklabels(ch, fontproperties=MSYH, fontsize=10)
    ax1.set_ylabel("人数", fontproperties=MSYH, fontsize=10.5)
    for i, c in enumerate(cac):
        txt = "零获客成本" if c == 0 else f"CAC ¥{c}"
        ax1.text(i, max(imp[i], lead[i]) + 9, txt, ha="center", fontproperties=MSYHB, fontsize=9.5,
                 color="#228B57" if c <= 15 else "#C03A33")
    ax1.set_ylim(0, 290)
    ax1.legend(prop=MSYH, fontsize=9.5, frameon=False, loc="upper left")
    ax1.set_title("分渠道获客与 CAC（线上 LTV/CAC = 0.83 已停投）", fontproperties=MSYHB, fontsize=12, pad=10)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(axis="y", ls=":", color="#DDDDDD"); ax1.set_axisbelow(True)

    grp = ["借设备\n（单独）", "地推\n（单独）", "线上投放\n（单独）", "三者组合\n（工作坊）"]
    rate = [3.2, 1.2, 1.0, 3.6]
    cols = ["#C9D3DF", "#C9D3DF", "#C9D3DF", "#228B57"]
    ax2.bar(range(4), rate, 0.55, color=cols, edgecolor="white")
    for i, v in enumerate(rate):
        ax2.text(i, v + 0.09, f"{v}×", ha="center", fontproperties=MSYHB, fontsize=11,
                 color="#228B57" if i == 3 else GREY_HEX)
    ax2.axhline(1.0, ls="--", color="#9AA4B2", lw=1.2)
    ax2.text(3.45, 0.84, "增值率 1.0 = 不亏不赚基准", ha="right", va="center", fontproperties=MSYH, fontsize=8.6, color=GREY_HEX)
    ax2.set_xticks(range(4)); ax2.set_xticklabels(grp, fontproperties=MSYH, fontsize=9.5)
    ax2.set_ylabel("资源增值率（产出市场替代价 ÷ 投入）", fontproperties=MSYH, fontsize=10)
    ax2.set_title("资源组合增值实验：协同系数 2.0 > 1", fontproperties=MSYHB, fontsize=12, pad=10)
    ax2.set_ylim(0, 4.3)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", ls=":", color="#DDDDDD"); ax2.set_axisbelow(True)
    fig.tight_layout()
    p = os.path.join(OUT, "图6_渠道与资源组合增值.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# =====================================================================
# 图 7：RACI-V 调整前后对比
# =====================================================================
def fig_raci():
    names = ["邵子中", "李昊桐", "姜亚楷"]
    cvals = {"R": 3, "A": 4, "C": 2, "S": 1.5, "I": 1}
    def build(rows):
        m = np.zeros((len(rows), 3))
        for i, r in enumerate(rows):
            for j, cell in enumerate(r[1:4]):
                key = cell[0] if cell else ""
                m[i, j] = cvals.get(key, 0)
        return m
    fig, axes = plt.subplots(1, 2, figsize=(15.0, 4.8), dpi=200)
    for ax, rows, tag in zip(axes, [D.RACI_BEFORE, D.RACI_AFTER], ["调整前（中期评审）", "调整后（本单元末）"]):
        m = build(rows)
        ax.imshow(m, cmap="Blues", vmin=0, vmax=4.4, aspect="auto")
        for i, r in enumerate(rows):
            for j, cell in enumerate(r[1:4]):
                txt = cell.replace("（兼岗）", "") if cell else "—"
                ax.text(j, i, txt, ha="center", va="center", fontproperties=MSYHB, fontsize=11,
                        color="white" if m[i, j] >= 3 else "#22303F")
            v = r[4].split("（")[0]
            ax.text(3.15, i, "V：" + v, ha="left", va="center", fontproperties=MSYH, fontsize=9.5, color="#2C5AA0")
        ax.set_xticks([0, 1, 2, 4.4])
        ax.set_xticklabels(names + ["V 验证者\n（外部）"], fontproperties=MSYHB, fontsize=10.5)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([r[0].replace("（", "\n（") for r in rows], fontproperties=MSYH, fontsize=9)
        ax.set_title(tag, fontproperties=MSYHB, fontsize=12, pad=10)
        ax.set_xlim(-0.5, 6.0)
        ax.set_xticks(np.arange(-.5, 3, 1), minor=True)
        ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
        ax.grid(which="minor", color="white", lw=2)
        ax.tick_params(which="minor", length=0)
    axes[0].set_xlabel("R 执行 · A 最终责任 · C 咨询 · S 支持 · V 验证者（对成果给出独立验证意见或提供支持性资源的外部相关方）",
                       fontproperties=MSYH, fontsize=9.5)
    fig.suptitle("RACI-V 调整前后对比：新增 3 项资源类任务、3 次角色动态调整",
                 fontproperties=MSYHB, fontsize=13, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = os.path.join(OUT, "图7_RACIV调整对比.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# =====================================================================
# 图 8：能力发展雷达图（“资源”领域五项能力）
# =====================================================================
def fig_radar():
    labels = [a[0].replace("① ", "").replace("② ", "").replace("③ ", "").replace("④ ", "").replace("⑤ ", "") for a in D.ABILITIES]
    lv = lambda s: float(s[1:])
    pre_i = [lv(a[1]) for a in D.ABILITIES]
    pre_t = [lv(a[2]) for a in D.ABILITIES]
    post_i = [lv(a[3]) for a in D.ABILITIES]
    post_t = [lv(a[4]) for a in D.ABILITIES]
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    ang += ang[:1]
    close = lambda v: v + v[:1]
    fig = plt.figure(figsize=(7.6, 6.6), dpi=200)
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    series = [("课前 · 个体", close(pre_i), "#9AA4B2", "--", "o"),
              ("课前 · 团队", close(pre_t), "#C9A227", "--", "s"),
              ("课后 · 个体", close(post_i), BLUE_HEX, "-", "o"),
              ("课后 · 团队", close(post_t), GREEN_HEX2, "-", "s")]
    for lb, v, c, ls, mk in series:
        ax.plot(ang, v, ls, color=c, lw=2.0, marker=mk, ms=6, label=lb)
        ax.fill(ang, v, color=c, alpha=0.10)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontproperties=MSYHB, fontsize=11.5)
    ax.set_ylim(1, 8); ax.set_yticks([2, 3, 4, 5, 6, 7, 8])
    ax.set_yticklabels(["L2", "L3", "L4", "L5", "L6", "L7", "L8"], fontproperties=MSYH, fontsize=9, color=GREY_HEX)
    ax.set_title("能力发展雷达图——“资源”领域五项能力（课前 → 课后，刻度 L1–L8）",
                 fontproperties=MSYHB, fontsize=13, pad=38)
    ax.legend(prop=MSYH, fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False)
    fig.tight_layout()
    p = os.path.join(OUT, "图8_能力发展雷达图.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


BLUE_HEX = "#2C5AA0"
GREEN_HEX2 = "#228B57"


if __name__ == "__main__":
    canvas_v4()
    fig_defects()
    fig_gap_quadrant()
    fig_resource_waterfall()
    fig_dashboard()
    fig_channels()
    fig_raci()
    fig_radar()
    print("ALL FIGURES DONE")
