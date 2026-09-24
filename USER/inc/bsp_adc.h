#ifndef __BSP_ADC_H
#define __BSP_ADC_H

#include "cw32l010.h"
#include "cw32l010_adc.h"
#include "cw32l010_gpio.h"

/* VBAT 电池电压采样: PB00 = ADC_IN7
 * ADC 参考电压为 VDD(3.3V), 12bit, 单次转换+均值滤波 */

#define VBAT_ADC_VREF_MV     3300U       /* ADC 参考电压 mV (VDD) */
#define VBAT_DIV_RATIO       2U          /* 电池->PB00 分压比 (1:1 时填 1) */
#define VBAT_AVG_NUM         8           /* 均值采样次数 (50ms 周期内采样) */

void BSP_ADC_Init(void);
uint16_t BSP_ADC_ReadVbatMv(void);

#endif /* __BSP_ADC_H */
