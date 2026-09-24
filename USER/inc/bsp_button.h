#ifndef __BSP_BUTTON_H
#define __BSP_BUTTON_H

#include "cw32l010.h"
#include "cw32l010_gpio.h"

/* 按键扫描 (按下为低):
 *   外挂款 BTN1..BTN5 = PA02 PA04 PA05 PA06 PB03
 *   内置款 BTN1..BTN7 = PA00 PA01 PA02 PA04 PA05 PA06 PB03
 * (型号切换见 app_config.h)
 * 去抖 12ms, 返回按下的按键位掩码 (bit0=BTN1 ... bit6=BTN7)
 * 调用间隔推荐 5ms 左右, 非阻塞 */

#define BTN1_MASK           0x01
#define BTN2_MASK           0x02
#define BTN3_MASK           0x04
#define BTN4_MASK           0x08
#define BTN5_MASK           0x10
#define BTN6_MASK           0x20
#define BTN7_MASK           0x40

#define BTN_DEBOUNCE_COUNT  3       /* 连续 3 次一致判定 (5ms x 3 = 15ms) */

void BSP_BTNs_Init(void);
uint8_t BSP_BTNs_Scan(void);        /* 返回本次新按下的按键位掩码 */
uint8_t BSP_BTNs_GetState(void);    /* 返回当前稳定电平掩码 (1=按下) */

#endif /* __BSP_BUTTON_H */
