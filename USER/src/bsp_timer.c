#include "bsp_timer.h"
#include "cw32l010_sysctrl.h"

/*******************************************************************************
 * BSP_TIMER - BTIM1 定时器初始化
 *
 * 参考 H563 工程的 tim.c (MX_TIM_Init 一类封装), 对应 CW32L010 的 BTIM1.
 ******************************************************************************/

volatile uint32_t g_ms_tick = 0;    /* 全局毫秒时基, 由 BTIM1 中断累加 */

void BSP_TIMER_Init(void)
{
    BTIM_TimeBaseInitTypeDef btim = {0};

    /* 打开 BTIM 时钟 */
    __SYSCTRL_BTIM123_CLK_ENABLE();

    /* 计数时钟: 48MHz / 8 = 6MHz */
    btim.BTIM_Mode      = BTIM_MODE_TIMER;
    btim.BTIM_Period    = TIMER_PERIOD;        /* 6MHz/6000 -> 1ms 中断 */
    btim.BTIM_Prescaler = TIMER_PSC;

    BTIM_TimeBaseInit(CW_BTIM1, &btim);

    /* 使能更新(溢出)中断, 启动定时器; 中断处理见 interrupts_cw32l010.c */
    BTIM_ITConfig(CW_BTIM1, BTIM_IT_UPDATE, ENABLE);
    BTIM_Cmd(CW_BTIM1, ENABLE);
}
