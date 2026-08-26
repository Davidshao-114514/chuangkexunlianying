#include "bsp_pwm.h"
#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

void BSP_PWM_SetDuty(uint8_t ch, uint16_t permille)
{
    uint16_t cmp = (uint16_t)((uint32_t)PWM_MAX_DUTY * permille / 1000);
    if (cmp > PWM_MAX_DUTY - 1)
        cmp = PWM_MAX_DUTY - 1;
    switch (ch)
    {
    case PWM_CH1:   ATIM_SetCompare2(cmp);  break;
    case PWM_CH2:   ATIM_SetCompare3(cmp);  break;
    default:                                 break;
    }
}

void BSP_PWM_Init(void)
{
    ATIM_InitTypeDef    atim = {DISABLE, 0};
    ATIM_OCInitTypeDef  oc   = {DISABLE, 0};
    GPIO_InitTypeDef    gpio = {0};

    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();
    __SYSCTRL_ATIM_CLK_ENABLE();

    /* ---- PWM1: PB01 = ATIM_CH2 ---- */
    PB01_AFx_ATIMCH2();
    gpio.IT   = GPIO_IT_NONE;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pins = PWM1_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)PWM1_GPIO_PORT, &gpio);

    /* ---- PWM2: PA03 = ATIM_CH3 ---- */
    PA03_AFx_ATIMCH3();
    gpio.Pins = PWM2_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)PWM2_GPIO_PORT, &gpio);

    /* ---- ATIM 基本配置 ---- */
    atim.BufferState         = DISABLE;                  /* ARR 无缓冲 */
    atim.CounterAlignedMode  = ATIM_COUNT_ALIGN_MODE_EDGE;   /* 边沿对齐, PWM 频率=countclk/(ARR+1) */
    atim.CounterDirection    = ATIM_COUNTING_UP;
    atim.CounterOPMode       = ATIM_OP_MODE_REPETITIVE;
    atim.Prescaler           = PWM_PRESCALER;
    atim.ReloadValue         = PWM_ARR;
    atim.RepetitionCounter   = 0;
    ATIM_Init(&atim);

    /* ---- 输出比较 PWM1 / PWM2 ---- */
    oc.BufferState       = DISABLE;
    oc.OCComplement      = DISABLE;                      /* 非互补输出 */
    oc.OCFastMode        = DISABLE;
    oc.OCInterruptState  = DISABLE;
    oc.OCMode            = ATIM_OCMODE_PWM1;
    oc.OCPolarity        = ATIM_OCPOLARITY_NONINVERT;
    oc.OCNPolarity       = ATIM_OCPOLARITY_NONINVERT;

    /* CH1 必须初始化(作为输出比较基准) */
    ATIM_OC1Init(&oc);
    ATIM_OC2Init(&oc);
    ATIM_OC3Init(&oc);

    ATIM_CH2Config(ENABLE);     /* 使能 CH2 输出 (PB01) */
    ATIM_CH3Config(ENABLE);     /* 使能 CH3 输出 (PA03) */

    ATIM_SetCompare1(0);
    ATIM_SetCompare2(0);
    ATIM_SetCompare3(0);

    BSP_PWM_Start();
}

void BSP_PWM_Start(void)
{
    ATIM_CtrlPWMOutputs(ENABLE);    /* MOE 打开 */
    ATIM_Cmd(ENABLE);
}

void BSP_PWM_Stop(void)
{
    ATIM_Cmd(DISABLE);
    ATIM_CtrlPWMOutputs(DISABLE);
}
