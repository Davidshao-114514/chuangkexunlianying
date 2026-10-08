#ifndef __BSP_PWM_H
#define __BSP_PWM_H

#include "cw32l010.h"
#include "cw32l010_atim.h"
#include "cw32l010_gpio.h"

/* ATIM PWM 输出 (SY7200 EN/PWM 调光引脚)
 * PWM1: PB01 (引脚12) -> ATIM_CH2 -> SY7200 EN/PWM (组1)
 * PWM2: PA03 (引脚13) -> ATIM_CH3 -> SY7200 EN/PWM (组2)
 * 系统时钟 48MHz (HSI), 计数时钟 48MHz
 *
 * [调光频率] 驱动芯片为 RY3730 (pin-to-pin 替代 SY7200, 更经济),
 *   手册(应用信息-调光控制)原文:
 *     "preventing the flicker issue, the selected PWM frequency is
 *      >=100Hz and <=10KHz"
 *   -> PWM 调光频率必须在 100Hz ~ 10kHz 内, 否则出现频闪
 *   本工程: PWM_FREQ_HZ = 8kHz (区间偏高段)
 *     - 频率取偏高: 每个周期输出波动小, 低亮度不闪
 *     - 1kHz 曾实测低占空比频闪 (关断期过长, 输出电容放电过深+IC 低频重启)
 *     - 20k/30kHz 曾超上限 (频闪/啸叫)
 *     - 计数时钟 = 48MHz -> ARR = 5999 -> 6000 级亮度
 *   调优提示: 若想进一步降低低亮度功耗, 在"不闪"的前提下把频率逐步下调
 *   (5k->9599, 4k->11999, 3k->15999, 2k->23999), 找到刚好不闪的最低频
 *
 * 说明: ATIM 仅作 PWM 输出, 未使用任何 ATIM 中断;
 *       系统时基/ADC/按键调度均在 BTIM1 1ms 中断, 与本频率无关
 */

#define PWM_CLK_HZ          48000000    /* SYSCTRL_HSIOSC_DIV1 = 48MHz */
#define PWM_PRESCALER       0           /* 1 分频 -> 计数时钟 48MHz */
#define PWM_FREQ_HZ         8000        /* RY3730 EN/PWM 调光: 100Hz~10kHz (手册) */
#define PWM_ARR             (PWM_CLK_HZ / (PWM_PRESCALER + 1) / PWM_FREQ_HZ - 1)
#define PWM_MAX_DUTY        (PWM_ARR + 1)

#define PWM_CH1             0           /* PB01 - ATIM_CH2 */
#define PWM_CH2             1           /* PA03 - ATIM_CH3 */

void BSP_PWM_Init(void);
void BSP_PWM_SetDuty(uint8_t ch, uint16_t permille);       /* 0..1000 (千分数) */
void BSP_PWM_Start(void);
void BSP_PWM_Stop(void);

#endif /* __BSP_PWM_H */
