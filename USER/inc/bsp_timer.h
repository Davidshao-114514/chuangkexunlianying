#ifndef __BSP_TIMER_H
#define __BSP_TIMER_H

#include "cw32l010.h"
#include "cw32l010_btim.h"

/*******************************************************************************
 * BSP_TIMER - 周期定时器 (BTIM1)
 *
 * 功能: 产生 1ms 的定时中断, 作为全局系统时基, 驱动按键扫描/ADC采样/
 *       界面刷新等周期任务 (任务代码见 main.c 的 App_Task1ms()).
 *
 * 时基计算: HSI 48MHz -> BTIM 预分频 8 -> 计数时钟 6MHz -> Period=5999 -> 1ms
 ******************************************************************************/

#define TIMER_CLK_HZ        48000000    /* 系统时钟 PCLK = 48MHz */
#define TIMER_PSC           7           /* BTIM 预分频 (2^n) 8分频 -> 6MHz */
#define TIMER_PERIOD        5999        /* 6MHz/6000 = 1ms */

/* 系统时基 (由 ISR 维护, 单位 ms) */
extern volatile uint32_t g_ms_tick;

void BSP_TIMER_Init(void);

#endif /* __BSP_TIMER_H */
