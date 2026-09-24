#include "../inc/main.h"

/*******************************************************************************
 * UserApp - CW32L010F8 应用框架
 *
 * 结构划分 (参考 H563 工程):
 *   - main.c          应用主程序: 初始化和界面刷新 (OLED 内容)
 *   - interrupts.c    BTIM1 1ms 定时中断: 周期任务调度
 *   - bsp_timer.c     BTIM1 定时器配置 (时基 1ms)
 *   - bsp_power.c     低功耗: 停机(STOP)休眠 + 按键唤醒
 *   - bsp_oled.c      OLED 显示原语 (ShowStr 等, 屏幕内容由 main.c 决定)
 *   - bsp_i2c.c       软件 I2C (OLED)
 *   - bsp_pwm.c       PWM (ATIM_CH2/CH3): 组1/组2 LED 输出
 *   - bsp_adc.c       VBAT 电压采样 (ADC_IN7)
 *   - bsp_button.c    按键扫描
 *   - bsp_detect.c    磁吸接口 LED 吸附检测 (复用 OSC+/OSC-)
 *
 * [硬件说明]
 *   - 无外部晶振: 内部高速时钟 HSI 48MHz
 *   - 4pin 磁吸接口 x2 (仅外挂款): 3V3 / GND / LED- / DET
 *     DET 检测线: 板/线侧下拉电阻, LED 端 3V3 接检测线
 *     -> 高电平 = LED 已吸附
 *   - 检测引脚: 组1 = PA01(OSC-), 组2 = PA00(OSC+)
 *
 * [软件开关 - 产品型号] 见 app_config.h (烧录前切换)
 *   外挂款: 磁吸检测启用, 按键 5 个 (PA02 PA04 PA05 PA06 PB03)
 *   内置款: 无检测, 按键 7 个 (PA00 PA01 PA02 PA04 PA05 PA06 PB03)
 *
 * [按键功能]
 *   外挂款 BTN1..BTN5 (=PA02 PA04 PA05 PA06 PB03):
 *     BTN1: 整机开关; BTN2/3: 当前组亮度-/+; BTN4: 分组切换; BTN5: 全部亮灭
 *   内置款 BTN1..BTN7 (=PA00 PA01 PA02 PA04 PA05 PA06 PB03):
 *     BTN1: 整机开关; BTN2/3: 当前组亮度-/+; BTN4: 分组切换;
 *     BTN5: 组1 亮灭; BTN6: 组2 亮灭; BTN7: 全部亮灭
 ******************************************************************************/

/* 断言上报接口: CW32 库 base_types.h 无条件开启 USE_FULL_ASSERT, 必须实现 */
#ifdef USE_FULL_ASSERT
/**
 * @brief 库函数参数校验失败时被调用 (assert_param 触发)
 * @param file 出错源文件
 * @param line 出错行号
 */
void assert_failed(uint8_t *file, uint32_t line)
{
    (void)file;
    (void)line;
    while (1);      /* 死循环等待调试 */
}
#endif /* USE_FULL_ASSERT */

/* ============================ 数据结构定义 ============================ */

/**
 * @brief 灯组状态
 * @note 组1 -> PWM1 (PB01, ATIM_CH2); 组2 -> PWM2 (PA03, ATIM_CH3)
 */
typedef struct
{
    uint8_t  on;            /* 点亮状态: 1=亮, 0=灭 */
    uint16_t brightness;    /* 亮度档位 (千分数 0..1000) */
} LEDGroup_t;

/* ============================ 应用状态变量 ============================ */
volatile uint16_t g_vbat_mv      = 0;     /* 电池电压 (mV), ISR 每50ms采样更新 */

volatile LEDGroup_t g_grp1       = {1, 500};  /* 组1: 亮, 50% 亮度 */
volatile LEDGroup_t g_grp2       = {1, 500};  /* 组2: 亮, 50% 亮度 */
volatile uint8_t    g_active_grp = 1;        /* 当前亮度调节组 (1/2) */
volatile uint8_t    g_power_on   = 1;        /* 整机开关 (LDO CE) */
volatile uint8_t    g_ui_req     = 0;        /* 界面刷新请求 (ISR置位) */
volatile uint8_t    g_sleep_req  = 0;        /* 关机: 请求进入停机休眠 */
volatile uint8_t    g_det1       = 0;        /* 组1 吸附状态缓存 (1=已连接; 内置款恒1) */
volatile uint8_t    g_det2       = 0;        /* 组2 吸附状态缓存 (1=已连接; 内置款恒1) */

/* 唤醒后 300ms 内吞掉按键事件 (避免"开机后立刻再次关机") */
static volatile uint32_t s_swallow_until = 0;

/* 周期任务调度计数 (ISR 内使用) */
static volatile uint32_t s_cnt_5ms   = 0;    /* 按键扫描 5ms 计时器 */
static volatile uint32_t s_cnt_50ms  = 0;    /* ADC 采样 50ms 计时器 */
static volatile uint32_t s_cnt_200ms = 0;    /* 界面刷新 200ms 计时器 */

/* ============================ 静态函数声明 ============================ */
static void Board_Init(void);
static void HandleKey(uint8_t evt);
static void ApplyOutputs(void);
static void UpdateDetect(void);
static void OLED_ShowVBat(uint8_t x, uint8_t y, uint16_t mv);
static void OLED_ShowPct(uint8_t x, uint8_t y, uint16_t permille);
static void OLED_ShowGroup(uint8_t x, uint8_t y, const LEDGroup_t *grp);
static void OLED_ShowDet(uint8_t x, uint8_t y, uint8_t attached);

/* ======================================================================
 * 输出刷新: 将 (整机电源 x 组点亮 x 亮度 x 吸附检测) 写入 PWM 寄存器
 * 任意状态改变后调用 (ISR/初始化均可, 仅寄存器写, 耗时极短)
 * 安全逻辑: LED 未吸附(检测为低)时该组禁止输出, 防止空载驱动
 * ==================================================================== */
static void ApplyOutputs(void)
{
    uint16_t d1, d2;

#if BSP_DETECT_ENABLED
    /* [外挂款] 组1: 需 电源 ON + 组1点亮 + 组1已吸附 */
    d1 = (g_power_on && g_grp1.on && g_det1) ? g_grp1.brightness : 0;
    /* 组2: 需 电源 ON + 组2点亮 + 组2已吸附 */
    d2 = (g_power_on && g_grp2.on && g_det2) ? g_grp2.brightness : 0;
#else
    /* [内置款] LED 内置, 无吸附检测 (g_det 恒为 1) */
    d1 = (g_power_on && g_grp1.on) ? g_grp1.brightness : 0;
    d2 = (g_power_on && g_grp2.on) ? g_grp2.brightness : 0;
#endif

    BSP_PWM_SetDuty(PWM_CH1, d1);       /* 组1 (PB01) */
    BSP_PWM_SetDuty(PWM_CH2, d2);       /* 组2 (PA03) */
}

/**
 * @brief 吸附检测更新: 读取检测状态, 变化时联动 PWM 输出
 * @note 由 App_Task1ms 的 5ms 节拍调用 (去抖在 bsp_detect.c)
 */
static void UpdateDetect(void)
{
#if BSP_DETECT_ENABLED
    uint8_t d1 = BSP_DETECT_IsAttached(0);      /* 组1 吸附状态 */
    uint8_t d2 = BSP_DETECT_IsAttached(1);      /* 组2 吸附状态 */

    if ((d1 != g_det1) || (d2 != g_det2))       /* 吸附/脱落事件 */
    {
        g_det1 = d1;
        g_det2 = d2;
        ApplyOutputs();                         /* 联动输出 (脱落即灭) */
        g_ui_req = 1;                           /* 刷新界面显示 */
    }
#else
    /* [内置款] 视为一直吸附 */
    g_det1 = 1;
    g_det2 = 1;
#endif
}

/* ======================================================================
 * 周期任务 (由 BTIM1 1ms 中断调用, 见 interrupts_cw32l010.c)
 *
 * 本函数内按分频计划调度各周期任务, "大部分工作"在中断中完成,
 * 主循环只做最慢的 OLED 刷屏 (刷新需要数 ms, 不适合放 ISR):
 *   - 5ms : 按键扫描 + 吸附检测 (去抖后联动输出)
 *   - 50ms: VBAT 电压采样 (ADC 均值)
 *   - 200ms: 请求界面数值刷新
 * ==================================================================== */
void App_Task1ms(void)
{
    uint8_t evt;

    g_ms_tick++;                        /* 系统毫秒时基 (bsp_timer.h 声明) */

    /* ---------- 5ms: 按键扫描 + 吸附检测 ---------- */
    if (++s_cnt_5ms >= 5)
    {
        s_cnt_5ms = 0;

        evt = BSP_BTNs_Scan();          /* 按键去抖扫描 (15ms 稳定) */
        if (evt)
            HandleKey(evt);             /* 按键功能 (开关机/亮度/分组) */

#if BSP_DETECT_ENABLED
        BSP_DETECT_Task();              /* [外挂款] 吸附检测采样 (100ms 去抖) */
        UpdateDetect();                 /* 状态联动 (脱落 -> 灭) */
#endif
    }

    /* ---------- 50ms: ADC 电压采样 ---------- */
    if (++s_cnt_50ms >= 50)
    {
        s_cnt_50ms = 0;
        g_vbat_mv = BSP_ADC_ReadVbatMv();
    }

    /* ---------- 200ms: 界面刷新请求 ---------- */
    if (++s_cnt_200ms >= 200)
    {
        s_cnt_200ms = 0;
        g_ui_req = 1;                   /* 主循环检测到后执行 UI_RefreshValues() */
    }
}

/* ======================================================================
 * 按键功能处理 (从 ISR 调用)
 *
 * BTN1: 开关机 (整机电源 = LDO CE + 停机休眠)
 * BTN2/BTN3: 当前组亮度 -10% / +10%
 * BTN4: 分组切换 (组1 <-> 组2)
 * BTN5: 全部 点亮/熄灭
 * ==================================================================== */
static void HandleKey(uint8_t evt)
{
    uint8_t  g;         /* 当前调节组索引 (0=组1, 1=组2) */
    uint16_t br;

    /* ---- 唤醒保护: 停机恢复后短时间内吞掉当前按键按下事件,
     *      避免"唤醒后立刻再次触关机/误操作"---- */
    if (g_ms_tick < s_swallow_until)
    {
        return;
    }

    /* ---- BTN1: 整机开关机 (LDO CE + 进入/退出停机休眠) ---- */
    if (evt & BTN1_MASK)
    {
        g_power_on = !g_power_on;
        if (g_power_on)
        {
            LDO_CE_Enable();                    /* CE 拉高, LDO 上电 */
            ApplyOutputs();
        }
        else
        {
            LDO_CE_Disable();                   /* CE 拉低, LDO 断电 */
            ApplyOutputs();                     /* PWM 输出归零 */
            OLED_OFF();                         /* 关屏 */
            g_sleep_req = 1;                    /* 主循环进入 STOP 休眠 */
        }
    }

    /* ---- BTN2/BTN3: 亮度-/+ (作用于当前组) ---- */
    if (evt & (BTN2_MASK | BTN3_MASK))
    {
        g  = (g_active_grp == 1) ? 0 : 1;   /* 映射组索引 */
        br = (g == 0) ? g_grp1.brightness : g_grp2.brightness;

        if (evt & BTN2_MASK)                /* 亮度- */
            br = (br >= 100) ? (br - 100) : 100;    /* 下限 10% (保持可调) */
        if (evt & BTN3_MASK)                /* 亮度+ */
            br = (br <= 900) ? (br + 100) : 1000;   /* 上限 100% */

        if (g == 0) g_grp1.brightness = br;
        else        g_grp2.brightness = br;
        g_ui_req = 1;
        ApplyOutputs();
    }

    /* ---- BTN4: 分组切换 (当前亮度调节的组) ---- */
    if (evt & BTN4_MASK)
    {
        g_active_grp = (g_active_grp == 1) ? 2 : 1;
    }

    /* ---- BTN5: 全部 点亮/熄灭 (同步两组 ----
     * 外挂款: BTN5 即"全部"; 内置款: BTN5/6 单独控制组1/组2, BTN7 全部 */
    if (evt & BTN5_MASK)
    {
#if BSP_DETECT_ENABLED
        g_grp1.on = !g_grp1.on;
        g_grp2.on = !g_grp2.on;
#else
        g_grp1.on = !g_grp1.on;
#endif
        ApplyOutputs();
    }
#if !BSP_DETECT_ENABLED
    if (evt & BTN6_MASK)                /* 内置款: 组2 单独亮灭 */
    {
        g_grp2.on = !g_grp2.on;
        ApplyOutputs();
    }
    if (evt & BTN7_MASK)                /* 内置款: 全部亮灭 */
    {
        g_grp1.on = !g_grp1.on;
        g_grp2.on = !g_grp2.on;
        ApplyOutputs();
    }
#endif
}

/* ======================================================================
 * 格式化辅助
 * ==================================================================== */

/**
 * @brief 显示电压值 格式 "xx.xxV"
 * @param x 起始列 0..127
 * @param y 起始页 0..7
 * @param mv 电压 (mV)
 */
static void OLED_ShowVBat(uint8_t x, uint8_t y, uint16_t mv)
{
    uint8_t b[8];
    uint8_t ip = (uint8_t)(mv / 1000);              /* 整数部分 */
    uint8_t fp = (uint8_t)((mv % 1000) / 10);       /* 小数部分(2位) */

    b[0] = (uint8_t)('0' + ip / 10 % 10);           /* 十位 */
    b[1] = (uint8_t)('0' + ip % 10);                /* 个位 */
    b[2] = '.';
    b[3] = (uint8_t)('0' + fp / 10);                /* 0.1V 位 */
    b[4] = (uint8_t)('0' + fp % 10);                /* 0.01V 位 */
    b[5] = 'V';
    b[6] = '\0';
    OLED_ShowStr(x, y, b, 1);
}

/**
 * @brief 显示占空比 格式 "xx%"
 * @param x 起始列 0..127
 * @param y 起始页 0..7
 * @param permille 千分数 0..1000
 */
static void OLED_ShowPct(uint8_t x, uint8_t y, uint16_t permille)
{
    uint8_t b[4];
    uint8_t p = (uint8_t)(permille / 10);           /* 千分 -> 百分 */

    b[0] = (uint8_t)('0' + p / 10 % 10);            /* 十位 */
    b[1] = (uint8_t)('0' + p % 10);                 /* 个位 */
    b[2] = '%';
    b[3] = '\0';
    OLED_ShowStr(x, y, b, 1);
}

/**
 * @brief 显示一组灯的状态 格式 "ON xx%"/"OFF"
 * @param x 起始列
 * @param y 起始页
 * @param grp 灯组状态指针
 */
static void OLED_ShowGroup(uint8_t x, uint8_t y, const LEDGroup_t *grp)
{
    if (grp->on)
        OLED_ShowPct(x, y, grp->brightness);
    else
        OLED_ShowStr(x, y, (uint8_t *)"OFF", 1);
}

/**
 * @brief 显示吸附检测状态 格式 "OK"/"NO"
 * @param x 起始列
 * @param y 起始页
 * @param attached 1=已吸附(高电平), 0=未吸附
 */
static void OLED_ShowDet(uint8_t x, uint8_t y, uint8_t attached)
{
    OLED_ShowStr(x, y, (uint8_t *)(attached ? "OK" : "NO"), 1);
}

/* ======================================================================
 * 界面层 (main.c 内, 内容布局参考 H563 的 OLED_Scan 函数风格)
 * ==================================================================== */

/**
 * @brief 画静态标签 (上电后调用一次)
 * 屏幕布局 (每行 6x8 字体, 21 字符):
 *   Row0: VBAT: xx.xxV   电池电压
 *   Row1: G1(PB1): nn%   组1 (磁吸接口1) 亮度
 *   Row2: G2(PA3): nn%   组2 (磁吸接口2) 亮度
 *   Row3: PWR:ON  CUR:1   整机电源 / 当前调节组
 *   Row4: DET1:OK DET2:NO 磁吸吸附检测 (高=已连接)
 *   Row5~7: 按键提示
 */
void UI_StaticInit(void)
{
    OLED_CLS();

    /* 数据区标签 */
    OLED_ShowStr(0, 0, (uint8_t *)"VBAT:", 1);
    OLED_ShowStr(0, 1, (uint8_t *)"G1(PB1):", 1);
    OLED_ShowStr(0, 2, (uint8_t *)"G2(PA3):", 1);
    OLED_ShowStr(0, 3, (uint8_t *)"PWR:", 1);
    OLED_ShowStr(60, 3, (uint8_t *)"CUR:", 1);

#if BSP_DETECT_ENABLED
    /* [外挂款] 吸附检测标签 */
    OLED_ShowStr(0, 4, (uint8_t *)"DET1:", 1);
    OLED_ShowStr(60, 4, (uint8_t *)"DET2:", 1);

    /* 按键提示 */
    OLED_ShowStr(0, 5, (uint8_t *)"1:PWR 2/3:BRT-/+", 1);
    OLED_ShowStr(0, 6, (uint8_t *)"4:GRP 5:ALL", 1);
    OLED_ShowStr(0, 7, (uint8_t *)"DET:Hi=LINK", 1);
#else
    /* [内置款] 显示型号标识 */
    OLED_ShowStr(0, 4, (uint8_t *)"BUILT-IN", 1);

    /* 按键提示 (7 键) */
    OLED_ShowStr(0, 5, (uint8_t *)"1:PWR 2/3:BRT-/+", 1);
    OLED_ShowStr(0, 6, (uint8_t *)"4:GRP 5:G1 6:G2", 1);
    OLED_ShowStr(0, 7, (uint8_t *)"7:ALL", 1);
#endif

    /* 画一遍动态数值, 避免首屏空白 */
    UI_RefreshValues();
}

/**
 * @brief 刷新数值区 (由主循环在 g_ui_req 置位时调用, 200ms 一次)
 * 只更新数值区域, 避免整屏重刷, 与 H563 OLED_Scan 思路一致
 */
void UI_RefreshValues(void)
{
    OLED_ShowVBat(30, 0, g_vbat_mv);                    /* Row0: 电压 */

    OLED_ShowGroup(60, 1, (const LEDGroup_t *)&g_grp1); /* Row1: 组1 亮度/OFF */
    OLED_ShowGroup(60, 2, (const LEDGroup_t *)&g_grp2); /* Row2: 组2 亮度/OFF */

    OLED_ShowStr(24, 3, (uint8_t *)(g_power_on ? "ON  " : "OFF "), 1);    /* PWR */
    OLED_ShowStr(84, 3, (uint8_t *)(g_active_grp == 1 ? "1  " : "2  "), 1); /* CUR */

#if BSP_DETECT_ENABLED
    OLED_ShowDet(30, 4, g_det1);                        /* Row4: 组1 吸附检测 */
    OLED_ShowDet(90, 4, g_det2);                        /* Row4: 组2 吸附检测 */
#endif
}

/* ======================================================================
 * 初始化
 * ==================================================================== */

/**
 * @brief 板上外设初始化
 */
static void Board_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    /* ---- 时钟: 内部高速时钟 HSI 48MHz (PCLK = 48MHz, 无外部晶振) ---- */
    SYSCTRL_HSI_Enable(SYSCTRL_HSIOSC_DIV1);
    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();

    /* ---- CE: LDO 使能 (PB04, 上电默认使能) ---- */
    gpio.IT   = GPIO_IT_NONE;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pins = CE_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)CE_GPIO_PORT, &gpio);
    LDO_CE_Enable();
    g_power_on = 1;

    /* ---- 外设 ---- */
    I2C_GPIO_Init();                    /* 软件 I2C (OLED) */
    BSP_PWM_Init();                     /* PWM1/2 (组1/组2 LED) */
    BSP_ADC_Init();                     /* VBAT 采样 */
    BSP_BTNs_Init();                    /* 按键 */
#if BSP_DETECT_ENABLED
    BSP_DETECT_Init();                  /* [外挂款] 磁吸吸附检测 (OSC+/OSC-) */
#endif

    /* ---- OLED ---- */
    OLED_Init();

    /* ---- 定时器: BTIM1 1ms 时基 + 中断 ---- */
    __disable_irq();
    BSP_TIMER_Init();
    NVIC_SetPriority(BTIM1_IRQn, 1);    /* 优先级高于主循环, 低于系统调用 */
    NVIC_EnableIRQ(BTIM1_IRQn);
    __enable_irq();

    /* ---- 按当前状态输出 PWM (组默认亮, 50%; 外挂款未吸附的组不输出) ---- */
#if BSP_DETECT_ENABLED
    g_det1 = BSP_DETECT_IsAttached(0);  /* 读取初始吸附状态 */
    g_det2 = BSP_DETECT_IsAttached(1);
#else
    g_det1 = 1;                         /* 内置款: 视为已连接 */
    g_det2 = 1;
#endif
    ApplyOutputs();
}

/* ======================================================================
 * 主循环
 * ==================================================================== */

int main(void)
{
    Board_Init();                       /* 板上初始化 */

    UI_StaticInit();                    /* 画静态界面 */

    while (1)
    {
        /* ---------- 关机: 进入停机模式 (STOP) 休眠 ----------
         * 流程: 已关 LDO + PWM 归零 + 关屏, 此处进入低功耗;
         *       任意按键按下 -> GPIO 下降沿中断唤醒 -> WFI 返回后继续执行 */
        if (g_sleep_req)
        {
            g_sleep_req = 0;

            BSP_POWER_EnterStop();          /* 休眠, 唤醒后返回 */

            /* ============ 唤醒恢复 (按键按下) ============ */
            BSP_POWER_WakeupInit();         /* 恢复时钟/外设/按键扫描 */
#if BSP_DETECT_ENABLED
            BSP_DETECT_Init();              /* [外挂款] 重新初始化吸附检测 */
#endif

            s_swallow_until = g_ms_tick + 300;  /* 300ms 内吞掉唤醒按键事件 */
            g_power_on = 1;
            LDO_CE_Enable();                /* CE 拉高, LDO 上电 */
            OLED_ON();                      /* 开屏 */
            UpdateDetect();                 /* 刷新吸附状态并联动输出 */
            g_ui_req = 1;                   /* 刷一次界面 */
        }

        /* ---------- 界面刷新 (200ms 由 ISR 请求) ----------
         * OLED 写入耗时较长, 放主循环中执行, 避免阻塞 1ms 时基中断 */
        if (g_ui_req)
        {
            g_ui_req = 0;
            UI_RefreshValues();
        }
    }
}
