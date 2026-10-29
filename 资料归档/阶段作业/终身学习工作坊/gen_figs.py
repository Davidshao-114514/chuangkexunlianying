# -*- coding: utf-8 -*-
"""终身学习工作坊：配图（三领域前后测雷达图 / 增量图 / 作品示意图）"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageDraw, ImageFont
import data3 as D

OUT = os.path.dirname(os.path.abspath(__file__))
MSYH = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
MSYHB = FontProperties(fname=r"C:\Windows\Fonts\msyhbd.ttc")
NAVY, TEAL, ORANGE, GREY = "#1F3B63", "#2E8B85", "#D97B29", "#8A94A6"
plt.rcParams["axes.unicode_minus"] = False


def radar():
    labels = [f"{c} {n}" for c, n, _, _ in D.PREPOST]
    pre = [p for _, _, p, _ in D.PREPOST]
    post = [q for _, _, _, q in D.PREPOST]
    n = len(labels)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    ang += ang[:1]
    pre += pre[:1]
    post += post[:1]
    fig = plt.figure(figsize=(10.6, 8.6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 8)
    ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_yticklabels([f"L{i}" for i in range(1, 9)], fontproperties=MSYH, fontsize=9, color=GREY)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(labels, fontproperties=MSYH, fontsize=10.5, color="#333")
    ax.tick_params(pad=9)
    ax.plot(ang, pre, color=GREY, linewidth=2, linestyle="--", label="前测（课程初）")
    ax.fill(ang, pre, color=GREY, alpha=0.10)
    ax.plot(ang, post, color=TEAL, linewidth=2.6, label="后测（课程末）")
    ax.fill(ang, post, color=TEAL, alpha=0.20)
    for a, p, q in zip(ang[:-1], pre[:-1], post[:-1]):
        ax.annotate(f"+{q-p}" if q > p else "0", (a, q), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontproperties=MSYHB, fontsize=9, color=ORANGE)
    ax.set_title("EntreComp 三领域 15 项三级指标：前测 vs 后测", fontproperties=MSYHB, fontsize=15, color=NAVY, pad=26)
    ax.legend(loc="lower right", bbox_to_anchor=(1.16, -0.06), prop=MSYH, fontsize=11, frameon=False)
    fig.text(0.02, 0.025, "数据来源：本人于课程测评系统完成的前测 / 后测问卷（以系统截图为准）；本图由测评结果数据绘制。",
             fontproperties=MSYH, fontsize=9, color=GREY)
    fig.tight_layout(rect=[0, 0.04, 0.88, 1])
    fig.savefig(os.path.join(OUT, "图A_三领域前后测雷达图.png"), dpi=190, facecolor="white")
    plt.close(fig)


def delta():
    items = [(f"{c} {n}", q - p) for c, n, p, q in D.PREPOST]
    items.sort(key=lambda x: (-x[1], x[0]))
    names = [i[0] for i in items]
    vals = [i[1] for i in items]
    colors = [TEAL if v >= 3 else (NAVY if v == 2 else ORANGE) for v in vals]
    fig, ax = plt.subplots(figsize=(9.4, 7.4))
    y = np.arange(len(names))[::-1]
    ax.barh(y, vals, color=colors, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontproperties=MSYH, fontsize=10.5)
    for yy, v in zip(y, vals):
        ax.text(v + 0.06, yy, f"+{v}", va="center", fontproperties=MSYHB, fontsize=11,
                color=TEAL if v >= 3 else (NAVY if v == 2 else ORANGE))
    ax.set_xlim(0, 3.6)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["0", "+1", "+2", "+3"], fontproperties=MSYH, fontsize=10.5)
    ax.set_xlabel("等级增量（后测 − 前测）", fontproperties=MSYH, fontsize=11.5, color="#333")
    ax.set_title("15 项三级指标增量图（+3 深绿 / +2 蓝 / +1 橙）", fontproperties=MSYHB, fontsize=14.5, color=NAVY, pad=14)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#E3E8F0", linewidth=1)
    ax.set_axisbelow(True)
    fig.text(0.02, 0.02, "数据来源：课程测评系统前测 / 后测结果（截图见随附）；本图由测评结果数据绘制。",
             fontproperties=MSYH, fontsize=9, color=GREY)
    fig.tight_layout(rect=[0, 0.045, 1, 1])
    fig.savefig(os.path.join(OUT, "图B_增量图.png"), dpi=190, facecolor="white")
    plt.close(fig)


# ---------------- 作品示意图（PIL 手绘） ----------------
F = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", s)
FB = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", s)


def device_sketch(W=1240, H=760, path="图C_作品示意图.png"):
    img = Image.new("RGB", (W, H), "#FBFCFE")
    d = ImageDraw.Draw(img)
    # 桌面
    d.rectangle([60, 560, W - 60, 620], fill="#E8EDF6", outline="#C9D3E4", width=2)
    d.text((76, 578), "焊台桌面", font=F(24), fill="#5A6678")
    # 金属底板
    d.rectangle([150, 540, 620, 566], fill="#B9C2D0", outline="#98A4B6", width=2)
    d.text((636, 520), "铁质底板（磁吸面）", font=F(24), fill="#5A6678")
    # 磁吸座
    d.rounded_rectangle([250, 470, 360, 546], 10, fill="#3C4C68", outline="#26344A", width=2)
    d.text((252, 484), "磁吸座", font=F(22), fill="white")
    # 万向柔臂
    pts = [(305, 470), (300, 400), (330, 350), (360, 310), (400, 290)]
    d.line(pts, fill="#2E8B85", width=16, joint="curve")
    for p in pts[1:-1]:
        d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill="#1F6B66")
    d.text((104, 330), "万向柔臂", font=F(24), fill="#26685F")
    d.text((104, 362), "（400mm，任意悬停）", font=F(20), fill="#6A7688")
    # 灯头
    d.rounded_rectangle([378, 262, 486, 302], 8, fill="#1F3B63", outline="#14243C", width=2)
    d.polygon([(418, 302), (446, 302), (528, 430), (352, 430)], fill="#FFE9A8", outline="#E5C86A")
    for xx in (392, 418, 446, 472):
        d.line([(xx, 306), ((xx - 418) * 3.2 + 440, 424)], fill="#F2D479", width=2)
    d.text((392, 232), "灯头（可调光）", font=F(22), fill="#1F3B63")
    # 光斑
    d.ellipse([352, 425, 528, 500], fill="#FFF6D0", outline="#E8D79A", width=3)
    d.text((566, 462), "光斑 Ø60mm", font=F(24), fill="#B08A2E")
    # 焊接板与焊点
    d.rounded_rectangle([700, 300, 1130, 520], 12, fill="#14603F", outline="#0C4630", width=3)
    d.text((716, 316), "PCB（焊接对象）", font=F(24), fill="#CDEBDC")
    for i, (x, y) in enumerate([(830, 380), (870, 380), (910, 380), (950, 380), (990, 380), (1030, 380)]):
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill="#E6C36A", outline="#B99243")
    d.text((830, 410), "0603 焊盘阵列", font=F(21), fill="#A9D7C1")
    # 手与烙铁（简化）
    d.line([(1075, 300), (1180, 220)], fill="#8A94A6", width=13)
    d.polygon([(1078, 292), (1066, 300), (1072, 312)], fill="#6E7686")
    d.text((1136, 200), "烙铁", font=F(22), fill="#6E7686")
    # 说明
    d.text((60, 60), "磁吸焊接辅助手电 · 工作原理示意", font=FB(38), fill="#1F3B63")
    d.text((62, 120), "磁吸固定解放双手 → 万向悬停指哪照哪 → 无级调光适配光环境（65 元可得）", font=F(24), fill="#5A6678")
    d.line([(60, 165), (W - 60, 165)], fill="#DCE3EE", width=2)
    d.text((60, H - 66), "示意图（非实拍）；实拍照片见结题材料照片留存 B-10 ~ B-12。", font=F(21), fill="#8A94A6")
    img.save(os.path.join(OUT, path), quality=95)
    return img.size


if __name__ == "__main__":
    radar()
    delta()
    print("device sketch ->", device_sketch())
    print("figs done")
