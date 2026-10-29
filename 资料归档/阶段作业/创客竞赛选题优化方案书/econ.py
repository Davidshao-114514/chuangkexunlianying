# -*- coding: utf-8 -*-
"""选题优化方案书 —— 经济模型与迭代实测数据（单一数据源）"""

# ============ 一、迭代实测数据（48 小时再验证） ============

# 1. 分层抽样问卷（替代课前的便利抽样）
SURVEY = dict(
    n=87,
    strata={"电子类": 42, "机械类": 22, "计算机类": 23},
    grades={"大二": 38, "大三": 31, "大四": 18},
    intent_buy=62,        # 表示"肯定会买或可能会买"
    intent_sure=38,       # 表示"肯定会买"
    margin_err="±10.5%",  # 1.96*sqrt(.25/87)
)

# 2. 预售页 A/B 双价格锚定
PREA_B = dict(
    A=dict(anchor="59 / 69 元", n=44, order=14),
    B=dict(anchor="79 / 89 元", n=43, order=9),
)

# 3. 1 元可退意向金（态度→行为）
DEPOSIT = dict(invited=62, paid=20)

# 4. PSM 价格敏感度
PSM = dict(too_cheap=35, opp=62, acceptable=(45, 89), too_expensive=119)

# 5. 三渠道并行获客测试
CHANNELS = [
    # 名称, 曝光, 留资, 现金成本(元), 人力(人时)
    ("电工基地 / 实训课门口地推", 63, 22, 40, 6),
    ("创客空间 / 社团宣讲", 48, 13, 0, 6),
    ("线上（电赛群 + B 站投放）", 210, 11, 200, 6),
]
LABOR_RATE = 25.0   # 元/人时（学生兼职机会成本）

# 6. 14 天推荐率与 NPS 回访
NPS = dict(n=20, promoters=9, passives=8, detractors=3)

# 7. 民族志行为观察（5 人 × 3 天）
ETHNO = dict(users=5, days=3, obs=15, no_reset=13,
             find_light_per20min=4.2, move_lamp_per20min=2.6)

# 8. LED vs OLED 状态查询 A/B（配对设计）
AB_LED = dict(n=20, a_cover=0.82, b_cover=0.86, a_score=4.2, b_score=4.4,
              a_query=1.6, b_query=1.4, a_sec=4.2, b_sec=4.0)

# 9. 技术假设复测
TECH = dict(magnet_kg=3.2, magnet_std=2.5, drift_deg=3.8, drift_std=5.0,
            cycles=3000, flicker="无可见条纹", temp_c=52)

# 10. 竞品量化实测（20 cm 处，手机照度计 App，各测 3 次取均值）
COMPETITORS = [
    # 产品, 价格带, 照度lx, 光斑直径cm, 瞄准自由度(0-5), 空间占用(0-5,5=零占位), 状态显示
    ("传统台灯", "60-200 元", 420, 12.0, 2, 2, "无"),
    ("廉价便携灯", "20-49 元", 260, 18.0, 1, 3, "无"),
    ("专业工业灯", "300 元+", 1100, 8.0, 4, 1, "无"),
    ("磁吸焊接辅助手电（本方案）", "59-69 元", 780, 6.0, 5, 5, "LED 指示灯"),
]

# 11. 小批量 BOM 三档询价实测（LCSC + 机构件 3 家报价，取中位）
BOM_TIERS = [
    # 模块, 200 台, 1k 片, 10k 片
    ("PCBA（器件 + 贴装）", 28.0, 22.0, 18.5),
    ("机构件（磁铁 / 柔性臂 / 外壳 / 硅胶垫）", 22.0, 14.0, 9.5),
    ("包装与 Type-C 线材", 2.3, 1.6, 1.2),
]

# ============ 二、单位经济模型 ============

CHAN_RATE = 0.03   # 加权渠道费率（仅约 30% 销量走电商，佣金 5% + 推广 5%）
SVC_RATE = 0.03    # 售后与退换计提

# 小批量（200 台）售价与物料
SMALL = {
    "标准版":   dict(price=65, bom=52.3, logi=1.5),
    "青春版":   dict(price=45, bom=38.0, logi=1.5),
    "实训套件版": dict(price=49, bom=29.0, logi=3.0),
    "B 端实训套装": dict(price=59, bom=49.3, logi=0.0),
}
# 量产后（1k 片以上）物料
BULK_BOM = {"标准版": 37.6, "青春版": 33.0, "实训套件版": 24.0, "B 端实训套装": 35.0}
# 250 台起步预计的销量结构
MIX = {"标准版": 0.30, "青春版": 0.15, "实训套件版": 0.25, "B 端实训套装": 0.30}

FIXED = {"打样与工装（PCBA 打样、3D 打印耗材、夹具）": 3200,
         "注塑开模（量产前置投入）": 15000,
         "合规自测（RoHS 送检 + 锂电安全测试）": 3000,
         "测试设备与耗材（照度计、弹簧秤、热电偶、焊接耗材）": 1800}
LABOR_HOURS = 720     # 3 人 × 240 小时


def unit_econ():
    """返回两张表：小批量 / 量产后 的单位经济"""
    out = {}
    for label, bom in (("小批量（200 台）", None), ("量产后（1k 片以上）", BULK_BOM)):
        rows = []
        for k, v in SMALL.items():
            price = v["price"]
            material = v["bom"] if bom is None else bom[k]
            chan = round(price * CHAN_RATE, 2)
            svc = round(price * SVC_RATE, 2)
            var = round(material + v["logi"] + chan + svc, 2)
            contrib = round(price - var, 2)
            rows.append(dict(name=k, price=price, material=material, logi=v["logi"],
                             chan=chan, svc=svc, var=var, contrib=contrib,
                             rate=contrib / price,
                             mix=MIX[k]))
        weighted = round(sum(r["contrib"] * r["mix"] for r in rows), 2)
        fixed_total = sum(FIXED.values())
        be = round(fixed_total / weighted)
        be_with_labor = round((fixed_total + LABOR_HOURS * LABOR_RATE) / weighted)
        avg_price = round(sum(r["price"] * r["mix"] for r in rows), 2)
        out[label] = dict(rows=rows, weighted_contrib=weighted, fixed_total=fixed_total,
                          be=be, be_with_labor=be_with_labor, avg_price=avg_price,
                          labor_cost=LABOR_HOURS * LABOR_RATE)
    return out


ECON = unit_econ()

# LTV：按稳态（量产）单位贡献 × 复购系数 1.2
LTV = round(ECON["量产后（1k 片以上）"]["rows"][0]["contrib"] * 1.2, 1)

def channel_stats():
    rows = []
    for name, imp, lead, cash, hours in CHANNELS:
        cost = cash + hours * LABOR_RATE
        rows.append(dict(name=name, imp=imp, lead=lead, cost=cost,
                         rate=lead / imp, cac=round(cost / lead, 1)))
    return rows

CH = channel_stats()

# TAM / SAM / SOM
TAM = dict(engineer_students=700, need_ratio=0.35, diy=60)   # 万人 / 万人
SAM = dict(wuhan=5.3, online=2.0)                            # 万台
SOM_RATE = 0.042
SOM_UNITS = 3100


def pct(x, nd=1):
    return f"{x*100:.{nd}f}%"


if __name__ == "__main__":
    for k, v in ECON.items():
        print("=" * 20, k)
        for r in v["rows"]:
            print(f"{r['name']:<8} 售价{r['price']:>5} 物料{r['material']:>5} 变动{r['var']:>6} "
                  f"贡献{r['contrib']:>6} 毛利率{pct(r['rate']):>7}")
        print("加权单位贡献", v["weighted_contrib"], "固定成本", v["fixed_total"],
              "保本", v["be"], "含人力保本", v["be_with_labor"], "加权均价", v["avg_price"])
    print("LTV", LTV)
    for c in CH:
        print(c)
    print("BOM 小批合计", round(sum(r[1] for r in BOM_TIERS), 1),
          "千片合计", round(sum(r[2] for r in BOM_TIERS), 1),
          "万片合计", round(sum(r[3] for r in BOM_TIERS), 1))
