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
 *   - 唤醒键 PB03: VBAT 分压常电供电, 高有效, 上升沿唤醒 (见 EnterStop)
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
    uint16_t i;

    /* ---- 1. 停用 1ms 时基中断 (BTIM 时钟即将关闭, 断开其 NVIC) ---- */
    NVIC_DisableIRQ(BTIM1_IRQn);

    /* ---- 2. 关闭全部外设时钟, 仅保留 GPIOA/GPIOB (GPIO 中断需用) ---- */
    CW_SYSCTRL->APBEN1 = 0x5A5A0000U;           /* APB1 外设全部断电 */
    CW_SYSCTRL->APBEN2 = 0x5A5A0000U;           /* APB2 外设全部断电 */
    CW_SYSCTRL->AHBEN  = 0x5A5A0000U;           /* AHB 外设全部断电 */
    __SYSCTRL_GPIOA_CLK_ENABLE();               /* 仅开 GPIOA */
    __SYSCTRL_GPIOB_CLK_ENABLE();               /* 仅开 GPIOB */
    __SYSCTRL_RTC_CLK_ENABLE();                 /* RTC 保持走时 (1h 恢复窗口) */

    /* ---- 3. 待机/唤醒按键配置 (硬件方案) ----
     * PB03(电源键) 由 VBAT 电阻分压常电供电 (不经 ME6211, 单片机电池直供),
     *   关机后仍有电 -> 保持与运行一致的"高电平有效":
     *   浮空输入(外部下拉, 空闲低) + 按下为高(上升沿唤醒);
     * PA04/PA05 不参与唤醒, 配内部上拉固定状态, 避免浮空耗电 */
    s.IT   = GPIO_IT_NONE;
    s.Mode = GPIO_MODE_INPUT_PULLUP;
    s.Pins = GPIO_PIN_4;
    GPIO_Init(CW_GPIOA, &s);                    /* PA04 */
    s.Pins = GPIO_PIN_5;
    GPIO_Init(CW_GPIOA, &s);                    /* PA05 */

    s.IT   = GPIO_IT_RISING;                    /* 上升沿 = 按下 (高有效) */
    s.Mode = GPIO_MODE_INPUT;                   /* 外部下拉, 空闲低 */
    s.Pins = GPIO_PIN_3;
    GPIO_Init(CW_GPIOB, &s);                    /* PB03 唤醒键 */

    /* ---- 4. 清除挂起, 使能 GPIOB 唤醒中断 (PB03 在 GPIOB) ---- */
    GPIOB_INTFLAG_CLR(CW_GPIOB->ISR);
    NVIC_ClearPendingIRQ(GPIOB_IRQn);
    NVIC_EnableIRQ(GPIOB_IRQn);

    /* ---- 5. 等待 PB03 释放 (松开后为低), 或 2s 超时 ----
     * 防止关机时手指仍按着/电平残余产生边沿, 导致立即假唤醒 */
    for (i = 0; i < 2000U; i++)
    {
        if ((CW_GPIOB->IDR & GPIO_PIN_3) == 0U)
            break;                              /* 已释放(低) */
        {
            volatile uint32_t k;
            for (k = 0; k < 48000U; k++);       /* 约 1ms */
        }
    }
    GPIOB_INTFLAG_CLR(CW_GPIOB->ISR);           /* 清等待期间的边沿 */

    /* ---- 6. 进入停机模式 (STOP: CPU/内核停止, GPIO 下降沿可唤醒) ---- */
    pwr.PWR_Sevonpend   = PWR_Sevonpend_Disable;
    pwr.PWR_SleepDeep   = PWR_SleepDeep_Enable;     /* 深度睡眠 -> STOP */
    pwr.PWR_SleepOnExit = PWR_SleepOnExit_Disable;
    PWR_Config(&pwr);
    PWR_GotoLpmMode();                              /* __WFI(), 唤醒后在此返回 */

    /* 唤醒后: 关闭唤醒中断并清标志 (按键模式由 BSP_BTNs_Init 恢复) */
    NVIC_DisableIRQ(GPIOB_IRQn);
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

    /* ---- 2. 恢复 1ms 时基中断 ----
     * 注意: 按键恢复不在此处调用! 唤醒后 LDO(3V3) 尚未重建,
     *       需由应用等 3V3 稳定后再调 BSP_BTNs_Init (见 main.c 唤醒恢复) */

    NVIC_ClearPendingIRQ(BTIM1_IRQn);
    NVIC_EnableIRQ(BTIM1_IRQn);
}
