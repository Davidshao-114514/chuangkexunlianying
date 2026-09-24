#ifndef __BSP_BUTTON_H
#define __BSP_BUTTON_H

#include "cw32l010.h"
#include "cw32l010_gpio.h"

/* 按键扫描 (有效电平见 bsp_pin.h 的 BTN_ACTIVE_LEVEL): BTN1=PB03, BTN2=PA04, BTN3=PA05 (仅3键)
 * 去抖 15ms, 返回按下的按键位掩码 (bit0=BTN1 ... bit2=BTN3)
 * 调用间隔推荐 5ms 左右, 非阻塞 */

#define BTN1_MASK           0x01
#define BTN2_MASK           0x02
#define BTN3_MASK           0x04

#define BTN_DEBOUNCE_COUNT  3       /* 连续 3 次一致判定 (5ms x 3 = 15ms) */

void BSP_BTNs_Init(void);
uint8_t BSP_BTNs_Scan(void);        /* 返回本次新按下的按键位掩码 */
uint8_t BSP_BTNs_GetState(void);    /* 返回当前稳定电平掩码 (1=按下) */

#endif /* __BSP_BUTTON_H */
