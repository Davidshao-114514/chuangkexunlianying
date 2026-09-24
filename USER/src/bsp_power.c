#include "bsp_power.h"
#include "bsp_pin.h"
#include "bsp_button.h"
#include "cw32l010_sysctrl.h"
#include "cw32l010_pwr.h"

/*******************************************************************************
 * BSP_POWER - 低功耗管理实现
 *
 * 参考: CW32L010 例程 PWR\PWR_ConsumptionTest
 *   - 停机模式: PWR_Config(SleepDeep 使能) + PWR_GotoLpmMode() (__WFI)
 *   - 唤醒: GPIO 下降沿中断 (按键按下, 内部上拉确保空闲为高)
 *   - 进入低功耗前除 GPIOA/GPIOB 外所有外设时钟关闭 (最低功耗)
 ******************************************************************************/

/**
 * @brief 进入停机模式 (STOP), 任意按键按下唤醒
 * @note 返回时即已唤醒, 调用后应尽快做唤醒处理
 */
void BSP_POWER_EnterStop(void)
{
    PWR_InitTypeDef pwr = {0};
    GPIO_InitTypeDef s  = {0};
    uint8_t i;

    /* ---- 1. 停用 1ms 时基中断 (BTIM 时钟即将关闭, 断开其 NVIC) ---- */
    NVIC_DisableIRQ(BTIM1_IRQn);

    /* ---- 2. 关闭全部外设时钟, 仅保留 GPIOA/GPIOB (GPIO 中断需用) ---- */
    CW_SYSCTRL->APBEN1 = 0x5A5A0000U;           /* APB1 外设全部断电 */
    CW_SYSCTRL->APBEN2 = 0x5A5A0000U;           /* APB2 外设全部断电 */
    CW_SYSCTRL->AHBEN  = 0x5A5A0000U;           /* AHB 外设全部断电 */
    __SYSCTRL_GPIOA_CLK_ENABLE();               /* 仅开 GPIOA */
    __SYSCTRL_GPIOB_CLK_ENABLE();               /* 仅开 GPIOB */

    /* ---- 3. 按键引脚重配为"下降沿中断 + 内部上拉" (按键低电平有效) ---- */
    s.IT   = GPIO_IT_FALLING;
    s.Mode = GPIO_MODE_INPUT_PULLUP;
    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        s.Pins = BTN_PIN[i];
        GPIO_Init((GPIO_TypeDef *)BTN_PORT[i], &s);
    }

    /* ---- 4. 清除旧的中断挂起位, 使能 GPIO 中断唤醒 ---- */
    GPIOA_INTFLAG_CLR(CW_GPIOA->ISR);
    GPIOB_INTFLAG_CLR(CW_GPIOB->ISR);
    NVIC_ClearPendingIRQ(GPIOA_IRQn);
    NVIC_ClearPendingIRQ(GPIOB_IRQn);
    NVIC_EnableIRQ(GPIOA_IRQn);
    NVIC_EnableIRQ(GPIOB_IRQn);

    /* ---- 5. 进入停机模式 (STOP: CPU/内核停止, GPIO 中断可唤醒) ---- */
    pwr.PWR_Sevonpend   = PWR_Sevonpend_Disable;
    pwr.PWR_SleepDeep   = PWR_SleepDeep_Enable;     /* 深度睡眠 -> STOP */
    pwr.PWR_SleepOnExit = PWR_SleepOnExit_Disable;
    PWR_Config(&pwr);
    PWR_GotoLpmMode();                              /* __WFI(), 唤醒后在此返回 */

    /* 唤醒后: 关闭唤醒用 GPIO 中断 (按键模式将由 BSP_BTNs_Init 恢复) */
    NVIC_DisableIRQ(GPIOA_IRQn);
    NVIC_DisableIRQ(GPIOB_IRQn);
    GPIOA_INTFLAG_CLR(CW_GPIOA->ISR);
    GPIOB_INTFLAG_CLR(CW_GPIOB->ISR);
}

/**
 * @brief 唤醒后恢复: 时钟/外设/按键扫描/时基中断
 * @note HSI 在 STOP 模式被关闭, 需重新使能; 各外设寄存器在 STOP 均保留,
 *       因此只需恢复时钟与中断, 无需重新初始化外设
 */
void BSP_POWER_WakeupInit(void)
{
    /* ---- 1. 时钟恢复: HSI 48MHz ---- */
    SYSCTRL_HSI_Enable(SYSCTRL_HSIOSC_DIV1);
    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();
    __SYSCTRL_ATIM_CLK_ENABLE();
    __SYSCTRL_ADC_CLK_ENABLE();
    __SYSCTRL_BTIM123_CLK_ENABLE();

    /* ---- 2. 按键回到正常扫描模式 (去抖扫描, 无中断) ---- */
    BSP_BTNs_Init();

    /* ---- 3. 恢复 1ms 时基中断 ---- */
    NVIC_ClearPendingIRQ(BTIM1_IRQn);
    NVIC_EnableIRQ(BTIM1_IRQn);
}
