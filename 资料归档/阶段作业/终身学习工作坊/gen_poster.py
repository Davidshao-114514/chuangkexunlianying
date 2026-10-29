# -*- coding: utf-8 -*-
"""生成创客竞赛作品海报（A4 电子版）：个体初稿 + 团队代表作品"""
import os
from PIL import Image, ImageDraw, ImageFont
import data3 as D

OUT = os.path.dirname(os.path.abspath(__file__))
F = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", s)
FB = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", s)
W, H = 2480, 3508          # A4 @300dpi
NAVY, TEAL, ORANGE, INK, GREY = "#1F3B63", "#1E7A72", "#D97B29", "#22303F", "#7A8598"
SOFT, LINE = "#F4F7FB", "#DBE3EE"
import re
_TOK = re.compile(r"[A-Za-z0-9%¥.+\-/→≥≤×]+|.", re.S)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for ch in _TOK.findall(text):
        t = cur + ch
        if d.textlength(t, font=font) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, maxw, fill=INK, lh=1.5, align="left"):
    lines = wrap(d, text, font, maxw)
    for i, ln in enumerate(lines):
        xx = x if align == "left" else (x + (maxw - d.textlength(ln, font=font)) / 2 if align == "center" else x)
        d.text((xx, y + i * font.size * lh), ln, font=font, fill=fill)
    return y + len(lines) * font.size * lh


def card(d, box, fill="white", outline=LINE, r=26, width=3):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def section_label(d, x, y, txt, color=TEAL):
    d.rounded_rectangle([x, y, x + 14, y + 44], 6, fill=color)
    d.text((x + 30, y - 2), txt, font=FB(46), fill=NAVY)


def photo_slot(d, box, caption="团队合影"):
    d.rounded_rectangle(box, 22, fill="#EFF3F9", outline="#C9D5E6", width=3)
    x0, y0, x1, y1 = box
    for i in range(x0 + 20, x1 - 10, 34):                      # 斜纹示意照片位
        d.line([(i, y1 - 20), (min(i + 60, x1 - 10), y0 + 20)], fill="#DFE7F2", width=3)
    d.text(((x0 + x1) / 2 - d.textlength(caption, font=FB(40)) / 2, (y0 + y1) / 2 - 26),
           caption, font=FB(40), fill="#93A0B4")


def member_cards(d, x, y, w, members, accent=TEAL):
    n = len(members); gap = 22; cw = (w - gap * (n - 1)) / n
    for i, (nm, role) in enumerate(members):
        bx = x + i * (cw + gap)
        card(d, [bx, y, bx + cw, y + 210], fill="#FAFCFF")
        d.ellipse([bx + 26, y + 30, bx + 106, y + 110], fill=accent)
        d.text((bx + 26 + (80 - d.textlength(nm[0], font=FB(52))) / 2, y + 44), nm[0], font=FB(52), fill="white")
        d.text((bx + 124, y + 40), nm, font=FB(44), fill=NAVY)
        para(d, bx + 124, y + 96, role, F(28), cw - 146, fill=GREY, lh=1.35)


def data_cards(d, x, y, w, items, accent=NAVY):
    gap = 26; cw = (w - gap) / 2
    for i, (big, small) in enumerate(items):
        bx = x + (i % 2) * (cw + gap); by = y + (i // 2) * (250 + gap)
        card(d, [bx, by, bx + cw, by + 250], fill="#F7FAFF")
        d.text((bx + 34, by + 30), big, font=FB(62), fill=accent)
        para(d, bx + 34, by + 122, small, F(32), cw - 68, fill=GREY, lh=1.4)


def footer(d, y, extra=""):
    d.line([(110, y), (W - 110, y)], fill=LINE, width=3)
    d.text((110, y + 22), f"{D.COURSE}　|　{D.TEAM_FULL}　|　{D.DATE}", font=FB(34), fill=NAVY)
    para(d, 110, y + 78, "关键数据来源：意向金收款明细与邀请名单、可用性测试现场观察记录、8 小时连续工况温升记录表、BOM 三档询价单"
         + ("；" + extra if extra else ""), F(28), W - 220, fill=GREY, lh=1.35)


# ==================== 团队代表作品 ====================
def team_poster():
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 470], fill=NAVY)
    d.rectangle([0, 470, W, 486], fill=ORANGE)
    d.text((110, 74), "华中科技大学《创客训练营》课程作品", font=F(40), fill="#A9BEDC")
    d.text((110, 132), D.PROJ, font=FB(122), fill="white")
    d.text((110, 288), f"“{D.SLOGAN}”", font=FB(60), fill="#FFD9A0")
    d.text((110, 374), "AI + OPC 主题　|　硬件产品型　|　1班C组 · 仿真跑不队", font=F(42), fill="#C9D8EE")

    y = 560
    section_label(d, 110, y, "团队信息")
    photo_slot(d, [1830, y - 10, 2370, y + 300], "团队合影")
    member_cards(d, 110, y + 70, 1660, [("邵子中", "负责人 / 经济模型 · 固件 · 答辩主讲"),
                                        ("李昊桐", "结构 · 可靠性测试 · 装配"),
                                        ("姜亚楷", "渠道 · B 端交付 · 财务监督")])
    y += 300

    # 价值主张
    section_label(d, 110, y + 80, "核心价值主张", ORANGE)
    card(d, [110, y + 145, W - 110, y + 445], fill="#FFF9F0", outline="#F0DCBE")
    para(d, 170, y + 185, D.POSTER["value"], F(44), W - 350, fill="#4A3A22", lh=1.5)
    y += 445

    # 认知收获
    section_label(d, 110, y + 80, "核心认知收获", TEAL)
    card(d, [110, y + 145, W - 110, y + 400], fill="#EFF8F6", outline="#BFE0DA")
    d.text((170, y + 178), "“", font=FB(120), fill="#9ACFC7")
    para(d, 300, y + 200, D.POSTER["insight"], FB(50), W - 470, fill="#14544E", lh=1.45)
    y += 400

    # 关键数据
    section_label(d, 110, y + 80, "关键数据（可追溯）", NAVY)
    data_cards(d, 110, y + 150, W - 220, D.POSTER["data"])
    y += 150 + 2 * 250 + 26

    # 作品呈现
    section_label(d, 110, y + 70, "作品呈现")
    card(d, [110, y + 130, 1560, y + 130 + 760], fill="#FBFCFE")
    sk = Image.open(os.path.join(OUT, "图C_作品示意图.png"))
    sk = sk.resize((1420, int(1420 * sk.height / sk.width)))
    img.paste(sk, (130, y + 150))
    card(d, [1610, y + 130, W - 110, y + 130 + 760], fill="#FBFCFE")
    d.text((1650, y + 165), "三代原型演进", font=FB(44), fill=NAVY)
    for i, (nm, desc) in enumerate([("V1.0", "面包板 + 改造小夜灯 + 磁铁胶带"),
                                    ("V2.0", "PCBA 打样 + 3D 打印外壳 + 磁吸座"),
                                    ("V3.0 / V4.0", "硅胶磁吸垫 + NTC 过温 + 4 颗状态灯")]):
        by = y + 250 + i * 200
        d.rounded_rectangle([1650, by, 1650 + 96, by + 96], 16, fill=TEAL)
        d.text((1658, by + 24), f"V{i+1}", font=FB(38), fill="white")
        d.text((1770, by + 6), nm, font=FB(40), fill=INK)
        para(d, 1770, by + 56, desc, F(30), 480, fill=GREY, lh=1.35)
    footer(d, H - 230)
    f1 = os.path.join(OUT, "海报_团队代表作品_仿真跑不队.png")
    img.save(f1, quality=96)
    img.save(os.path.join(OUT, "海报_团队代表作品_仿真跑不队.pdf"), "PDF", resolution=300.0)
    return f1


# ==================== 个体初稿（邵子中） ====================
def personal_poster():
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 470], fill=TEAL)
    d.rectangle([0, 470, W, 486], fill=ORANGE)
    d.text((110, 74), f"华中科技大学《创客训练营》课程作品　|　个体海报初稿：{D.STUDENT}（{D.SID}）", font=F(38), fill="#D5F0EC")
    d.text((110, 132), D.PROJ, font=FB(122), fill="white")
    d.text((110, 288), f"“{D.SLOGAN}”", font=FB(60), fill="#FFE6B8")
    d.text((110, 374), "我的角色：负责人 / 经济模型与固件 / 答辩主讲　|　1班C组 · 仿真跑不队", font=F(42), fill="#E3F6F3")

    y = 560
    section_label(d, 110, y, "团队信息")
    photo_slot(d, [1830, y - 10, 2370, y + 300], "团队合影")
    member_cards(d, 110, y + 70, 1660, [("邵子中", "负责人 / 经济模型 · 固件 · 答辩主讲"),
                                        ("李昊桐", "结构 · 可靠性测试 · 装配"),
                                        ("姜亚楷", "渠道 · B 端交付 · 财务监督")], accent=NAVY)
    y += 300

    section_label(d, 110, y + 80, "核心价值主张", ORANGE)
    card(d, [110, y + 145, W - 110, y + 445], fill="#FFF9F0", outline="#F0DCBE")
    para(d, 170, y + 185, D.POSTER["value"], F(44), W - 350, fill="#4A3A22", lh=1.5)
    y += 445

    section_label(d, 110, y + 80, "我的核心认知收获", TEAL)
    card(d, [110, y + 145, W - 110, y + 400], fill="#EFF8F6", outline="#BFE0DA")
    d.text((170, y + 178), "“", font=FB(120), fill="#9ACFC7")
    para(d, 300, y + 200, D.POSTER["insight"], FB(50), W - 470, fill="#14544E", lh=1.45)
    para(d, 300, y + 330, "（这条认知来自我负责的经济账主线：陪审团追问 → 意向金 39pp 落差 → 我自己证伪了 H-005）",
         F(30), W - 470, fill="#3E7C74", lh=1.3)
    y += 400

    section_label(d, 110, y + 80, "我负责的关键数据（可追溯）", NAVY)
    data_cards(d, 110, y + 150, W - 220, [("量产 BOM ¥37.6", "三档 ¥52.3 / ¥37.6 / ¥29.2（询价单 E-11）"),
                                          ("保本销量 1,232 台", "单位经济与盈亏平衡模型（量产定价口径）"),
                                          ("意向金支付率 37.3%", "22/59 人真实支付；问卷态度口径 71.3%"),
                                          ("5Why 归因 8 条", "P0/P1 缺陷根因追溯（E-12）")])
    y += 150 + 2 * 250 + 26

    section_label(d, 110, y + 70, "作品呈现与我的关键节点")
    card(d, [110, y + 130, 1560, y + 130 + 760], fill="#FBFCFE")
    sk = Image.open(os.path.join(OUT, "图C_作品示意图.png"))
    sk = sk.resize((1420, int(1420 * sk.height / sk.width)))
    img.paste(sk, (130, y + 150))
    card(d, [1610, y + 130, W - 110, y + 130 + 760], fill="#FBFCFE")
    d.text((1650, y + 165), "我的三个关键节点", font=FB(44), fill=NAVY)
    nodes = [("选题评审 09-26", "被追问“扣掉佣金、物流、售后还剩多少” → 当晚重算两套口径，更换核心指标口径"),
             ("中期评审 10-08", "1 元意向金仅 20/62 人支付，与问卷 71.3% 差 39pp → 北极星指标改为行为口径"),
             ("结题评审 10-22", "被质疑“单台单轮测安全、单一渠道撑转型” → 认知：结论强度取决于样本与渠道数")]
    for i, (t, sdesc) in enumerate(nodes):
        by = y + 250 + i * 200
        d.rounded_rectangle([1650, by, 1650 + 96, by + 96], 16, fill=TEAL)
        d.text((1662, by + 22), str(i + 1), font=FB(46), fill="white")
        d.text((1770, by + 6), t, font=FB(40), fill=INK)
        para(d, 1770, by + 56, sdesc, F(28), 500, fill=GREY, lh=1.3)
    footer(d, H - 230)
    f2 = os.path.join(OUT, "海报_个体初稿_邵子中.png")
    img.save(f2, quality=96)
    img.save(os.path.join(OUT, "海报_个体初稿_邵子中.pdf"), "PDF", resolution=300.0)
    return f2


if __name__ == "__main__":
    print("team:", team_poster())
    print("personal:", personal_poster())
