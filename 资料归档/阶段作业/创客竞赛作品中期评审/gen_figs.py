# -*- coding: utf-8 -*-
"""中期评审：PPT 配图（盲测雷达 / 资源效率 / 基线对比）"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from data import BLIND_TEST, BLIND_N, TOTAL_TABLE, PROGRESS, DASHBOARD

OUT = os.path.dirname(os.path.abspath(__file__))
MSYH = FontProperties(fname="C:/Windows/Fonts/msyh.ttc")
MSYHB = FontProperties(fname="C:/Windows/Fonts/msyhbd.ttc")
plt.rcParams["axes.unicode_minus"] = False
G, Y, R, B, GR = "#227F57", "#D09414", "#C0392F", "#2C5AA0", "#8C97A8"


def radar():
    labels = BLIND_TEST["维度"]
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist(); ang += ang[:1]
    fig, ax = plt.subplots(figsize=(9.8, 8.8), subplot_kw=dict(polar=True))
    fig.subplots_adjust(top=0.90, bottom=0.20, left=0.07, right=0.88)
    styles = {"本方案": (G, 3.2, 0.24), "专业工业灯": (B, 2.0, 0.10),
              "传统台灯": (Y, 2.0, 0.10), "廉价便携灯": (R, 2.0, 0.10)}
    for name, (c, lw, al) in styles.items():
        v = BLIND_TEST[name] + BLIND_TEST[name][:1]
        ax.plot(ang, v, color=c, linewidth=lw, label=name)
        ax.fill(ang, v, color=c, alpha=al)
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontproperties=MSYH, fontsize=13)
    ax.set_ylim(0, 5); ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=9, color="#888")
    ax.set_title(f"竞品盲测雷达图（N={BLIND_N} 位目标用户，不告知品牌，5 维度 1–5 分）",
                 fontproperties=MSYHB, fontsize=15, pad=24)
    ax.legend(prop=MSYH, fontsize=12, loc="upper right", bbox_to_anchor=(1.20, 1.10))
    note = ("差异化优势（本方案高出竞品 ≥1 分）：功能覆盖 vs 台灯/便携灯 4.0 vs 2.4/1.9；\n"
            "用户体验 vs 台灯/便携灯 4.5 vs 2.6/2.2；价格可接受度 vs 专业灯 4.3 vs 2.1。\n"
            "劣势维度：可信度 3.7，低于专业工业灯 4.5——品牌与可靠性背书不足。")
    fig.text(0.04, 0.035, note, fontproperties=MSYH, fontsize=11, color="#555", linespacing=1.75)
    fig.savefig(os.path.join(OUT, "图A_盲测雷达图.png"), dpi=190)


def efficiency():
    fig, axes = plt.subplots(1, 2, figsize=(15.6, 5.6))
    ax = axes[0]
    names = ["时间（人时 / 条）", "资金（元 / 份）", "外部资源（次 / 项）"]
    vals = [2.1, 53.0, 0.455]
    forms = ["每 2.1 人时\n= 1 条验证数据", "每 ¥53\n= 1 份付费行为数据", "每次外部调用\n= 2.2 项改进/合作"]
    cols = [G, B, Y]
    bars = ax.bar(names, vals, 0.5, color=cols)
    for b, f in zip(bars, forms):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.06, f, ha="center",
                fontproperties=MSYH, fontsize=12)
    ax.set_yscale("log"); ax.set_ylim(0.25, 180)
    ax.set_ylabel("单位产出所需投入（对数刻度）", fontproperties=MSYH, fontsize=11)
    ax.set_xticklabels(names, fontproperties=MSYH, fontsize=12)
    ax.set_title("资源投入-产出效率（三项核心换算）", fontproperties=MSYHB, fontsize=14)
    ax.grid(axis="y", alpha=0.22)

    ax = axes[1]
    m = [p[0].split("：")[0] for p in PROGRESS]
    pct = [p[2] for p in PROGRESS]
    cols = [G, Y, B]
    bars = ax.barh(m, pct, 0.42, color=cols)
    for b, v, p in zip(bars, pct, PROGRESS):
        ax.text(v + 1.5, b.get_y() + b.get_height() / 2, f"{v}%  {p[3]}", va="center",
                fontproperties=MSYH, fontsize=12)
    ax.axvline(68, color=R, linestyle="--", linewidth=2)
    ax.text(70, 2.42, "加权目标完成度 68%\n（权重 M1 40% / M2 35% / M3 25%）",
            color=R, fontproperties=MSYH, fontsize=10.5, va="center")
    ax.set_xlim(0, 122); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels([f"{v}%" for v in (0, 25, 50, 75, 100)], fontproperties=MSYH)
    ax.set_yticklabels(m, fontproperties=MSYH, fontsize=11.5)
    ax.set_title("里程碑进度总览", fontproperties=MSYHB, fontsize=14)
    ax.grid(axis="x", alpha=0.22)
    fig.suptitle("“做得值不值”与“做得快不快”：资源效能与进度健康度", fontproperties=MSYHB, fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图B_资源效率与进度.png"), dpi=190, bbox_inches="tight")


def baseline_vs_now():
    fig, axes = plt.subplots(1, 4, figsize=(16.0, 4.9))
    items = [
        ("付费意愿（口径）", 71.3, 32.3, "问卷态度 → 行为（意向金）", "%"),
        ("沉浸式焊接失败率", 50.0, 20.0, "无灯 → 用本方案", "%"),
        ("预约/下单转化", 0.0, 31.8, "预售页 A 组（基线为 0）", "%"),
        ("温升余量", 8.0, 8.0, "标准 ≤60℃，实测 52℃", "℃"),
    ]
    for ax, (t, pre, now, note, unit) in zip(axes, items):
        if pre > 0:
            bars = ax.bar(["选题评审基线", "中期实测"], [pre, now], 0.5, color=[GR, G])
        else:
            bars = ax.bar(["选题评审基线", "中期实测"], [0.001, now], 0.5, color=[GR, G])
        for b, v in zip(bars, [pre, now]):
            ax.text(b.get_x() + b.get_width() / 2, v + (3 if unit == "%" else 0.6),
                    f"{v}{unit}", ha="center", fontproperties=MSYH, fontsize=12)
        ax.set_title(t, fontproperties=MSYHB, fontsize=13)
        ax.set_ylim(0, max(pre, now) * 1.42 + 3)
        ax.tick_params(axis="x", labelsize=10)
        for lb in ax.get_xticklabels():
            lb.set_fontproperties(MSYH)
        ax.grid(axis="y", alpha=0.22)
        ax.text(0.5, -0.30, note, transform=ax.transAxes, ha="center",
                fontproperties=MSYH, fontsize=9.5, color="#555")
    fig.suptitle("关键指标：基线 vs 中期实测（进展总览页的对比依据）", fontproperties=MSYHB, fontsize=16)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "图C_基线与中期对比.png"), dpi=190, bbox_inches="tight")


if __name__ == "__main__":
    radar(); efficiency(); baseline_vs_now()
    print("figs done ->", OUT)
