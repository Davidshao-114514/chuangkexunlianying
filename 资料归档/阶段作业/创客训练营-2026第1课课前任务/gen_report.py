# -*- coding: utf-8 -*-
"""《创客训练营》2026年第1课"团队合作"课前任务：生成 4 张配图 + 完整 Word 报告"""
import os, math, re
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\35464\Desktop\创客训练营-2026第1课课前任务"
os.makedirs(OUT, exist_ok=True)

FONT_R = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"

def F(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)

def wrap(d, text, font, max_w):
    """标点感知断行：优先在标点/空格后断行；引号/括号不拆开（避免「…」孤行）。"""
    lines = []
    for para in text.split("\n"):
        toks = [t for t in re.split(r'(?<=[，。；、：！？…—\s])', para) if t]
        if not toks:
            toks = [para]
        cur = ""
        for t in toks:
            if d.textlength(cur + t, font=font) <= max_w:
                cur += t
            else:
                if cur:
                    lines.append(cur)
                    cur = ""
                if d.textlength(t, font=font) > max_w:  # 超长 token 逐字断
                    for ch in t:
                        if d.textlength(cur + ch, font=font) <= max_w or not cur:
                            cur += ch
                        else:
                            lines.append(cur)
                            cur = ch
                else:
                    cur = t
        if cur:
            # 孤立的结尾标点并入上一行，避免单字成行
            if len(cur) <= 2 and lines and cur.strip("，。；、：！？）」』…—.· ") == "":
                lines[-1] += cur
            else:
                lines.append(cur)
    return lines

def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img

def arrow(d, p1, p2, color, width=6, head=16):
    x1, y1 = p1; x2, y2 = p2
    d.line([(x1, y1), (x2, y2)], fill=color, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (2.6, -2.6):
        hx = x2 - head * math.cos(ang + da)
        hy = y2 - head * math.sin(ang + da)
        d.line([(x2, y2), (hx, hy)], fill=color, width=width)

# ============================================================ 1. 海报
def make_poster():
    W = 1200
    GOLD = (255, 201, 77); WHITE = (255, 255, 255); LBLUE = (157, 180, 232)
    CARD = (16, 34, 78); EDGE = (46, 74, 143)
    x, wcard = 70, W - 140
    pad, lh, body_sz = 28, 44, 25
    f_body = F(body_sz)
    f_hd = F(30, True)

    # 测量用临时画布
    img_t = Image.new("RGB", (W, 10)); d_t = ImageDraw.Draw(img_t)

    cards = [
        ("个人成长 · 从「会做题」到「会做作品」", (74, 144, 226), [
            "硬技能：CH224K+FP7209 恒流电源实战，掌握原理图设计、Altium Designer 布局、参数计算与实测调试，完成从原理图到打样的完整流程",
            "软技能：完成一次完整的路演答辩；至少经历 2 次「冲突解决」实战，提升沟通与谈判能力",
            "每位新人配一位学长/学姐全程带教（老带新）——两周内点亮自己亲手做的第一块电源板",
        ]),
        ("项目成效 · 快 30%，错 50%↓", (124, 179, 66), [
            "速度：Git 分支并行开发 + 在线任务看板，你的任务开发周期可缩短 30% 以上",
            "质量：原理图评审 + 代码审查制度，让错误率降低 50%——评审不过，绝不出货",
            "机制：每周 15 分钟例会同步进度与卡点，问题当天暴露、当天解决，没有人掉队",
        ]),
        ("团队文化 · 你不是一个人在战斗", (232, 163, 61), [
            "情绪安全：你可以毫无负担地说「我不懂」「我搞砸了」，第一反应永远是「我们一起解决」",
            "归属感：轮值主持机制让每个人都有主导权时刻，内向与资历浅绝不会成为被边缘化的理由",
            "情感支持：备赛夜宵有人叫、进展有人鼓掌；困难时，总会有人主动问「你需要什么帮助」",
        ]),
    ]
    tags = ["共同目标", "明确分工", "开放沟通", "责任共担", "信任尊重", "冲突解决", "资源共享"]

    # ---- 预排版：各类内容行数 -> 卡片高度 ----
    body_w = wcard - 2 * pad - 44
    all_lines, h_body = [], []
    for title, col, bullets in cards:
        lines = []
        for b in bullets:
            lines.append(wrap(d_t, b, f_body, body_w))
        all_lines.append(lines)
        n_lines = sum(len(ls) for ls in lines)
        h_body.append(64 + pad * 2 + (n_lines - 1) * lh + int(body_sz * 1.5))
    TAG_H = 26 + 2 + 20 + 52 + 24          # 卡片3 标签区：分隔线间距+线+间距+标签+底部
    h_card = max(h_body[0], h_body[1], h_body[2] + TAG_H)

    # ---- 总布局 ----
    y_title = 52; y_sub = 188; y_line = 242; y0 = 284
    GAP = 28
    join_h = 240; y_join = y0 + 3 * h_card + 2 * GAP + 44
    y_footer = y_join + join_h + 52
    H = y_footer + 68

    img = gradient(W, H, (8, 20, 52), (24, 44, 92))
    d = ImageDraw.Draw(img)

    def center(y, text, font, fill):
        w = d.textlength(text, font=font)
        d.text(((W - w) / 2, y), text, font=font, fill=fill)

    center(y_title, "HUST 电工基地 · 创客训练营 · 参赛战队招募", F(25), LBLUE)
    center(y_title + 56, "星火电赛战队 · 2026 招新", F(58, True), GOLD)
    center(y_sub, "用一块自己点亮的电源板，回答「我为什么要加入你们」", F(27), WHITE)
    d.line([(240, y_line), (W - 240, y_line)], fill=GOLD, width=3)

    # ---- 三张统一高度的卡片 ----
    y = y0
    for ci, ((title, col, _), lines, hb) in enumerate(zip(cards, all_lines, h_body)):
        d.rounded_rectangle([x, y, x + wcard, y + h_card], radius=22, fill=CARD, outline=EDGE, width=2)
        d.rectangle([x, y, x + wcard, y + 8], fill=col)
        d.rounded_rectangle([x + pad, y + 22, x + pad + 40, y + 62], radius=10, fill=col)
        d.text((x + pad + 56, y + 26), title, font=f_hd, fill=WHITE)
        yy = y + 64 + pad
        for ls in lines:
            for ln in ls:
                d.rounded_rectangle([x + pad + 4, yy + 12, x + pad + 16, yy + 24], radius=4, fill=col)
                d.text((x + pad + 30, yy), ln, font=f_body, fill=(232, 238, 252))
                yy += lh
        if ci == 2:  # 标签区并入卡片3
            ly = y + hb + 26
            d.line([(x + pad, ly), (x + wcard - pad, ly)], fill=EDGE, width=2)
            fy = ly + 20
            tf = F(20, True); tgap = 14; tp = 50
            tws = [d.textlength(t, font=tf) + tp for t in tags]
            tx = (W - (sum(tws) + tgap * (len(tags) - 1))) / 2
            for t, tw in zip(tags, tws):
                d.rounded_rectangle([tx, fy, tx + tw, fy + 52], radius=26, fill=(30, 52, 100), outline=GOLD, width=2)
                d.text((tx + tp / 2, fy + 26), t, font=tf, fill=GOLD, anchor="lm")
                tx += tw + tgap
        y += h_card + GAP

    # ---- 加入方式 ----
    d.rounded_rectangle([x, y_join, x + wcard, y_join + join_h], radius=22, fill=CARD, outline=EDGE, width=2)
    d.text((x + pad, y_join + 24), "加入方式", font=F(28, True), fill=GOLD)
    info = [
        "面向大一、大二本科生（有硬件/单片机基础优先，零基础同样欢迎）",
        "扫码加入招新群 · 报名截止 2026 年 9 月 15 日",
        "组队与选题：9 月中旬完成组队，月底完成选题入库",
    ]
    iy = y_join + 78
    for t in info:
        d.text((x + pad, iy), t, font=F(21), fill=(220, 228, 250))
        iy += 38
    qs = 200
    qx = x + wcard - pad - qs
    qy = y_join + (join_h - qs) / 2
    for k in range(0, qs, 12):
        d.line([(qx + k, qy), (qx + k + 8, qy)], fill=LBLUE, width=2)
        d.line([(qx + k, qy + qs), (qx + k + 8, qy + qs)], fill=LBLUE, width=2)
        d.line([(qx, qy + k), (qx, qy + k + 8)], fill=LBLUE, width=2)
        d.line([(qx + qs, qy + k), (qx + qs, qy + k + 8)], fill=LBLUE, width=2)
    d.rectangle([qx, qy, qx + qs, qy + qs], outline=LBLUE, width=2)
    d.text((qx + qs / 2, qy + qs / 2), "二维码\n占位", font=F(22), fill=LBLUE, anchor="mm")

    center(y_footer, "让平凡的人聚在一起，做出不平凡的事——也让你自己变得不平凡", F(24), LBLUE)
    img.save(os.path.join(OUT, "海报-团队招募.png"))
    print("poster ok")

# ============================================================ 2. 乔哈里视窗
def make_johari():
    W, H = 1000, 1160
    img = Image.new("RGB", (W, H), (248, 250, 253))
    d = ImageDraw.Draw(img)
    BLUE = (37, 74, 151); GRAY = (90, 100, 120)
    x0, y0, side = 220, 100, 560
    hf = side / 2
    quads = [
        (x0, y0, "公开象限", "我知道 · 你也知道", (255, 233, 184), (120, 80, 0)),
        (x0 + hf, y0, "盲点象限", "我不知道 · 你知道", (220, 231, 255), (20, 50, 110)),
        (x0, y0 + hf, "隐私象限", "我知道 · 你不知道", (214, 240, 217), (20, 90, 40)),
        (x0 + hf, y0 + hf, "未知象限", "我不知道 · 你不知道", (233, 233, 240), (90, 90, 100)),
    ]
    d.text((W / 2, 44), "沟通视窗（乔哈里视窗）模型", font=F(36, True), fill=BLUE, anchor="mm")
    d.text((W / 2, 82), "公开象限越大 → 信任越高、沟通效率越高", font=F(22), fill=GRAY, anchor="mm")
    for qx, qy, name, sub, fill, tcol in quads:
        d.rectangle([qx, qy, qx + hf, qy + hf], fill=fill, outline=(160, 170, 190), width=2)
        d.text((qx + hf / 2, qy + hf / 2 - 30), name, font=F(32, True), fill=tcol, anchor="mm")
        d.text((qx + hf / 2, qy + hf / 2 + 26), sub, font=F(21), fill=tcol, anchor="mm")
    d.rectangle([x0, y0, x0 + side, y0 + side], outline=BLUE, width=3)

    rows = [
        ("隐私象限", "自我揭示（主动说出自己的想法与困难）", (46, 160, 90)),
        ("盲点象限", "恳请反馈（主动请他人指出自己的盲区）", (220, 120, 40)),
        ("未知象限", "共同探索（深度沟通、一起经历项目）", (120, 100, 220)),
    ]
    ry = y0 + side + 60
    d.text((W / 2, ry - 34), "三个方向的动态转化：", font=F(24, True), fill=BLUE, anchor="mm")
    for i, (src, label, col) in enumerate(rows):
        yy = ry + 20 + i * 96
        d.rounded_rectangle([180, yy, 320, yy + 56], radius=12, fill=(240, 243, 250), outline=col, width=2)
        d.text((250, yy + 28), src, font=F(24, True), fill=col, anchor="mm")
        d.text((250, yy + 92), label, font=F(19), fill=(120, 130, 150), anchor="mm")
        arrow(d, (325, yy + 28), (600, yy + 28), col, width=5)
        d.rounded_rectangle([605, yy, 745, yy + 56], radius=12, fill=(255, 233, 184), outline=(200, 150, 30), width=2)
        d.text((675, yy + 28), "公开象限", font=F(24, True), fill=(120, 80, 0), anchor="mm")
    d.text((W / 2, ry + 360), "若回避反馈、封闭自我 → 公开象限萎缩 → 误解与冲突增多（负循环）", font=F(21), fill=GRAY, anchor="mm")
    img.save(os.path.join(OUT, "乔哈里视窗.png"))
    print("johari ok")

# ============================================================ 3. 倾听思维导图
def make_mindmap():
    W, H = 1600, 980
    img = Image.new("RGB", (W, H), (250, 252, 255))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 44), "有效倾听三步骤 · 思维导图", font=F(38, True), fill=(30, 60, 120), anchor="mm")

    rx, ry, rw, rh = 50, 440, 250, 120
    d.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=20, fill=(255, 201, 77), outline=(200, 140, 20), width=3)
    d.text((rx + rw / 2, ry + 34), "有效倾听", font=F(34, True), fill=(90, 60, 0), anchor="mm")
    d.text((rx + rw / 2, ry + 84), "三步骤", font=F(26), fill=(90, 60, 0), anchor="mm")

    cols = [
        ("① 接收", (74, 144, 226), ["停止手中其他事务", "目光接触、面向对方", "不打断、不抢话", "放下手机与电脑"]),
        ("② 理解", (124, 179, 66), ["复述确认：“你是说……对吗？”", "提问澄清：“能举个例子吗？”", "换位思考、捕捉对方情绪", "区分事实与观点"]),
        ("③ 反馈", (232, 163, 61), ["表达感受与共鸣", "总结要点、确认理解一致", "说出下一步行动", "感谢对方的坦诚"]),
    ]
    cxs = [650, 1030, 1410]
    for (title, col, items), cx in zip(cols, cxs):
        nw, nh = 300, 64
        nx, ny = cx - nw // 2, 240
        d.line([(rx + rw, ry + rh // 2), (nx, ny + nh // 2)], fill=col, width=5)
        d.rounded_rectangle([nx, ny, nx + nw, ny + nh], radius=16, fill=col, outline=None)
        d.text((cx, ny + nh // 2), title, font=F(30, True), fill=(255, 255, 255), anchor="mm")
        tw = 360
        pill_h = 68
        trunk_x = cx
        d.line([(trunk_x, ny + nh), (trunk_x, ny + nh + 8 + len(items) * (pill_h + 18))], fill=col, width=4)
        py = ny + nh + 22
        for item in items:
            d.line([(trunk_x, py + pill_h // 2), (nx + nw // 2 - tw // 2 + 20, py + pill_h // 2)], fill=col, width=3)
            d.rounded_rectangle([cx - tw // 2, py, cx + tw // 2, py + pill_h], radius=14,
                                fill=(255, 255, 255), outline=col, width=2)
            lines = wrap(d, item, F(21), tw - 30)
            if len(lines) == 1:
                d.text((cx, py + pill_h // 2), lines[0], font=F(21), fill=(40, 50, 70), anchor="mm")
            else:
                d.text((cx, py + 12), lines[0], font=F(21), fill=(40, 50, 70), anchor="mm")
                d.text((cx, py + pill_h - 14), lines[1], font=F(21), fill=(40, 50, 70), anchor="mm")
            py += pill_h + 18
    d.text((W / 2, H - 40), "倾听不是“等对方说完”，而是“让对方感到被听见”", font=F(22), fill=(120, 130, 150), anchor="mm")
    img.save(os.path.join(OUT, "倾听思维导图.png"))
    print("mindmap ok")

# ============================================================ 4. 电子名片
def make_namecard():
    W, H = 1500, 920
    img = gradient(W, H, (250, 252, 255), (225, 234, 252))
    d = ImageDraw.Draw(img)
    DARK = (28, 38, 62); GOLD = (255, 201, 77)
    d.rounded_rectangle([24, 24, W - 24, H - 24], radius=28, outline=(46, 74, 143), width=4)
    d.rounded_rectangle([40, 40, W - 40, H - 40], radius=22, outline=GOLD, width=2)

    d.text((80, 66), "（你的姓名）", font=F(50, True), fill=DARK)
    d.rounded_rectangle([420, 76, 690, 132], radius=28, fill=GOLD)
    d.text((555, 104), "DI · 指挥官 + 社交者", font=F(27, True), fill=(90, 60, 0), anchor="mm")
    d.text((W - 80, 76), "星火电赛战队 · 团队协作名片", font=F(27, True), fill=(46, 74, 143), anchor="ra")
    d.text((W - 80, 118), "—— 给队友的《使用说明书》", font=F(22), fill=(120, 130, 150), anchor="ra")

    cols = [
        ("能力宣言", (74, 144, 226), "我能快速抓住目标，把模糊想法变成可执行的行动计划，并用我的感染力让全队愿意一起干。"),
        ("协作说明书", (124, 179, 66), "找我决策请直接说重点，带两个方案并说明利弊；我行动快、喜欢当场拍板，这不是忽视你的意见——有不同想法请直接打断我；如果我在讨论中打断了你，提醒我停下来听你说完。"),
        ("主动担当", (232, 163, 61), "团队士气低落或没人牵头时，我来当启动者：组织分工、对外沟通（路演、答辩、对接老师与基地资源）；讨论冷场时我来破冰。"),
    ]
    cw, gap = 430, 26
    x = 80
    for title, col, body in cols:
        d.rounded_rectangle([x, 190, x + cw, 700], radius=18, fill=(255, 255, 255), outline=(200, 212, 235), width=2)
        d.rectangle([x, 190, x + cw, 246], fill=col)
        d.text((x + cw / 2, 218), title, font=F(30, True), fill=(255, 255, 255), anchor="mm")
        lines = wrap(d, body, F(24), cw - 60)
        yy = 284
        for ln in lines:
            d.text((x + 30, yy), ln, font=F(24), fill=(50, 60, 85))
            yy += 40
        x += cw + gap

    d.rounded_rectangle([80, 736, W - 80, 856], radius=16, fill=(255, 243, 224), outline=(232, 163, 61), width=2)
    d.text((110, 758), "⚠ 雷区（我的底线）", font=F(26, True), fill=(180, 100, 20))
    d.text((110, 800), "反复讨论却不拍板；否定方案却不给依据；让我只能当背景板。想让我配合，请直接说明目标和你认为可行的办法。",
           font=F(22), fill=(120, 80, 30))
    img.save(os.path.join(OUT, "电子名片.png"))
    print("namecard ok")

make_poster(); make_johari(); make_mindmap(); make_namecard()
