#ifndef __BSP_PIN_H
#define __BSP_PIN_H

#include "cw32l010.h"
#include "cw32l010_gpio.h"
#include "app_config.h"

/*******************************************************************************
 * 开发板引脚分配 (原理图, MCU: CW32L010F8, TSSOP20)
 *
 *  引脚号   MCU引脚        功能
 *  -----------------------------------------------
 *    1    PB04  (CE)   LDO 使能 (GPIO 输出)
 *    2    PB05  (SDA)  OLED IIC SDA (软件IIC)
 *    3    PB06  (SCK)  OLED IIC SCL (软件IIC; 丝印SCK)
 *    4    PB07/NRST    系统复位/OLED RST (不再作按钮)
 *    5    PA00 (OSC+)  磁吸接口组2 吸附检测 (高=已连接)
 *    6    PA01 (OSC-)  磁吸接口组1 吸附检测 (高=已连接)
 *   10    PA02         (未用)
 *   14    PA04         按键 BTN2
 *   15    PA05         按键 BTN3
 *   16    PA06         (未用)
 *   11    PB00 (VBAT)  电池电压采样 (ADC_IN7)
 *   12    PB01 (PB1)   PWM1 输出 (ATIM_CH2) -> LED组1
 *   13    PA03 (PA3)   PWM2 输出 (ATIM_CH3) -> LED组2
 *   20    PB03         按键 BTN1
 *   19    PB02         未引出 (原理图 X)
 *   17/18 PA08/PA07    SWCLK/SWDIO 调试口
 *
 * 磁吸接口 (4pin, 每灯组一个):
 *   1) 3V3  板侧输出 3.3V 供 LED 端
 *   2) GND  地
 *   3) LED- LED 灯条负极 (由 PWM 低边开关驱动)
 *   4) DET  检测线: LED 端 3V3 接到检测线 -> 吸附后 3.3V 拉高
 *   板侧: DET 经下拉电阻到地 (未吸附=低), MCU 检测线输入高电平 = 已吸附
 *   注意: 未用外部晶振, OSC+/OSC- (PA00/PA01) 复用为检测端口
 ******************************************************************************/

/* ============================ LDO 使能 CE (PB04) ============================ */
#define CE_GPIO_PORT         CW_GPIOB
#define CE_GPIO_PINS         GPIO_PIN_4
#define CE_ACTIVE_LEVEL      1       /* 1 = 高电平使能 LDO; 0 = 低电平使能 */

#define LDO_CE_Enable()      (CE_ACTIVE_LEVEL ? (CE_GPIO_PORT->BSRR = CE_GPIO_PINS) \
                                              : (CE_GPIO_PORT->BRR  = CE_GPIO_PINS))
#define LDO_CE_Disable()     (CE_ACTIVE_LEVEL ? (CE_GPIO_PORT->BRR  = CE_GPIO_PINS) \
                                              : (CE_GPIO_PORT->BSRR = CE_GPIO_PINS))
#define LDO_CE_GetState()    ((CE_GPIO_PORT->IDR & CE_GPIO_PINS) != 0)

/* ============================ OLED IIC (PB05/PB06) =========================== */
#define OLED_SCL_PORT        CW_GPIOB
#define OLED_SCL_PIN         GPIO_PIN_6
#define OLED_SDA_PORT        CW_GPIOB
#define OLED_SDA_PIN         GPIO_PIN_5

/* ============================= 电压采样 VBAT (PB00) =========================== */
#define VBAT_GPIO_PORT       CW_GPIOB
#define VBAT_GPIO_PINS       GPIO_PIN_0
#define VBAT_ADC_CHANNEL     ADC_InputCH7   /* PB00 = ADC_IN7 */

/* ============================== PWM 输出 (ATIM) =============================== */
/* PWM1: PB01 (引脚12) -> ATIM_CH2 -> LED组1;  PWM2: PA03 (引脚13) -> ATIM_CH3 -> LED组2 */
#define PWM1_GPIO_PORT       CW_GPIOB
#define PWM1_GPIO_PINS       GPIO_PIN_1
#define PWM2_GPIO_PORT       CW_GPIOA
#define PWM2_GPIO_PINS       GPIO_PIN_3

/* ==================== 磁吸接口 LED 吸附检测 (复用 OSC 引脚) ==================== */
/* 高电平 = LED 已吸附 (要求板侧/灯端有下拉电阻, 灯端 3V3 接检测线)
 * 仅外挂款启用; 内置款时 PA00/PA01 作普通按键 */
#if BSP_DETECT_ENABLED
#define DET1_GPIO_PORT       CW_GPIOA
#define DET1_GPIO_PINS       GPIO_PIN_1           /* OSC- : LED组1 (PWM1/PB01) 吸附检测 */
#define DET2_GPIO_PORT       CW_GPIOA
#define DET2_GPIO_PINS       GPIO_PIN_0           /* OSC+ : LED组2 (PWM2/PA03) 吸附检测 */
#endif

/* =============================== 按键 =============================== */
/* 按键有效电平: 1=按下为高 (外部下拉, 本板实际接线), 0=按下为低 (内部上拉) */
#define BTN_ACTIVE_LEVEL     1
/* 仅 3 个按键: BTN1=PB03, BTN2=PA04, BTN3=PA05 (其余引脚无按键) */
#define BTN_MAX_NUM          3
static const GPIO_TypeDef *const BTN_PORT[BTN_MAX_NUM] = { CW_GPIOB, CW_GPIOA, CW_GPIOA };
static const uint16_t BTN_PIN[BTN_MAX_NUM] = { GPIO_PIN_3, GPIO_PIN_4, GPIO_PIN_5 };

#endif /* __BSP_PIN_H */
