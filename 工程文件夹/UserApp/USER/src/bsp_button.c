#include "bsp_button.h"
#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

static uint8_t s_deb[BTN_MAX_NUM];      /* 去抖计数器 */
static uint8_t s_stable[BTN_MAX_NUM];   /* 稳定电平 (1=按下) */
static uint8_t s_state;                 /* 当前全部按下掩码 */

void BSP_BTNs_Init(void)
{
    GPIO_InitTypeDef s = {0};
    uint8_t i;

    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();

    s.IT = GPIO_IT_NONE;
#if BTN_ACTIVE_LEVEL          /* 按下为高: 浮空输入 + 外部下拉 */
    s.Mode = GPIO_MODE_INPUT;
#else                         /* 按下为低: 内部上拉 */
    s.Mode = GPIO_MODE_INPUT_PULLUP;
#endif
    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        s.Pins = BTN_PIN[i];
        GPIO_Init((GPIO_TypeDef *)BTN_PORT[i], &s);
        s_deb[i] = 0;
        /* 关键: 以当前实际电平作为初始稳定态
         * 防止"上电时已按下的键(卡键/接线异常)"被误判为新按下事件
         * (曾导致 PB03=开关机键时一上电即触发关机断电) */
#if BTN_ACTIVE_LEVEL
        s_stable[i] = ((BTN_PORT[i]->IDR & BTN_PIN[i]) != 0) ? 1 : 0;
#else
        s_stable[i] = ((BTN_PORT[i]->IDR & BTN_PIN[i]) == 0) ? 1 : 0;
#endif
    }

    s_state = 0;
    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        if (s_stable[i])
            s_state |= (1U << i);
    }
}

uint8_t BSP_BTNs_Scan(void)
{
    uint8_t i;
    uint8_t pressed = 0;
    uint8_t prev    = s_state;

    for (i = 0; i < BTN_MAX_NUM; i++)
    {
#if BTN_ACTIVE_LEVEL
        uint8_t raw = ((BTN_PORT[i]->IDR & BTN_PIN[i]) != 0) ? 1 : 0;   /* 高=按下 */
#else
        uint8_t raw = ((BTN_PORT[i]->IDR & BTN_PIN[i]) == 0) ? 1 : 0;   /* 低=按下 */
#endif
        if (raw != s_stable[i])
        {
            if (++s_deb[i] >= BTN_DEBOUNCE_COUNT)
            {
                s_stable[i] = raw;
                s_deb[i]    = 0;
            }
        }
        else
        {
            s_deb[i] = 0;
        }
    }

    s_state = 0;
    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        if (s_stable[i])
            s_state |= (1U << i);
    }

    pressed = s_state & ~prev;      /* 此次新按下的键 */
    return pressed;
}

uint8_t BSP_BTNs_GetState(void)
{
    return s_state;
}
