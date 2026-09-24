# CW32L010 UserApp - 磁吸 LED 灯控固件框架

基于 **武汉芯源 CW32L010F8** (Cortex-M0+, TSSOP20, 64KB Flash / 4KB RAM) 的完整应用框架，
Keil MDK5 (uVision) + **AC6 (ARMCLANG)** 编译，所有外设时钟来自 **无源 HSI 48MHz**（无外部晶振）。

## 功能特性

- **HSI 48MHz 单时钟**：`SYSCTRL_HSIOSC_DIV1`，HSE/LSE 不使用，OSC 引脚复用为检测口
- **双组 PWM 调光**：ATIM_CH2(PB01) / ATIM_CH3(PA03)，20kHz，2400 级，适配 SY7200 EN/PWM (20kHz~1MHz)
- **0.91" OLED**：SSD1306 **128x32** (4 页)，软件 I2C (PB05/PB06)，驱动自 H563 工程移植
- **磁吸 4pin 外接 LED 吸附检测**（外挂款）：复用 OSC- (PA01)/OSC+ (PA00)，高电平=已吸附；未吸附禁止输出
- **电池电压监测**：PB00 = ADC_IN7，**10K/10K 分压 (VBAT/2)**，50ms 采样 + 8 次均值
- **软件过放保护**：<3.5V 低电提醒（告警页/闪烁）；<3.2V 关断输出；2s 确认 + 滞回 (3.55/3.35V) 防振荡；告警页可按键关屏，1 分钟无操作自动关屏省电
- **低功耗**：关机 → LDO(CE) 断电 + STOP 停机（GPIO 下降沿唤醒），任意按键唤醒自动恢复
- **双型号软件开关**：`app_config.h` 一行切换 外挂款 / 内置款

## 完整引脚关系图

### 1. 总体拓扑

```
 电池 V+/V- ────────────────────────────────────────────────────────────┐
     │                                                                 │
     ├─[10K]──┐                                                        │
     │        └──────────┐   VBAT/2  (采样点)                          │
     └────────[10K]──GND──┤    │                                       │
                          ▼    ▼                                       │
      ┌────────────────────────────────────────────────────────────┐  │
      │                    CW32L010F8 (TSSOP20)                    │  │
      │          HSI 48MHz / 内核 / 无外部晶振                      │  │
      │  PB00 ADC_IN7 ←──(10K/10K 分压采样)─────────────────────────┼──┘
      │    PA01(OSC-) ◄── DET1 磁吸接口1 检测线 ────────────────────┼─▶ 3.3V(灯端)
      │    PA00(OSC+) ◄── DET2 磁吸接口2 检测线 ────────────────────┼─▶ 3.3V(灯端)
      │    PB01 ATIM_CH2 ── PWM 低边开关 ──▶ LED1-〔SY7200 EN/PWM〕 ┼─▶ 组1 LED
      │    PA03 ATIM_CH3 ── PWM 低边开关 ──▶ LED2-〔SY7200 EN/PWM〕 ┼─▶ 组2 LED
      │    PB04 CE ──▶ LDO 使能 (LDO→3.3V 输出/或直接给灯组供电)     │
      │    PB05 SDA ────▶ OLED SSD1306 (0.91", 128x32, I2C 0x3C)    │
      │    PB06 SCL ────▶                                        ▲  │
      │    PB07/NRST ────▶ OLED RST (并联系统复位)                 │  │
      │    PA02 PA04 PA05 PA06 PB03 ── 按键(外部上拉, 按下为低)     │  │
      │    (内置款: +PA00 PA01 作按键)                              │  │
      │    PA07/PA08 ── SWDIO/SWCLK 调试口                          │  │
      └────────────────────────────────────────────────────────────┘
```

### 2. MCU 引脚全表 (TSSOP20)

| 引脚 | 名称 | 功能 | 接口 (原理图丝印) | 方向/配置 |
|---|---|---|---|---|
| 1 | PB04 | LDO 使能 | CE | 输出 PP，有效电平可配 |
| 2 | PB05 | OLED SDA | SDA | 软件 I2C，开漏+上拉 |
| 3 | PB06 | OLED SCL | SCK (丝印) | 软件 I2C，开漏+上拉 |
| 4 | PB07/NRST | 系统复位 | RST (OLED RST 并联) | 复位输入 |
| 5 | PA00 | OSC+ | 外挂款=DET2 / 内置款=按键 | 输入(外部下拉)/上拉输入 |
| 6 | PA01 | OSC- | 外挂款=DET1 / 内置款=按键 | 输入(外部下拉)/上拉输入 |
| 7 | VSS | 地 | — | — |
| 8 | Vcore | 稳压器输出 | C13/C11 100nF+1uF | — |
| 9 | VDD | 电源 | 3.3V | — |
| 10 | PA02 | 按键 BTN1 | — | 上拉输入, 按下低 |
| 11 | PB00 | 电池采样 | VBAT | ADC_IN7, 10K/10K |
| 12 | PB01 | PWM1 输出 | PB1 | ATIM_CH2 → SY7200 EN (组1) |
| 13 | PA03 | PWM2 输出 | PA3 | ATIM_CH3 → SY7200 EN (组2) |
| 14 | PA04 | 按键 BTN2 | — | 上拉输入, 按下低 |
| 15 | PA05 | 按键 BTN3 | — | 上拉输入, 按下低 |
| 16 | PA06 | 按键 BTN4 | — | 上拉输入, 按下低 |
| 17 | PA07/SWDIO | 调试 | — | SWDIO |
| 18 | PA08/SWCLK | 调试 | — | SWCLK |
| 19 | PB02 | 未使用 | X (原理图叉掉) | — |
| 20 | PB03 | 按键 BTN5 | — | 上拉输入, 按下低 |

### 3. 磁吸 4pin 接口 (每灯组一个, 共 X2)

```
 磁吸接口(组1)              磁吸接口(组2)
 ┌──────────┐                ┌──────────┐
 │ ① 3V3    │──3.3V─        │ ① 3V3    │──3.3V─
 │ ② GND    │──GND──        │ ② GND    │──GND──
 │ ③ LED-   │──PWM1(PB01)── │ ③ LED-   │──PWM2(PA03)──▶ SY7200 EN/PWM
 │ ④ DET    │──PA01(OSC-)── │ ④ DET    │──PA00(OSC+)──▶ 检测输入
 └──────────┘                └──────────┘
   灯端接线: ① 3V3 ─▶ LED+ / DET(内部短接3V3)     ← 吸附后 DET 检测线被拉高
             ④ DET ▲ 线侧下拉电阻(如10K)到 GND     ← 未吸附时 DET = 低电平
             ③ LED- ◀─ SY7200 EN/PWM 低边开关     ← 20kHz PWM 调光
```

### 4. 器件级接线说明

| 器件 | 接口 | 说明 |
|---|---|---|
| OLED (SSD1306 0.91") | SCL=PB06, SDA=PB05, RST=PB07/NRST | 软件 I2C @~100kHz, 地址 0x3C; 128x32 4 页 |
| LED (经 SY7200) | EN/PWM = PB01/PA03 | 20kHz, 2400 级; PWM 高=亮 |
| 磁吸 DET | PA00/PA01, 外部下拉 + 灯端 3.3V | 高=已吸附; 未吸附组不输出 |
| LDO | CE = PB04 | 关机断电 (GPIO 即可/有效电平 CE_ACTIVE_LEVEL 可配) |
| 电池采样 | PB00 + 10K/10K | VBAT/2, 测限 6.6V |
| 按键 | PA02/PA04/PA05/PA06/PB03 (+PA00/PA01 内置款) | 内部上拉, 按下低; 作 STOP 唤醒 |
| 调试 | PA07(SWDIO)/PA08(SWCLK) | SWD 烧录/调试 |

## 软件开关：外挂款 / 内置款

`USER/inc/app_config.h`：

```c
#define APP_PRODUCT_VARIANT   PRODUCT_VARIANT_EXTERNAL   // 外挂款 (默认)
#define APP_PRODUCT_VARIANT   PRODUCT_VARIANT_BUILTIN    // 内置款
```

| | 外挂款 | 内置款 |
|---|---|---|
| 吸附检测 | 启用 (PA00/PA01) | 无（视为已连接） |
| 按键 | 5 个：PA02 PA04 PA05 PA06 PB03 | 7 个：+PA00 PA01 |
| 按键功能 | 1:PWR 2/3:亮度∓ 4:分组 5:全亮灭 | 同左 +5:G1亮灭 6:G2亮灭 7:全亮灭 |
| 界面 | 显示 D1/D2 吸附检测 | 显示 CUR 当前组 |

## 软件架构（参考 STM32H563 工程分层）

```
Main Loop ── OLED 界面刷新 (UI_StaticInit / UI_RefreshValues)
     ▲
BTIM1 1ms 中断 (interrupts_cw32l010.c)
   ├─ 1ms  系统时基 / 告警页自动关屏倒计时
   ├─ 5ms  按键扫描 / 吸附检测 / 输出联动
   ├─ 50ms VBAT 采样 + 电池保护状态机
   └─ 200ms 界面刷新请求
```

| 文件 | 职责 |
|---|---|
| `USER/src/main.c` | 初始化、电池保护状态机、按键逻辑、OLED 界面内容 |
| `USER/src/bsp_power.c` | STOP 休眠 + 按键唤醒 |
| `USER/src/bsp_timer.c` | BTIM1 1ms 时基 |
| `USER/src/bsp_pwm.c` | ATIM 20kHz PWM / 2400 级调光 |
| `USER/src/bsp_adc.c` | VBAT 分压采样 (10K/10K) |
| `USER/src/bsp_button.c` | 按键扫描 (去抖 15ms) |
| `USER/src/bsp_detect.c` | 磁吸吸附检测 (100ms 去抖) |
| `USER/src/bsp_i2c.c` | 软件 I2C (OLED) |
| `USER/src/bsp_oled.c` | SSD1306 显示原语 (6x8 ShowStr) |
| `CW32L010_Lib/` | 内嵌 CW32L010 标准库 (Libraries/startup/retarget) |

## 构建与烧录

1. Keil MDK **Pack Installer** 安装 `WHXY.CW32L010_DFP 1.0.2`（MDK 5.35+）
2. 打开 `MDK/Project.uvprojx` → F7 编译（AC6 / ARMClang）
3. 连接 SWD (PA07/PA08) 下载；低功耗演示需接电池 + 磁吸灯

程序体积约：Code 8.1KB / RO 1.0KB / RAM 1.1KB（Flash ~14%，RAM ~27%）。

## 版本

- v1.0: 首版框架（PWM/OLED/按键/检测/保护/低功耗/双型号）
