#ifndef __BSP_ADC_H
#define __BSP_ADC_H

#include "cw32l010.h"
#include "cw32l010_adc.h"
#include "cw32l010_gpio.h"

/*******************************************************************************
 * BSP_ADC - 电池电压采样 (内部 BGR 1.2V 反推, 无需外部分压)
 *
 * [方案] MCU 由电池直接供电 => VDD = VBAT; ADC 参考 = VDD。
 *   采样内部 BGR1.2V 通道, 按比例反推供电电压:
 *       VBAT(mV) = VDD(mV) = BGR_mV x 4095 / raw_bgr
 *   BGR_mV 为芯片出厂 trim 精确值 (mV), 存于 0x001007D2。
 *
 * [省电] 外部 10K/10K 分压已拆除 (原静态耗电约 210uA @4.2V);
 *   BGR 也仅在测量瞬间开启 (测量完毕立即关闭), 待机零额外功耗。
 *   PB00 悬空, 保持模拟输入 (无电流)。
 *
 * [注意] 依赖 "电池直供 MCU" 的硬件前提; 若将来在电池与 VDD 之间增加
 *   稳压/二极管等, 测得的是 MCU 端电压而非电池端电压。
 ******************************************************************************/

void     BSP_ADC_Init(void);
uint16_t BSP_ADC_ReadVbatMv(void);          /* 电池电压 mV */

/* 调试用原始值 */
extern volatile uint16_t g_adc_raw;         /* 最近一次 BGR 通道原始均值 */
extern volatile uint16_t g_bgr_raw;         /* 同上 (保留别名) */
extern volatile uint16_t g_bgr_trim_mv;     /* BGR 出厂 trim 值 (mV) */

#endif /* __BSP_ADC_H */
