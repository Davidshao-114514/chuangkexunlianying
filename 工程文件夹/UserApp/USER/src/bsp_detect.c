#include "bsp_detect.h"

/* 仅外挂款启用; 内置款整个模块编译为空 */
#if BSP_DETECT_ENABLED

#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

/*******************************************************************************
 * BSP_DETECT - 磁吸接口 LED 吸附检测实现
 *
 * 检测方法: 引脚空闲 (外部下拉) -> 低; LED 吸附后检测线被 3.3V 拉高 -> 高
 * 去抖:     状态采样放在 5ms 周期任务 (App_Task1ms 分频),
 *           连续 DETECT_HOLD_CNT 次一致才翻转, 防止磁吸瞬间抖动误判
 ******************************************************************************/

static volatile uint8_t  s_raw[2];      /* 前一次原始电平 (1=高/已吸附) */
static volatile uint8_t  s_stable[2];   /* 去抖后的稳定电平 */
static volatile uint16_t s_cnt[2];      /* 连续同值计数 */

/**
 * @brief 吸附检测引脚初始化
 * @note  GPIO 输入(无内部上/下拉), 板侧外接下拉电阻保证未吸附时电平为低
 *        未使用外部晶振, OSC+/OSC- (PA00/PA01) 可作普通 GPIO 输入
 */
void BSP_DETECT_Init(void)
{
    GPIO_InitTypeDef s = {0};

    __SYSCTRL_GPIOA_CLK_ENABLE();

    s.IT   = GPIO_IT_NONE;
    s.Mode = GPIO_MODE_INPUT;           /* 浮空输入 + 外部下拉 */
    s.Pins = DET1_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)DET1_GPIO_PORT, &s);
    s.Pins = DET2_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)DET2_GPIO_PORT, &s);

    s_raw[0]    = 0;
    s_raw[1]    = 0;
    s_stable[0] = 0;                    /* 上电默认未吸附 */
    s_stable[1] = 0;
    s_cnt[0]    = 0;
    s_cnt[1]    = 0;
}

/**
 * @brief 吸附检测周期任务 (每 5ms 调用一次, 由 App_Task1ms 调度)
 * @note  检测状态变化时由 App_Task1ms 检查并联动 PWM/界面
 */
void BSP_DETECT_Task(void)
{
    uint8_t i;
    uint8_t raw;

    static const GPIO_TypeDef *const det_port[2] = { DET1_GPIO_PORT, DET2_GPIO_PORT };
    static const uint16_t det_pin[2] = { DET1_GPIO_PINS, DET2_GPIO_PINS };

    for (i = 0; i < 2; i++)
    {
        raw = ((det_port[i]->IDR & det_pin[i]) != 0) ? 1 : 0;   /* 高=吸附 */

        if (raw == s_stable[i])
        {
            s_cnt[i] = 0;               /* 与稳定态一致 -> 清计数 */
        }
        else if (s_stable[i] != raw)
        {
            if (++s_cnt[i] >= DETECT_HOLD_CNT)   /* 连续一致达到去抖阈值 */
            {
                s_stable[i] = raw;      /* 确认翻转: 吸附/脱落 */
                s_cnt[i] = 0;
            }
        }
    }
}

/**
 * @brief 查询某灯组吸附状态
 * @param grp 0=组1 (PWM1/PB01), 1=组2 (PWM2/PA03)
 * @return 1=检测到高电平 (LED 已吸附), 0=未吸附
 */
uint8_t BSP_DETECT_IsAttached(uint8_t grp)
{
    if (grp == 0)
        return s_stable[0];
    else
        return s_stable[1];
}

#endif /* BSP_DETECT_ENABLED */
