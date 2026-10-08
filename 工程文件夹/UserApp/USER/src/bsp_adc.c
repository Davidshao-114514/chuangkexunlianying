#include "bsp_adc.h"
#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

/*******************************************************************************
 * BSP_ADC - 电池电压采样实现 (单 BGR 反推, 免外部分压)
 *
 * 公式: VBAT = VDD = BGR_mV x 4095 / raw_bgr
 * 参考: 官方 adc_sqr_sw_vdd_Ts 例程 (BGR 反推 VDD) 与 PWR 省电例程
 ******************************************************************************/

volatile uint16_t g_adc_raw = 0;          /* 调试: BGR 通道原始均值 */
volatile uint16_t g_bgr_raw = 0;          /* 调试: BGR 通道原始均值 */
volatile uint16_t g_bgr_trim_mv = 1200;   /* BGR 出厂 trim 精确值 (mV) */

/**
 * @brief 单次 ADC 转换 (序列 0 通道)
 * @param ch 通道 (ADC_InputCHx / ADC_InputVref1P2 ...)
 */
static uint16_t ADC_ConvOnce(uint16_t ch)
{
    CW_ADC->SQRCFR_f.SQRCH0 = ch;
    ADC_SoftwareStartConvCmd(ENABLE);
    while (!(CW_ADC->ISR & ADC_ISR_EOC_Msk));
    ADC_ClearITPendingBit(ADC_IT_EOC);
    return ADC_GetConversionValue(0);
}

void BSP_ADC_Init(void)
{
    ADC_InitTypeDef adc = {0};

    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();
    __SYSCTRL_ADC_CLK_ENABLE();

    /* PB00 原分压输入已拆除, 引脚悬空; 保持模拟输入 (无电流, 最省电) */
    PB00_ANALOG_ENABLE();

    adc.ADC_ClkDiv                    = ADC_Clk_Div8;      /* ADCCLK = PCLK/8 = 6MHz */
    adc.ADC_ConvertMode               = ADC_ConvertMode_Once;
    adc.ADC_SQREns                    = ADC_SqrEns0to0;    /* 单通道 */
    adc.ADC_IN0.ADC_InputChannel      = ADC_InputVref1P2;  /* 默认 BGR 通道 */
    adc.ADC_IN0.ADC_SampTime          = ADC_SampTime390Clk;/* 390clk@6MHz=65us;
                                                             * BGR 内部通道要求采样 >=40us */
    ADC_Init(&adc);

    ADC_ClearITPendingAll();
    ADC_Enable();

    /* 读取 BGR 出厂 trim 精确值 (mV); BGR 模块保持关闭, 测量时临时开启 */
    g_bgr_trim_mv = *(volatile uint16_t *)0x001007D2;
}

/**
 * @brief 读取电池电压 (mV)
 * @note  VBAT = VDD = BGR_mV x 4095 / raw_bgr
 *        BGR 仅测量瞬间开启, 完毕立即关闭 (省电, 待机零额外功耗)
 */
uint16_t BSP_ADC_ReadVbatMv(void)
{
    uint32_t sum = 0;
    uint16_t raw_b;
    uint32_t bgr_mv;
    uint32_t mv;
    static uint16_t s_filt_mv = 0;          /* 一阶平滑输出 */
    uint8_t i;

    /* 开启内部 BGR 1.2V, 等待建立 (>30us 规格) */
    CW_ADC->CR_f.BGREN = 1;
    {
        volatile uint32_t k;
        for (k = 0; k < 2400U; k++);        /* ~50us @48MHz */
    }

    /* 丢弃 1 次 (通道建立) + 6 次均值 (65us 长采样充分) */
    (void)ADC_ConvOnce(ADC_InputVref1P2);
    for (i = 0U; i < 6U; i++)
        sum += ADC_ConvOnce(ADC_InputVref1P2);

    CW_ADC->CR_f.BGREN = 0;                 /* 关闭 BGR (省电) */

    raw_b = (uint16_t)(sum / 6U);
    g_adc_raw = raw_b;
    g_bgr_raw = raw_b;

    bgr_mv = g_bgr_trim_mv;                 /* 出厂精确值 (mV) */
    if ((bgr_mv == 0U) || (bgr_mv > 5000U))
        bgr_mv = 1200U;                     /* trim 异常按标称 1.2V */
    if (raw_b == 0U)
        return 0U;

    /* VBAT(=VDD) = BGR_mV x 4095 / raw_bgr */
    mv = (uint32_t)(((uint64_t)bgr_mv * 4095U) / raw_b);

    /* 一阶 IIR 平滑 (50ms 周期, 响应约 200ms) */
    if (s_filt_mv == 0U)
        s_filt_mv = (uint16_t)mv;
    else
        s_filt_mv = (uint16_t)(((uint32_t)s_filt_mv * 3U + mv) / 4U);

    return s_filt_mv;
}
