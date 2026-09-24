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
    adc.ADC_IN0.ADC_SampTime          = ADC_SampTime390Clk; /* 390clk@6MHz=65µs;
                                                             * 官方要求采 TS/BGR 内部通道采样至少 40µs
                                                             * (VBAT通道源阻抗 5KΩ 同样受益) */
    ADC_Init(&adc);

    ADC_ClearITPendingAll();
    ADC_Enable();

    /* 打开内部 BGR 1.2V (常开, 用于反推 VDD), 再等待 >100us 稳定 */
    CW_ADC->CR_f.BGREN = 1;
    {
        volatile uint32_t i;
        for (i = 0; i < 4800; i++);
    }

    /* 读取 BGR 出厂 trim 精确值 (mV) */
    g_bgr_trim_mv = *(volatile uint16_t *)0x001007D2;
}

volatile uint16_t g_adc_raw = 0;    /* 调试: VBAT 通道原始均值 (CH7) */
volatile uint16_t g_bgr_raw = 0;    /* 调试: BGR1.2V 通道原始均值 (CH15) */
volatile uint16_t g_bgr_trim_mv = 1200;   /* BGR 出厂 trim 精确值 (mV) */

/* BGR 1.2V 精确值存放地址 (芯片出厂 trim, 单位 mV; 官方例程同款) */
#define BGR_TRIM_MV_ADDR    ((volatile uint16_t *)0x001007D2)

/**
 * @brief 单通道多次转换取均值 (含丢弃前 2 次)
 * @param ch  输入通道 (ADC_InputCHx / ADC_InputVref1P2 ...)
 * @param n   均值次数
 * @return 原始均值 (0..4095)
 */
static uint16_t ADC_ReadAvg(uint16_t ch, uint8_t n)
{
    uint32_t sum = 0;
    uint8_t i;

    CW_ADC->SQRCFR_f.SQRCH0 = ch;

    for (i = 0; i < 2; i++)             /* 丢弃前 2 次 (建立) */
    {
        ADC_SoftwareStartConvCmd(ENABLE);
        while (!(CW_ADC->ISR & ADC_ISR_EOC_Msk));
        ADC_ClearITPendingBit(ADC_IT_EOC);
    }
    for (i = 0; i < n; i++)             /* 均值 */
    {
        ADC_SoftwareStartConvCmd(ENABLE);
        while (!(CW_ADC->ISR & ADC_ISR_EOC_Msk));
        ADC_ClearITPendingBit(ADC_IT_EOC);
        sum += ADC_GetConversionValue(0);
    }
    return (uint16_t)(sum / n);
}

/**
 * @brief 读取电池电压 (mV)
 * @note  VBAT 直供 MCU 时 VDD=VBAT, ADC 参考=VDD, 采用 BGR1.2V 反推:
 *          VBAT = 2 x BGR_mV x raw_vbat / raw_bgr
 * @return 电池电压 mV (分压比 2 还原后)
 */
uint16_t BSP_ADC_ReadVbatMv(void)
{
    uint16_t raw_v, raw_b;
    uint32_t bgr_mv;
    uint32_t mv;

    raw_v = ADC_ReadAvg(VBAT_ADC_CHANNEL, VBAT_AVG_NUM);    /* CH7: VBAT/2 (内含丢弃2次) */
    raw_b = ADC_ReadAvg(ADC_InputVref1P2, BGR_AVG_NUM);     /* CH15: 内部1.2V (长采样保证准确) */
    CW_ADC->SQRCFR_f.SQRCH0 = VBAT_ADC_CHANNEL;             /* 恢复正常通道 */

    g_adc_raw = raw_v;
    g_bgr_raw = raw_b;

    bgr_mv = g_bgr_trim_mv;                                 /* 出厂精确值 (mV) */
    if ((bgr_mv == 0U) || (bgr_mv > 5000U))
        bgr_mv = 1200U;                     /* trim 异常时按标称 1.2V */
    if (raw_b == 0U)
        return 0U;

    mv = (2U * bgr_mv * raw_v) / raw_b;     /* VBAT = 2 x BGR x rawV / rawB */
    return (uint16_t)mv;
}
