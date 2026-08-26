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
 * [SY7200 调光频率要求] 20kHz ~ 1MHz
 *   本工程: PWM_FREQ_HZ = 20kHz (规格下限, 分辨率最优)
 *   计数时钟 = 48MHz -> ARR = 2399 -> 2400 级亮度 (0.04% 步进)
 */

#define PWM_CLK_HZ          48000000    /* SYSCTRL_HSIOSC_DIV1 = 48MHz */
#define PWM_PRESCALER       0           /* 1 分频 -> 计数时钟 48MHz */
#define PWM_FREQ_HZ         20000       /* SY7200 调光频率: 20kHz~1MHz */
#define PWM_ARR             (PWM_CLK_HZ / (PWM_PRESCALER + 1) / PWM_FREQ_HZ - 1)
#define PWM_MAX_DUTY        (PWM_ARR + 1)

#define PWM_CH1             0           /* PB01 - ATIM_CH2 */
#define PWM_CH2             1           /* PA03 - ATIM_CH3 */

void BSP_PWM_Init(void);
void BSP_PWM_SetDuty(uint8_t ch, uint16_t permille);       /* 0..1000 (千分数) */
void BSP_PWM_Start(void);
void BSP_PWM_Stop(void);

#endif /* __BSP_PWM_H */
