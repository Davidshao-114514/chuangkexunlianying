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

    s.IT   = GPIO_IT_NONE;
    s.Mode = GPIO_MODE_INPUT_PULLUP;
    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        s.Pins = BTN_PIN[i];
        GPIO_Init((GPIO_TypeDef *)BTN_PORT[i], &s);
        s_deb[i]    = 0;
        s_stable[i] = 0;
    }
    s_state = 0;
}

uint8_t BSP_BTNs_Scan(void)
{
    uint8_t i;
    uint8_t pressed = 0;
    uint8_t prev    = s_state;

    for (i = 0; i < BTN_MAX_NUM; i++)
    {
        uint8_t raw = ((BTN_PORT[i]->IDR & BTN_PIN[i]) == 0) ? 1 : 0;   /* 低=按下 */
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
