#ifndef __BSP_POWER_H
#define __BSP_POWER_H

#include "cw32l010.h"

/*******************************************************************************
 * BSP_POWER - 低功耗管理 (停机模式 STOP)
 *
 * 关机流程 (main.c): 关闭 LDO(CE) + PWM 归零
 *                        -> BSP_POWER_EnterStop(): 关外设时钟, 按键配置为
 *                           下降沿中断唤醒, 进入 STOP 模式 (WFI)
 *   -> 任意按键按下 -> GPIOA/GPIOB 中断 -> 唤醒 -> WFI 返回
 * 唤醒流程 (main.c): BSP_POWER_WakeupInit(): 恢复时钟/外设/按键扫描
 *                        -> LDO(CE) 上电 -> 恢复 PWM 输出 -> 刷新界面
 * 唤醒引脚: 全部 7 个按键 (PA00 PA01 PA02 PA04 PA05 PA06 PB03), 按下为低
 ******************************************************************************/

void BSP_POWER_EnterStop(void);     /* 进入停机, 唤醒后返回 */
void BSP_POWER_WakeupInit(void);    /* 唤醒后恢复 (时钟/外设/按键/中断) */

#endif /* __BSP_POWER_H */
