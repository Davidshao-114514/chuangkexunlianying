#ifndef __BSP_DETECT_H
#define __BSP_DETECT_H

#include "cw32l010.h"
#include "cw32l010_gpio.h"
#include "app_config.h"
#include "bsp_pin.h"

/* 仅外挂款启用; 内置款整个模块编译为空 */
#if BSP_DETECT_ENABLED

/*******************************************************************************
 * BSP_DETECT - 磁吸接口 LED 吸附检测
 *
 * 引脚 (原理图): DET1 = PA01 (OSC-), DET2 = PA00 (OSC+)
 * 电路: 检测线(DET) 板侧/线侧经下拉电阻到地; LED 端 3V3 接到检测线
 *       -> 未吸附 = 低电平, 吸附成功 = 高电平 (3.3V)
 * 复用说明: 不使用外部晶振, OSC+/OSC- 引脚可作为 GPIO 输入
 *
 * 全局函数:
 *   BSP_DETECT_Init()          初始化 (输入, 无内部上下拉, 依赖外部下拉)
 *   BSP_DETECT_Task()          5ms 周期任务: 去抖 + 状态更新
 *   BSP_DETECT_IsAttached(g)   查询: 0=灯组1, 1=灯组2; 返回 1=已吸附
 ******************************************************************************/

#define DETECT_DEBOUNCE_MS   5        /* 去抖采样周期 (5ms) */
#define DETECT_HOLD_CNT      20       /* 连续 20 次一致 (约100ms) */

void BSP_DETECT_Init(void);
void BSP_DETECT_Task(void);
uint8_t BSP_DETECT_IsAttached(uint8_t grp);      /* grp: 0=组1(PWM1), 1=组2(PWM2) */

#endif /* BSP_DETECT_ENABLED */
#endif /* __BSP_DETECT_H */
