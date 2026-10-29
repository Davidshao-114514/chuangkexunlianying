# -*- coding: utf-8 -*-
"""重建数据区：11 条痛点连续排列（表头保留），避免重复/错位"""
import openpyxl
from openpyxl.styles import Font, Alignment

p = r'C:\Users\35464\Desktop\创客训练营\痛点知识领域映射表.xlsx'
wb = openpyxl.load_workbook(p)
ws = wb['Sheet1']

# 表头样式（若已存在则复用其字体）
f = Font(name='微软雅黑', size=10.5)
al = Alignment(vertical='center', wrap_text=True)

# 清空行 2-30 的数据区
for r in range(2, 31):
    for c in range(1, 5):
        ws.cell(row=r, column=c).value = None

rows = [
    ("18650电池价格较高，无法控制成本到有限预算", "□范围 □进度 √成本 □质量 □资源 □沟通 □风险", "预算策略不合理"),
    ("原型制作前两人都以为对方负责采购，没人带材料", "□范围 □进度 □成本 □质量 √资源 □沟通 □风险", "责任分配不清 / 资源管理缺失"),
    ("蓝帽没控制好时间，白帽红帽各用 20 分钟，后段草草收场", "□范围 □进度 □成本 □质量 □资源 √沟通 □风险", "沟通机制缺失"),
    ("调查对象都是基地学生", "□范围 □进度 □成本 □质量 □资源 □沟通 √风险", "风险意识缺失"),
    ("做到一半发现时间不够了（原型制作 20 分钟只完成 60%）", "□范围 √进度 □成本 □质量 □资源 □沟通 □风险", "进度失控 / 缺乏里程碑"),
    ("做着做着偏离了原来的目标（SCAMPER 优化方案从 3 项滚到 6 项）", "√范围 □进度 □成本 □质量 □资源 □沟通 □风险", "范围蔓延"),
    ("出了问题不知道找谁（跨组互测反馈没有跟进人）", "□范围 □进度 □成本 □质量 □资源 √沟通 □风险", "沟通机制缺失 / 责任不明"),
    ("出现意外只能临时救火（访谈放鸽子、材料规格买错现场借）", "□范围 □进度 □成本 □质量 □资源 □沟通 √风险", "风险意识缺失 / 无风险应对预案"),
    ("原型“差不多就行了”，互测时被指出没有使用场景说明", "□范围 □进度 □成本 √质量 □资源 □沟通 □风险", "质量把关缺失 / 无验收标准"),
    ("材料员 3 分钟交完材料后旁观，原型制作员超载", "□范围 □进度 □成本 □质量 √资源 □沟通 □风险", "忙闲不均 / 资源分配失衡"),
    ("信息不同步，成员 A 做了成员 B 已经完成的工作（重复劳动）", "□范围 □进度 □成本 □质量 □资源 √沟通 □风险", "信息同步机制缺失 / 沟通失败"),
]
for i, (pain, area, term) in enumerate(rows):
    r = 2 + i
    ws.cell(row=r, column=1, value=i + 1)
    ws.cell(row=r, column=2, value=pain)
    ws.cell(row=r, column=3, value=area)
    ws.cell(row=r, column=4, value=term)
    for c in range(1, 5):
        ws.cell(row=r, column=c).font = f
        ws.cell(row=r, column=c).alignment = al

wb.save(p)
print('rebuilt, data rows:', len(rows))
