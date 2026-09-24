#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C"
{
#endif

#include "app_config.h"
#include "cw32l010.h"
#include "cw32l010_gpio.h"
#include "cw32l010_sysctrl.h"
#include "cw32l010_atim.h"
#include "cw32l010_adc.h"
#include "interrupts_cw32l010.h"
#include "system_cw32l010.h"

#include "bsp_pin.h"
#include "bsp_i2c.h"
#include "bsp_oled.h"
#include "bsp_pwm.h"
#include "bsp_adc.h"
#include "bsp_button.h"
#include "bsp_timer.h"
#include "bsp_power.h"
#include "bsp_detect.h"

/* ---- 低功耗: 关机后请求进入停机模式 (ISR置位, 主循环执行) ---- */
extern volatile uint8_t g_sleep_req;            /* 1 = 请求进入 STOP 休眠 */

/* ---- 周期任务 (由 BTIM1 1ms 中断调用, 实现在 main.c) ---- */
extern void App_Task1ms(void);              /* 1ms 周期任务: 按键/ADC/界面刷新调度 */

/* ---- 界面层 (实现在 main.c) ---- */
extern volatile uint8_t g_ui_req;           /* 界面刷新请求标志 (ISR置位, 主循环清零) */
extern void UI_StaticInit(void);            /* 画静态标签 (上电一次) */
extern void UI_RefreshValues(void);         /* 刷新数值区 (周期调用) */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
