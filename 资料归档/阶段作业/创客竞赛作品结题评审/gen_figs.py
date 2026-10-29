# -*- coding: utf-8 -*-
"""结题评审：配图（三阶段趋势 / 计划vs实际 / 认知迭代图谱 / 贡献值与效能）"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageDraw, ImageFont
import data2 as D

OUT = os.path.dirname(os.path.abspath(__file__))
MSYH = FontProperties(fname="C:/Windows/Fonts/msyh.ttc")
MSYHB = FontProperties(fname="C:/Windows/Fonts/msyhbd.ttc")
plt.rcParams["axes.unicode_minus"] = False
G, Y, R, B, GR = "#227F57", "#D09414", "#C0392F", "#2C5AA0", "#8C97A8"


def trend():
    fig, axes = plt.subplots(1, 4, figsize=(16.2, 4.9))
    items = [
        ("有效用户验证数据（份/次）", [5, 157, 312], 300, "份"),
        ("用户任务完成率（%）", [0, 50, 78], 85, "%"),
        ("意向金支付率（%）", [0, 32.3, 37.3], 30, "%"),
        ("连续工况温升（℃）", [0, 52, 49], 60, "℃"),
    ]
    for ax, (title, vals, plan, unit) in zip(axes, items):
        labels = ["选题", "中期", "结题"]
        cols = [GR, Y, G]
        bars = ax.bar(labels, vals, 0.52, color=cols)
        for b, v in zip(bars, vals):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.04,
                        f"{v}{unit}", ha="center", fontproperties=MSYH, fontsize=12)
        ax.axhline(plan, color=R, linestyle="--", linewidth=1.8)
        ax.text(2.42, plan, f"计划 {plan}{unit}", color=R, fontproperties=MSYH, fontsize=9.5, va="center")
        ax.set_title(title, fontproperties=MSYHB, fontsize=12.5)
        ax.set_ylim(0, max(max(vals), plan) * 1.34 + 2)
        ax.set_xlim(-0.6, 3.6)
        for lb in ax.get_xticklabels():
            lb.set_fontproperties(MSYH); lb.set_fontsize(11)
        ax.grid(axis="y", alpha=0.22)
    fig.suptitle("价值验证全景图：选题 → 中期 → 结题 三阶段关键指标轨迹（含计划目标线）",
                 fontproperties=MSYHB, fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图A_三阶段指标轨迹.png"), dpi=185, bbox_inches="tight")


def plan_vs_actual():
    fig, axes = plt.subplots(1, 2, figsize=(15.6, 5.6))
    ax = axes[0]
    names = ["用户任务\n完成率", "单位变动\n成本", "任务按时\n完成率", "连续工况\n温升", "NPS"]
    plan = [85, 40, 95, 60, 40]
    actual = [78, 43.0, 96, 49, 42]
    # 统一换算成“达标度”（实际/计划，成本与温升为逆向指标）
    ratio = [78 / 85 * 100, 40 / 43.0 * 100, 96 / 95 * 100, 60 / 49 * 100, 42 / 40 * 100]
    cols = [R if r < 100 else G for r in ratio]
    bars = ax.bar(names, ratio, 0.5, color=cols)
    for b, r, p, a in zip(bars, ratio, plan, actual):
        ax.text(b.get_x() + b.get_width() / 2, r + 2, f"{r:.0f}%", ha="center",
                fontproperties=MSYH, fontsize=12.5)
        ax.text(b.get_x() + b.get_width() / 2, 6, f"计划 {p}\n实际 {a}", ha="center",
                fontproperties=MSYH, fontsize=9.5, color="white")
    NAVY_ = "#1F3B63"
    ax.axhline(100, color=NAVY_, linestyle="--", linewidth=2)
    ax.text(-0.45, 143, "虚线 = 计划达成线 100%（低于此线即未达预期）", color=NAVY_,
            fontproperties=MSYH, fontsize=10.5, ha="left")
    ax.set_ylim(0, 150); ax.set_ylabel("计划达成度（%，逆向指标已折算）", fontproperties=MSYH, fontsize=11)
    ax.set_title("计划 vs 实际（执行偏差）", fontproperties=MSYHB, fontsize=14)
    for lb in ax.get_xticklabels():
        lb.set_fontproperties(MSYH); lb.set_fontsize(11)
    ax.grid(axis="y", alpha=0.22)

    ax = axes[1]
    idx = ["用户任务完成率\n（%）", "单位变动成本\n（元，逆向）", "任务按时完成率\n（%）"]
    mean = [78, 43.0, 96]
    best = [92, 39.6, 100]
    x = np.arange(3); wd = 0.32
    b1 = ax.bar(x - wd / 2, mean, wd, color=B, label="团队均值")
    b2 = ax.bar(x + wd / 2, best, wd, color=G, label="团队最优值")
    for bars, vals in ((b1, mean), (b2, best)):
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v}", ha="center",
                    fontproperties=MSYH, fontsize=12)
    gaps = ["差距 14pp（引导环节）", "差距 ¥3.4（B 端占比）", "差距 4pp（排期缓冲）"]
    for xi, t, top in zip(x, gaps, [max(a, b) for a, b in zip(mean, best)]):
        ax.text(xi, top + 5, t, ha="center", fontproperties=MSYH, fontsize=10, color=R)
    ax.set_xticks(x); ax.set_xticklabels(idx, fontproperties=MSYH, fontsize=11)
    ax.set_ylim(0, 118); ax.legend(prop=MSYH, fontsize=11)
    ax.set_title("团队均值 vs 最优值（能力分布与优化空间）", fontproperties=MSYHB, fontsize=14)
    ax.grid(axis="y", alpha=0.22)
    fig.suptitle("三类对比之二：计划 vs 实际、团队均值 vs 最优值", fontproperties=MSYHB, fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图B_计划与实际对比.png"), dpi=185, bbox_inches="tight")


def contribution():
    fig, ax = plt.subplots(figsize=(13.6, 5.4))
    names = [c[0] for c in D.CONTRIB]
    vals = [c[4] for c in D.CONTRIB]
    dif = [c[1] for c in D.CONTRIB]
    bars = ax.bar(names, vals, 0.42, color=[B, G, Y])
    for b, v, df, c in zip(bars, vals, dif, D.CONTRIB):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.06,
                f"贡献值 {v}\n（难度 {df} × 质量 {c[2]} × 协作 {c[3]}）", ha="center",
                fontproperties=MSYH, fontsize=11)
    ax.set_ylim(0, max(vals) * 1.32)
    ax.set_ylabel("贡献值 = 难度系数 × 完成质量 × 协作系数", fontproperties=MSYH, fontsize=11)
    ax.set_title("团队成员贡献值量化（离散度 1.08，较中期 1.42 缩小 24%）", fontproperties=MSYHB, fontsize=14.5)
    for lb in ax.get_xticklabels():
        lb.set_fontproperties(MSYH); lb.set_fontsize(13)
    ax.grid(axis="y", alpha=0.22)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图C_贡献值.png"), dpi=185, bbox_inches="tight")


def cognition_map():
    W = 2100
    img = Image.new("RGB", (W, 900), "white")
    d = ImageDraw.Draw(img)
    F = lambda sz, b=False: ImageFont.truetype(
        "C:/Windows/Fonts/msyhbd.ttc" if b else "C:/Windows/Fonts/msyh.ttc", sz)

    def wrap(text, font, maxw):
        lines, cur = [], ""
        for ch in text:
            if ch == "\n":
                lines.append(cur); cur = ""; continue
            if d.textlength(cur + ch, font=font) <= maxw:
                cur += ch
            else:
                lines.append(cur); cur = ch
        if cur:
            lines.append(cur)
        return lines

    d.text((46, 28), "体验式学习：认知迭代图谱（失败 → 归因 → 新认知 → 新指标）", font=F(46, True), fill=(20, 24, 32))
    d.text((46, 94), "两条链均为真实事件；链一 = 首轮 8 小时连续工况温升越线，链二 = 可用性测试任务完成率仅 50%。每节点附原始证据编号。",
           font=F(23), fill=(110, 118, 128))

    GAP = 44
    COLW = (W - 46 * 2 - GAP) // 2
    chains = [
        ("链一：安全熔断链", (192, 58, 51), 46, [
            ("失败事件", "首轮 8 小时连续工况温升 61.5℃，超过自定阈值 60℃（此前只测 30 分钟短工况，从未发现）", "证据 E-07"),
            ("5Why 归因", "为什么只测 30 分钟？→ 测试按“方便”排期；为什么按方便排？→ 把测试当成“证明合格”的手续，而不是逼近真实使用条件的探针", "证据 E-12"),
            ("新认知", "测试时长必须覆盖真实使用工况——让测试条件逼近产品，而不是让产品迁就测试条件", "证据 E-13"),
            ("新指标结果", "驱动电流降 10% + 铝基板 1.0→1.6mm + 导热硅脂 → 复测 8 小时最高 49℃（优于阈值 11℃）；照度损失仅 9.3%", "证据 E-07"),
        ]),
        ("链二：用户引导链", (44, 90, 160), 46 + COLW + GAP, [
            ("失败事件", "可用性测试任务完成率仅 50%（5/10），距 85% 目标差 35pp；团队把原因归为“用户不熟练”却无记录", "证据 E-08"),
            ("5Why 归因", "失败集中在哪一步？→ 7/12 人次卡在“确认电量档位”；为什么会卡？→ 4 颗 LED 指示含义不直观、说明书无引导步骤；为什么没意识到？→ 把“能点亮”当成“用户会用”", "证据 E-12"),
            ("新认知", "功能跑通 ≠ 用户会用：验收标准应从“功能状态”改为“用户行为指标”", "证据 E-13"),
            ("新指标结果", "硅胶垫丝印档位刻度 + 说明书改“3 步开工卡” → 任务完成率 78%（10/13）；该步骤失败率 58.3% → 7.7%", "证据 E-08"),
        ]),
    ]
    ytop = 158
    maxy = ytop
    for title, color, x, nodes in chains:
        d.rounded_rectangle([x, ytop, x + COLW, ytop + 58], 10, fill=color)
        d.text((x + 16, ytop + 12), title, font=F(28, True), fill="white")
        y = ytop + 74
        for i, (stage, text, ev) in enumerate(nodes):
            lines = wrap(text, F(23), COLW - 34)
            h = 56 + len(lines) * 30 + 14
            d.rounded_rectangle([x, y, x + COLW, y + h], 8, fill=(244, 246, 250), outline=color, width=3)
            d.text((x + 16, y + 14), stage, font=F(26, True), fill=color)
            tw = d.textlength(ev, font=F(21))
            d.text((x + COLW - tw - 16, y + 18), ev, font=F(21), fill=(132, 138, 148))
            for j, ln in enumerate(lines):
                d.text((x + 16, y + 52 + j * 30), ln, font=F(23), fill=(40, 44, 52))
            if i < len(nodes) - 1:
                cx = x + COLW // 2
                d.polygon([(cx - 13, y + h + 4), (cx, y + h + 16), (cx + 13, y + h + 4)], fill=color)
            y += h + 22
        maxy = max(maxy, y)

    img = img.crop((0, 0, W, maxy + 14))
    img.save(os.path.join(OUT, "图D_认知迭代图谱.png"))
    print("cognition map ->", img.size)


if __name__ == "__main__":
    trend(); plan_vs_actual(); contribution(); cognition_map()
