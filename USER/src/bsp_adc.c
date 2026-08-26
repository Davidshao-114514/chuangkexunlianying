#include "bsp_adc.h"
#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

void BSP_ADC_Init(void)
{
    ADC_InitTypeDef adc = {0};

    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();
    __SYSCTRL_ADC_CLK_ENABLE();

    /* PB00 模拟功能 */
    PB00_ANALOG_ENABLE();

    adc.ADC_ClkDiv                    = ADC_Clk_Div8;      /* ADCCLK = PCLK/8 = 6MHz (规格<=48MHz) */
    adc.ADC_ConvertMode               = ADC_ConvertMode_Once;
    adc.ADC_SQREns                    = ADC_SqrEns0to0;    /* 单通道 */
    adc.ADC_IN0.ADC_InputChannel      = VBAT_ADC_CHANNEL;  /* AIN7 */
    adc.ADC_IN0.ADC_SampTime          = ADC_SampTime42Clk;
    ADC_Init(&adc);

    ADC_ClearITPendingAll();
    ADC_Enable();
}

uint16_t BSP_ADC_ReadVbatMv(void)
{
    uint32_t sum = 0;
    uint8_t i;

    for (i = 0; i < VBAT_AVG_NUM; i++)
    {
        ADC_SoftwareStartConvCmd(ENABLE);
        while (!(CW_ADC->ISR & ADC_ISR_EOC_Msk));
        ADC_ClearITPendingBit(ADC_IT_EOC);
        sum += ADC_GetConversionValue(0);
    }
    sum = sum / VBAT_AVG_NUM;
    {
        uint32_t mv = (uint32_t)sum * VBAT_ADC_VREF_MV / 4095U;
        return (uint16_t)(mv * VBAT_DIV_RATIO);
    }
}
