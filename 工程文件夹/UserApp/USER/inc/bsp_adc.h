#ifndef __BSP_ADC_H
#define __BSP_ADC_H

#include "cw32l010.h"
#include "cw32l010_adc.h"
#include "cw32l010_gpio.h"

/* VBAT 电池电压采样: PB00 = ADC_IN7
 * 分压电路: 上/下电阻均为 10K (VBAT ---10K---[ADC引脚]---10K---GND)
 *   -> ADC 采样电压 = VBAT/2, 分压比 = 2 倍还原
 *   -> 引脚源阻抗 = 10K || 10K = 5KΩ
 *
 * [重要] 本机 VBAT 直接给 MCU 供电 (VDD = VBAT), 而 ADC 参考 = VDD,
 *        若按固定 3.3V 换算, raw 恒为满量程一半(2048), 与 VBAT 无关!
 *        故必须用内部 BGR 1.2V 反推真实 VDD 再折算:
 *          VDD(mV)  = 4095 x BGR_mV / raw_bgr
 *          VBAT(mV) = VDD x raw_vbat / 4095 x 2 = 2 x BGR_mV x raw_vbat / raw_bgr
 *        BGR_mV 为芯片出厂 trim 精确值 (mV)。
 * 12bit, 单次转换 + 均值滤波 */

#define VBAT_DIV_RATIO       2U          /* 分压比: 10K上/10K下 -> VBAT/2, 还原乘2 */
#define VBAT_AVG_NUM         8           /* 均值采样次数 (50ms 周期内采样) */
#define BGR_AVG_NUM          4           /* BGR 通道均值次数 */

void BSP_ADC_Init(void);
uint16_t BSP_ADC_ReadVbatMv(void);

/* 调试用: 最近一次均值后的 ADC 原始值 (0..4095) */
extern volatile uint16_t g_adc_raw;      /* VBAT 通道 (CH7) */
extern volatile uint16_t g_bgr_raw;      /* BGR1.2V 通道 (CH15) */
extern volatile uint16_t g_bgr_trim_mv;  /* BGR 出厂 trim 值 (mV) */

#endif /* __BSP_ADC_H */
