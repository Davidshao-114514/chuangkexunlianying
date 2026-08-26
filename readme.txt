UserApp - CW32L010F8 应用框架
================================
基于 CW32L010 标准库例程 (参考 GPIO/gpio_blink 工程结构),
软件开关支持外挂款/内置款两种型号, 见 USER\inc\app_config.h。

型号区别 (烧录前修改 app_config.h 的 APP_PRODUCT_VARIANT, 重新编译):
  外挂款 EXTERNAL (默认):
    - 磁吸 4pin 外接 LED (3V3/GND/LED-/DET), 吸附检测: 高=已连接
    - 检测引脚: PA01(OSC-)=组1, PA00(OSC+)=组2 (无外部晶振, 复用 OSC)
    - 按键 5 个: PA02 PA04 PA05 PA06 PB03
    - 未吸附的组不输出 PWM (防空载)
  内置款 BUILTIN:
    - LED 内置于整机, 无检测 (视为已连接)
    - PA00/PA01 恢复为按键, 共 7 个: PA00 PA01 PA02 PA04 PA05 PA06 PB03

引脚分配 (原理图):
  PB04(CE)   = LDO 使能            -> bsp_pin.h / LDO_CE_Enable()
  PB05(SDA)  = OLED IIC SDA        -> bsp_i2c.c (软件I2C, 参考 H563 bsp_i2c)
  PB06(SCL)  = OLED IIC SCL
  PB07/NRST  = 系统复位 (OLED RST 与复位相连, 无需 GPIO)
  PB00(VBAT) = 电池电压采样 AIN7    -> bsp_adc.c
  PB01(PB1)  = PWM1, ATIM_CH2 -> 组1 (SY7200 EN/PWM, 20kHz, 2400级)
  PA03(PA3)  = PWM2, ATIM_CH3 -> 组2 (SY7200 EN/PWM)

系统: 无外部晶振, HSI 48MHz (SYSCTRL_HSIOSC_DIV1)
按键功能:
  外挂款: BTN1 开关机 / BTN2,3 亮度-+ / BTN4 分组切换 / BTN5 全部亮灭
  内置款: BTN1 开关机 / BTN2,3 亮度-+ / BTN4 分组切换 /
          BTN5 组1亮灭 / BTN6 组2亮灭 / BTN7 全部亮灭
关机: BTN1 使 LDO(CE) 断电并进入 STOP 停机模式, 任意按键唤醒恢复。

OLED 驱动由 H563 工程 bsp_oled/bsp_i2c 移植 (SSD1306 0.91" 128x64, 地址 0x3C)。

使用:
  用 Keil MDK5 打开 MDK\Project.uvprojx, F7 编译, 下载到 CW32L010F8 即可。
  切换型号: 改 app_config.h 一行 -> 重新编译烧录。

请注意: 编译前确认已安装 WHXY.CW32L010_DFP 1.0.2 器件包 (Keil Pack Installer)。
