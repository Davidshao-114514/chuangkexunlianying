# -*- coding: utf-8 -*-
"""数值一致性校验：所有派生数字在此集中核对"""
import data_res as d

print("=" * 60)
print("资源台账")
print(" 人力机会成本", d.LABOR_COST, " 显性", d.CASH_SPENT, " 总投入", d.TOTAL_RESOURCE_COST)
print(" 隐性占比", round(d.IMPLICIT_RATIO * 100, 1), "%")
print(" 全成本/条", round(d.COST_PER_DATA, 2), " 现金/条", round(d.CASH_PER_DATA, 2), " 现金/付费数据", round(d.CASH_PER_PAID, 2))
print(" 本单元阶段投入", d.STAGE_COST, " 新增数据", d.NEW_DATA, " 增量成本/条", round(d.NEW_COST / d.NEW_DATA, 2))
print(" 当前累计", d.NOW_COST, "/", d.NOW_DATA, "=", round(d.NOW_COST / d.NOW_DATA, 2))
print(" 调整期", d.MID_ADJ_COST, "/", d.MID_ADJ_DATA, "=", round(d.MID_ADJ_COST / d.MID_ADJ_DATA, 2))

print("=" * 60)
print("单位经济（量产）")
for i, tag in enumerate(["基准", "调整", "当前"]):
    print(f" {tag}: 单位变动成本 ¥{d.UNIT_VAR[i]}  加权贡献 ¥{d.W_CONTRIB[i]}  含人力保本 {d.BE_LABOR[i]} 台  不含人力 {d.BE_CASH[i]} 台")
print(" 安全边际", round(d.SAFETY, 2), " SOM", d.SOM_UNITS)
price = {"标准版": 65, "青春版": 45, "实训套件版": 49, "B 端实训套装": 59}
mix = {"标准版": 0.30, "青春版": 0.15, "实训套件版": 0.25, "B 端实训套装": 0.30}
print(" 加权均价", round(sum(price[k] * mix[k] for k in price), 2))
# 小批口径
print(" 小批加权贡献 7.97 → 含人力保本", round((d.FIXED_TOTAL + d.LABOR_COST) / 7.97))

print("=" * 60)
print("缺口难度折价", d.GAP_COST_DIFF)
print(" P0 相关投入占比", round(1070 / d.STAGE_COST * 100, 1), "%")
print("=" * 60)
print("缺陷数", len(d.DEFECTS), "| 来源归并", d.FB_UNIQUE_SRC, "合计", sum(d.FB_UNIQUE_SRC))
from collections import Counter
print(" 优先级分布", Counter(x[4] for x in d.DEFECTS))
print(" 维度分布", Counter(x[3] for x in d.DEFECTS))
print(" 来源分布", Counter(x[1].split("（")[0] for x in d.DEFECTS))
print("=" * 60)
print("仪表盘", len(d.DASHBOARD), "行 | 结果表", len(d.RESULT_TABLE), "行 | 画布修改", len(d.CANVAS_CHANGES), "处")
print("5Why", len(d.FIVEWHY), "条 | 反思", len(d.REFLECTIONS), "份 | 能力", len(d.ABILITIES))
print("能力变化说明字数（含标点）", len(d.ABILITY_TEXT))
print("=" * 60)
print("组合增值率校验：产出价值 / 投入")
gain = 26 * 30 + 19 * 18 + 20 * 18.67
print(" 组合产出价值", round(gain), " 投入", 120 + 12 * 25, "→ 增值率", round(gain / (120 + 12 * 25), 2))
print(" 单一资源：设备", round(570 / 180, 2), "地推", round(22 * 18 / 340, 2), "线上", round(11 * 18 / 200, 2))
avg_single = (570 / 180 + 22 * 18 / 340 + 11 * 18 / 200) / 3
print(" 单一平均", round(avg_single, 2), "→ 协同系数", round((gain / (120 + 12 * 25)) / avg_single, 2))
