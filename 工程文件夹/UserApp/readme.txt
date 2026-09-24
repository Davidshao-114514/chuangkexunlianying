UserApp - CW32L010F8 应用框架
================================
基于 CW32L010 标准库 (内嵌 CW32L010_Lib), 详细说明见 README.md。

引脚关系 (TSSOP20):
  1  PB04(CE)   -> LDO 使能
  2  PB05(SDA)  -> OLED IIC SDA (软件I2C)
  3  PB06(SCK)  -> OLED IIC SCL
  4  PB07/NRST  -> 系统复位/OLED RST
  5  PA00(OSC+) -> 外挂款: 磁吸组2检测 / 内置款: 按键BTN6
  6  PA01(OSC-) -> 外挂款: 磁吸组1检测 / 内置款: 按键BTN7
  10 PA02       -> 按键 BTN1 (开关机)
  11 PB00(VBAT) -> 电池采样 ADC_IN7 (10K/10K 分压 VBAT/2)
  12 PB01(PB1)  -> PWM1: ATIM_CH2 -> SY7200 EN (磁吸组1 LED-)
  13 PA03(PA3)  -> PWM2: ATIM_CH3 -> SY7200 EN (磁吸组2 LED-)
  14 PA04       -> 按键 BTN2 (亮度-)
  15 PA05       -> 按键 BTN3 (亮度+)
  16 PA06       -> 按键 BTN4 (分组切换)
  17/18 PA07/PA08 -> SWDIO/SWCLK 调试
  19 PB02       -> 未使用 (原理图 X)
  20 PB03       -> 按键 BTN5 (全部亮灭, 内置款: 组1亮灭+6组2+7全部)

磁吸 4pin (每灯组一个): ① 3V3 ② GND ③ LED-(PWM低边) ④ DET(灯端3V3, 线侧下拉10K, 高=已吸附)

系统: 无外部晶振, HSI 48MHz; OLED 0.91" SSD1306 128x32 (4页, 6x8字体)
型号切换: USER/inc/app_config.h (外挂款/内置款)
过放保护: <3.5V告警, <3.2V关断, 滞回+2s确认; 告警页按键关屏/1分钟自动关屏
关机低功耗: BTN1 断电+STOP, 任意按键唤醒

编译: Keil MDK5 + AC6, 需安装 WHXY.CW32L010_DFP 1.0.2
