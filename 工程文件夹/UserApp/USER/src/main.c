#include "../inc/main.h"

/*******************************************************************************
 * UserApp - CW32L010F8 应用框架 (0.91" 128x32 OLED)
 *
 * 结构划分 (参考 H563 工程):
 *   - main.c          应用主程序: 初始化和界面刷新 (OLED 内容)
 *   - interrupts.c    BTIM1 1ms 定时中断: 周期任务调度
 *   - bsp_timer.c     BTIM1 定时器配置 (时基 1ms)
 *   - bsp_power.c     低功耗: 停机(STOP)休眠 + 按键唤醒
 *   - bsp_oled.c      OLED 显示原语 (6x8 ShowStr, 屏幕内容由 main.c 决定)
 *   - bsp_i2c.c       软件 I2C (OLED)
 *   - bsp_pwm.c       PWM (ATIM_CH2/CH3): 组1/组2 LED 输出
 *   - bsp_adc.c       VBAT 电压采样 (ADC_IN7, 10K/10K 分压)
 *   - bsp_button.c    按键扫描
 *   - bsp_detect.c    磁吸接口 LED 吸附检测 (复用 OSC+/OSC-)
 *
 * [硬件说明]
 *   - 无外部晶振: 内部高速时钟 HSI 48MHz
 *   - 0.91" OLED: SSD1306 128x32 (4 页, 每页 6x8 字体)
 *   - 4pin 磁吸接口 x2 (仅外挂款): 3V3 / GND / LED- / DET
 *     DET 检测线: 板侧/线侧下拉电阻, LED 端 3V3 接检测线
 *     -> 高电平 = LED 已吸附; 组1 = PA01(OSC-), 组2 = PA00(OSC+)
 *
 * [软件开关 - 产品型号] 见 app_config.h (烧录前切换)
 *   外挂款: 磁吸检测启用, 按键 5 个 (PA02 PA04 PA05 PA06 PB03)
 *   内置款: 无检测, 按键 7 个 (PA00 PA01 PA02 PA04 PA05 PA06 PB03)
 *
 * [按键功能] 仅 3 个按键:
 *   BTN1 (PB03): 开关机
 *   BTN2 (PA04): 亮度- (两组同步)
 *   BTN3 (PA05): 亮度+ (两组同步)
 *   电池非正常(LOW/PROTECT)时: BTN1 仍为开关机, 其余键切换告警页开关
 *   按键有效电平: 见 bsp_pin.h 的 BTN_ACTIVE_LEVEL (当前=按下为高)
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

/* ============================ 电池保护阈值 ============================ */
#define BAT_LOW_MV         3350U   /* 电压 < 3350mV: 电量低提醒 (提高电池容量使用度) */
#define BAT_WARN_RECOVER_MV 3400U  /* 回升到 3400mV: 解除低电提醒 (滞回 +50mV) */
#define BAT_CUT_MV         3200U   /* 电压 < 3200mV: 过放保护, 关断输出 */
#define BAT_CUT_RECOVER_MV 3350U   /* 回升到 3350mV: 恢复输出 (滞回 +150mV) */
#define BAT_CHK_HOLD       40      /* 状态切换需连续 40 次采样 (50ms x 40 = 2s) */

/* 电池状态机 */
#define BAT_STATE_OK       0       /* 正常 */
#define BAT_STATE_LOW      1       /* 低电量 (3.5V~3.2V): 提醒 */
#define BAT_STATE_PROTECT  2       /* 过放保护 (<3.2V): 输出关断 */

/* 无级调光参数 (按住亮度键连续平滑调节) */
#define DIM_STEP            5U      /* 每步变化 5‰ (0.5%) */
/* 长按加速手感 (三段): 起步慢速精细 -> 按住一会转中速 -> 再转快速 */
#define DIM_SPD1_INT        60U     /* 初期:   每 60ms 一步 (精细) */
#define DIM_SPD2_AT         1100U   /* 按下后 1.1s: 进入中速 */
#define DIM_SPD2_INT        30U     /* 中速:   每 30ms 一步 */
#define DIM_SPD3_AT         1900U   /* 按下后 1.9s: 进入快速 */
#define DIM_SPD3_INT        12U     /* 快速:   每 12ms 一步 */
#define DIM_MIN_PERMILLE    0U      /* 可调下限: 已开放到 0 (0=熄灭);
                                     * 若低占空比频闪可改回 30 (3%) 实现下限钳位 */
#define DIM_LONG_MS         300U    /* 长按判定: 超过则进入连续调节 */
#define DIM_DBL_MS          350U    /* 双击间隔窗口 */

/* 告警页显示策略 (省电: 告警屏耗电较大) */
#define ALERT_AUTO_CLOSE_MS 60000U /* 告警页无操作 1 分钟自动关屏 */

/* ============================ 应用状态变量 ============================ */
volatile uint16_t g_vbat_mv       = 0;     /* 电池电压 (mV), ISR 每50ms采样更新 */

volatile LEDGroup_t g_grp1        = {1, 100};   /* 组1: 亮, 10% 亮度 (开机防太亮) */
volatile LEDGroup_t g_grp2        = {1, 100};   /* 组2: 亮, 10% 亮度 (开机防太亮) */
volatile uint8_t    g_power_on    = 1;          /* 整机开关 (LDO CE) */
volatile uint8_t    g_ui_req      = 0;          /* 界面刷新请求 (ISR置位, 主循环清零) */
volatile uint8_t    g_sleep_req   = 0;          /* 关机: 请求进入停机休眠 (主循环执行) */
volatile uint8_t    g_det1        = 0;          /* 组1 吸附状态缓存 (1=已连接) */
volatile uint8_t    g_det2        = 0;          /* 组2 吸附状态缓存 (1=已连接; 内置款恒1) */

/* 双击 BTN2 切换: 亮度调节对象  0=A串(组1) 1=B串(组2) 2=一起 */
static volatile uint8_t s_dim_target = 2U;
/* 双击 BTN3 切换: 点亮模式      0=只A亮 1=只B亮 2=一起亮 */
static volatile uint8_t s_light_mode = 2U;

volatile uint8_t    g_bat_state   = BAT_STATE_OK;  /* 电池状态机 (0=OK 1=LOW 2=PROTECT) */
volatile uint8_t    g_ui_redraw   = 0;        /* 整屏重绘请求 (状态页切换) */
static volatile uint16_t s_bat_cnt = 0;       /* 状态切换连续采样计数 */

/* 告警页/显示控制 (省电) */
volatile uint8_t    g_alert_view  = 0;        /* 1=告警页显示中, 0=已关屏 */
volatile uint32_t   g_alert_timer = 0;        /* 告警页无操作倒计时 (ms) */
volatile uint8_t    g_disp_on     = 1;        /* 物理显示开关状态 */
volatile uint8_t    g_disp_change = 0;        /* 显示开关变更请求 (主循环执行) */

/* 唤醒后 300ms 内吞掉按键事件 (避免"开机后立刻再次关机") */
static volatile uint32_t s_swallow_until = 0;

/* 亮度变更 -> 延时自动保存 (解决"直接按 Reset 不经过关机流程"的丢失问题) */
static volatile uint8_t  s_save_dirty = 0;   /* 1=亮度有变更待保存 */
static volatile uint32_t s_save_tick  = 0;   /* 最后一次变更的时刻 */
#define SAVE_DELAY_MS   2000U                /* 变更后 2s 无操作即写入 Flash */

/* 唤醒后延时屏幕恢复: 经过指定数量的 1ms 中断后再初始化/刷屏
 * (关机期间 OLED 掉电, 需等供电稳定; 避免唤醒瞬间刷屏产生随机亮点) */
static volatile uint32_t s_wake_resume_at = 0;   /* 0=无待处理; 非0=恢复时刻(g_ms_tick) */
#define WAKE_RESUME_TICKS   500U                 /* 500 个 1ms 中断后恢复屏幕 */

/* 周期任务调度计数 (ISR 内使用) */
static volatile uint32_t s_cnt_5ms   = 0;     /* 按键扫描 5ms 计时器 */
static volatile uint32_t s_cnt_50ms  = 0;     /* ADC 采样 50ms 计时器 */
static volatile uint32_t s_cnt_200ms = 0;     /* 界面刷新 200ms 计时器 */

/* ============================ 静态函数声明 ============================ */
static void Board_Init(void);
static void HandleKey(uint8_t evt);
static void ApplyOutputs(void);
static void UpdateDetect(void);
static void Battery_Check(void);

/* ======================================================================
 * 输出刷新: 将 (整机电源 x 组点亮 x 亮度 x 吸附检测 x 未过放) 写入 PWM
 * 任意状态改变后调用 (ISR/初始化均可, 仅寄存器写, 耗时极短)
 * ==================================================================== */
static void ApplyOutputs(void)
{
    uint16_t d1, d2;
    uint8_t  ok = (g_bat_state != BAT_STATE_PROTECT);   /* 过放保护时禁止输出 */

#if BSP_DETECT_ENABLED
    /* [外挂款] 组输出需同时满足: 未过放 + 电源ON + 组点亮 + 已吸附 */
    d1 = (ok && g_power_on && g_grp1.on && g_det1) ? g_grp1.brightness : 0;
    d2 = (ok && g_power_on && g_grp2.on && g_det2) ? g_grp2.brightness : 0;
#else
    /* [内置款] 无吸附检测 (g_det 恒为 1) */
    d1 = (ok && g_power_on && g_grp1.on) ? g_grp1.brightness : 0;
    d2 = (ok && g_power_on && g_grp2.on) ? g_grp2.brightness : 0;
#endif

    BSP_PWM_SetDuty(PWM_CH1, d1);       /* 组1 (PB01) */
    BSP_PWM_SetDuty(PWM_CH2, d2);       /* 组2 (PA03) */
}

/* ======================================================================
 * BTN2/BTN3 多功能调光辅助 (单击微调 / 长按连续 / 双击切换)
 * ==================================================================== */

/**
 * @brief 对单个灯组做一步亮度调节 (含 3% 下限与 0 熄灭跳变规则)
 * @param g   目标灯组
 * @param dir >0 加一步, <0 减一步
 */
static void Dim_AdjustGroup(volatile LEDGroup_t *g, int8_t dir)
{
    uint16_t br = g->brightness;

    if (dir > 0)                                    /* 亮度+ */
    {
        if (br == 0U)
            /* 从熄灭起步: 有下限时直接到下限额, 无下限时到最小一档 */
            br = (DIM_MIN_PERMILLE != 0U) ? DIM_MIN_PERMILLE : DIM_STEP;
        else
            br = (br <= (1000U - DIM_STEP)) ? (br + DIM_STEP) : 1000U;
    }
    else                                            /* 亮度- */
    {
        if (br > DIM_MIN_PERMILLE)
            br = (br - DIM_STEP >= DIM_MIN_PERMILLE)
               ? (br - DIM_STEP) : DIM_MIN_PERMILLE;
        else
            br = 0U;                                /* 到下限再减 -> 熄灭(0) */
    }
    g->brightness = br;
}

/**
 * @brief 按当前调节对象 (A/B/AB) 调整亮度并联动输出
 */
static void Dim_Adjust(uint8_t idx, int8_t dir)
{
    (void)idx;

    if (s_dim_target != 1U)                         /* 目标含 A串(组1) */
        Dim_AdjustGroup((volatile LEDGroup_t *)&g_grp1, dir);
    if (s_dim_target != 0U)                         /* 目标含 B串(组2) */
        Dim_AdjustGroup((volatile LEDGroup_t *)&g_grp2, dir);

    ApplyOutputs();
    g_ui_req = 1;
    s_save_dirty = 1;
    s_save_tick  = g_ms_tick;
}

/**
 * @brief 双击 BTN2: 依次切换调节对象 A串 -> B串 -> 一起
 */
static void Dim_SwitchAdjustTarget(void)
{
    s_dim_target = (uint8_t)((s_dim_target + 1U) % 3U);
    g_ui_req = 1;
}

/**
 * @brief 双击 BTN3: 依次切换点亮模式 A亮 -> B亮 -> 一起亮
 */
static void Dim_SwitchLightMode(void)
{
    s_light_mode = (uint8_t)((s_light_mode + 1U) % 3U);

    g_grp1.on = (s_light_mode != 1U) ? 1U : 0U;     /* 0=A亮, 2=AB -> 组1亮 */
    g_grp2.on = (s_light_mode != 0U) ? 1U : 0U;     /* 1=B亮, 2=AB -> 组2亮 */

    ApplyOutputs();
    g_ui_req = 1;
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

/**
 * @brief 电池过放保护状态机 (由 50ms 采样刷新后调用)
 *
 * 状态迁移 (带 2s 连续确认 + 滞回, 防抖/防振荡):
 *   OK     -- 见 <3350mV 持续 2s --> LOW    (低电提醒, 输出不关)
 *   LOW    -- 回 >3400mV 持续 2s --> OK     (滞回 +50mV)
 *   LOW    -- 见 <3200mV 持续 2s --> PROTECT (关断输出 + OLED 告警)
 *   PROTECT-- 回 >3350mV 持续 2s --> OK (自动恢复输出; 滞回 +150mV)
 */
static void Battery_Check(void)
{
    uint8_t  ns = g_bat_state;
    uint8_t  ok;

    /* ---- 根据当前状态判定目标状态 ---- */
    switch (g_bat_state)
    {
    case BAT_STATE_OK:
        if (g_vbat_mv < BAT_LOW_MV)          ns = BAT_STATE_LOW;
        break;
    case BAT_STATE_LOW:
        if (g_vbat_mv > BAT_WARN_RECOVER_MV) ns = BAT_STATE_OK;        /* 回升 */
        else if (g_vbat_mv < BAT_CUT_MV)     ns = BAT_STATE_PROTECT;   /* 继续下跌 */
        break;
    case BAT_STATE_PROTECT:
        if (g_vbat_mv > BAT_CUT_RECOVER_MV)  ns = BAT_STATE_OK;        /* 回升恢复 */
        break;
    default:
        ns = BAT_STATE_OK;
        break;
    }

    /* ---- 连续确认: 目标态与当前态一致才切换 ---- */
    ok = (ns == g_bat_state);
    if (ok)
        s_bat_cnt = 0;
    else
    {
        if (++s_bat_cnt >= BAT_CHK_HOLD)
        {
            s_bat_cnt = 0;
            g_bat_state = ns;

            ApplyOutputs();             /* PROTECT 进入/退出 -> 立即关断/恢复 */

            /* 状态切换 -> 显示控制 */
            if (ns == BAT_STATE_OK)
            {
                /* 恢复 OK: 若之前告警屏被关闭, 强制点亮并回正常页 */
                g_alert_view   = 0;
                g_alert_timer  = 0;
                g_disp_on      = 1;
                g_disp_change  = 1;
            }
            else
            {
                /* 进入告警页: 点亮显示, 启动 1 分钟无操作自动关屏 */
                g_alert_view   = 1;
                g_alert_timer  = ALERT_AUTO_CLOSE_MS;
                g_disp_on      = 1;
                g_disp_change  = 1;
            }
            g_ui_redraw = 1;            /* 切换告警页/正常页 */
        }
    }
}

/* ======================================================================
 * 周期任务 (由 BTIM1 1ms 中断调用, 见 interrupts_cw32l010.c)
 *
 * 本函数内按分频计划调度各周期任务, "大部分工作"在中断中完成,
 * 主循环只做最慢的 OLED 刷屏 (刷新需要数 ms, 不适合放 ISR):
 *   - 1ms : 系统时基 / 告警页无操作自动关屏倒计时
 *   - 5ms : 按键扫描 + 吸附检测 (去抖后联动输出)
 *   - 50ms: VBAT 电压采样 + 电池保护状态机
 *   - 200ms: 请求界面数值刷新
 * ==================================================================== */
void App_Task1ms(void)
{
    uint8_t evt;

    g_ms_tick++;                        /* 系统毫秒时基 (bsp_timer.h 声明) */

    /* ---------- 告警页无操作自动关屏 (省电防过放) ---------- */
    if (g_alert_view && g_alert_timer)
    {
        if (--g_alert_timer == 0)
        {
            g_alert_view  = 0;
            g_disp_on     = 0;          /* 1 分钟无操作: 关闭 OLED */
            g_disp_change = 1;
        }
    }

    /* ---------- 5ms: 按键扫描 + 吸附检测 ---------- */
    if (++s_cnt_5ms >= 5)
    {
        s_cnt_5ms = 0;

        evt = BSP_BTNs_Scan();          /* 按键去抖扫描 (15ms 稳定) */
        if (evt)
            HandleKey(evt);             /* 按键功能 (开关机等) */

        /* ---------- BTN2/BTN3 多功能调光键 ----------
         *  单击 (<300ms): 亮度一步调节 (DIM_STEP)
         *  长按 (>=300ms): 连续平滑调节 (每 20ms 一步)
         *  双击 (两击间隔 <=350ms):
         *    BTN2(-): 依次切换调节对象  A串 -> B串 -> 一起
         *    BTN3(+): 依次切换点亮模式  A亮 -> B亮 -> 一起亮 */
        {
            typedef struct
            {
                uint8_t  pressed;       /* 当前按住 */
                uint8_t  long_fired;    /* 本次按压已进入长按连续调节 */
                uint8_t  click_wait;    /* 短按后等待第二击 */
                uint32_t press_tick;    /* 按下时刻 */
                uint32_t click_tick;    /* 上次短按释放时刻 */
            } DimKey_t;
            static DimKey_t s_k[2];                     /* 0=BTN2, 1=BTN3 */
            static uint32_t s_dim_tick = 0;
            uint8_t held, idx;

            if ((g_bat_state == BAT_STATE_OK) && (g_ms_tick >= s_swallow_until))
            {
                held = BSP_BTNs_GetState();

                for (idx = 0U; idx < 2U; idx++)
                {
                    uint8_t   mask = (idx == 0U) ? BTN2_MASK : BTN3_MASK;
                    DimKey_t *k    = &s_k[idx];

                    if (held & mask)                    /* ---- 按住 ---- */
                    {
                        if (!k->pressed)
                        {
                            k->pressed    = 1U;
                            k->long_fired = 0U;
                            k->press_tick = g_ms_tick;
                        }
                        else if (!k->long_fired)
                        {
                            if ((uint32_t)(g_ms_tick - k->press_tick) >= DIM_LONG_MS)
                            {
                                k->long_fired = 1U;     /* 进入连续调节(慢速起步) */
                                s_dim_tick = g_ms_tick - DIM_SPD1_INT;
                            }
                        }

                        if (k->long_fired)
                        {
                            uint32_t hold = (uint32_t)(g_ms_tick - k->press_tick);
                            uint32_t iv;

                            /* 三段加速: 慢 -> 中 -> 快 */
                            if (hold < DIM_SPD2_AT)       iv = DIM_SPD1_INT;
                            else if (hold < DIM_SPD3_AT)  iv = DIM_SPD2_INT;
                            else                          iv = DIM_SPD3_INT;

                            if ((uint32_t)(g_ms_tick - s_dim_tick) >= iv)
                            {
                                s_dim_tick = g_ms_tick;
                                Dim_Adjust(idx, (idx == 1U) ? 1 : -1);
                            }
                        }
                    }
                    else                                /* ---- 松开 ---- */
                    {
                        if (k->pressed)
                        {
                            k->pressed = 0U;
                            if (!k->long_fired)
                            {
                                if (k->click_wait &&
                                    ((uint32_t)(g_ms_tick - k->click_tick) <= DIM_DBL_MS))
                                {
                                    k->click_wait = 0U;         /* ===== 双击 ===== */
                                    if (idx == 0U)
                                        Dim_SwitchAdjustTarget();   /* 切换调节对象 */
                                    else
                                        Dim_SwitchLightMode();      /* 切换点亮模式 */
                                }
                                else
                                {
                                    k->click_wait = 1U;         /* 记为短按第一击 */
                                    k->click_tick = g_ms_tick;
                                }
                            }
                        }
                        else if (k->click_wait &&
                                 ((uint32_t)(g_ms_tick - k->click_tick) > DIM_DBL_MS))
                        {
                            k->click_wait = 0U;         /* 单击确认 -> 单步调节 */
                            Dim_Adjust(idx, (idx == 1U) ? 1 : -1);
                        }
                    }
                }
            }
        }

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
        Battery_Check();                /* 过放保护状态机 (50ms 周期) */
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
 * ==================================================================== */
static void HandleKey(uint8_t evt)
{

    /* ---- 唤醒保护: 停机恢复后短时间内吞掉当前按键按下事件,
     *      避免"唤醒后立刻再次触关机/误操作" ---- */
    if (g_ms_tick < s_swallow_until)
    {
        return;
    }

    /* ---- 电池非正常时: 告警页按键管理 (省电) ----
     *  - 告警页显示中: 任意键(除 BTN1)关闭告警页(OLED 关屏)
     *  - 告警页已关:   任意键(除 BTN1)重新点亮告警页
     *  - BTN1 始终执行开关机 (关机休眠在电量低时同样有效) */
    if (g_bat_state != BAT_STATE_OK)
    {
        if (evt & BTN1_MASK)
        {
            /* 继续执行下方 BTN1 关机逻辑 */
        }
        else
        {
            g_alert_view = !g_alert_view;
            if (g_alert_view)
            {
                g_alert_timer  = ALERT_AUTO_CLOSE_MS;   /* 重新倒计时 */
                g_disp_on      = 1;
                g_disp_change  = 1;
                g_ui_redraw    = 1;                     /* 重画告警页 */
            }
            else
            {
                g_disp_on      = 0;                     /* 关屏 */
                g_disp_change  = 1;
            }
            return;                         /* 告警态下其他键只控制显示 */
        }
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

    /* ---- BTN2/BTN3: 亮度调节 ----
     * 无级调光: 按住连续调节 (在 App_Task1ms 的 5ms 节拍中处理),
     * 此处不再做一次性步进, 避免与连续调节冲突 */
}

/* ======================================================================
 * 格式化辅助 (6x8 字体, 一页 21 字符)
 * ==================================================================== */

/**
 * @brief 显示电压值 格式 "xx.xxV"
 * @param x 起始列 0..126
 * @param y 起始页 0..3
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
    OLED_ShowStr(x, y, b);
}

/**
 * @brief 显示占空比 格式 "xx%"
 * @param x 起始列 0..126
 * @param y 起始页 0..3
 * @param permille 千分数 0..1000
 */
static void OLED_ShowPct(uint8_t x, uint8_t y, uint16_t permille)
{
    uint8_t b[5];
    uint8_t p = (uint8_t)(permille / 10);           /* 千分 -> 百分 (0..100) */

    b[0] = (uint8_t)('0' + p / 100 % 10);           /* 百位 */
    b[1] = (uint8_t)('0' + p / 10 % 10);            /* 十位 */
    b[2] = (uint8_t)('0' + p % 10);                 /* 个位 */
    b[3] = '%';
    b[4] = '\0';
    OLED_ShowStr(x, y, b);                          /* 固定 4 字符, 无残影 */
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
        OLED_ShowStr(x, y, (uint8_t *)"OFF ");      /* 4 字符与 "nnn%" 等宽, 防残影 */
}

/**
 * @brief 显示吸附检测状态 格式 "OK"/"NO"
 * @param x 起始列
 * @param y 起始页
 * @param attached 1=已吸附(高电平), 0=未吸附
 */
static void OLED_ShowDet(uint8_t x, uint8_t y, uint8_t attached)
{
    OLED_ShowStr(x, y, (uint8_t *)(attached ? "OK" : "NO"));
}

/* ======================================================================
 * 界面层 (main.c 内, 128x32 = 4 行文字)
 * ==================================================================== */

/**
 * @brief 画静态标签 (上电后调用一次)
 *
 * 正常页 (4 行):
 *   Row0: VBAT:xx.xxV + 电池状态(OK/LOW闪烁)
 *   Row1: G1:xx%  G2:xx%
 *   Row2: PWR:ON D1:OK D2:OK (外挂款) / PWR:ON CUR:1 (内置款)
 *   Row3: 按键提示
 * 告警页 (LOW/PROTECT 共用, 4 行):
 *   Row0: BATTERY LOW! (LOW 时闪烁)
 *   Row1: VBAT:xx.xxV
 *   Row2: OUTPUT ON / OUTPUT OFF
 *   Row3: CHARGE SOON / PROTECT<3.2V
 */
void UI_StaticInit(void)
{
    OLED_CLS();

    /* ---------- 电池告警页 (LOW / PROTECT) ---------- */
    if (g_bat_state != BAT_STATE_OK)
    {
        OLED_ShowStr(0, 0, (uint8_t *)"BATTERY LOW!");      /* 标题 (LOW 时闪烁) */
        OLED_ShowStr(0, 1, (uint8_t *)"VBAT:");             /* 电压行 */
        if (g_bat_state == BAT_STATE_PROTECT)
            OLED_ShowStr(0, 2, (uint8_t *)"OUTPUT OFF");    /* 已关断输出 */
        else
            OLED_ShowStr(0, 2, (uint8_t *)"OUTPUT ON");     /* 仍输出 */
        OLED_ShowStr(0, 3, (uint8_t *)((g_bat_state == BAT_STATE_PROTECT)
                                      ? "PROTECT<3.2V" : "CHARGE SOON"));
        OLED_ShowStr(0, 4, (uint8_t *)"Charge then");       /* 提示 */
        OLED_ShowStr(0, 5, (uint8_t *)"1:PWR KEY:SCR");     /* 任意键关屏/1:开关机 */
        UI_RefreshValues();
        return;
    }

    /* 正常页 (88x48: 6 行 x 14 字符) */

    /* Row0: 电池电压 (值 x30, 状态 x66) */
    OLED_ShowStr(0, 0, (uint8_t *)"VBAT:");

    /* Row1: A/B 两组亮度 (值 x12 / x54) */
    OLED_ShowStr(0, 1, (uint8_t *)"A:");
    OLED_ShowStr(42, 1, (uint8_t *)"B:");

    /* Row2: 电源 + 当前调节对象 (值 x24 / x68) */
    OLED_ShowStr(0, 2, (uint8_t *)"PWR:");
    OLED_ShowStr(44, 2, (uint8_t *)"TGT:");

    /* Row3: 外挂款显示吸附检测; 内置款显示型号 */
#if BSP_DETECT_ENABLED
    OLED_ShowStr(0, 3, (uint8_t *)"D1:");
    OLED_ShowStr(42, 3, (uint8_t *)"D2:");
#else
    OLED_ShowStr(0, 3, (uint8_t *)"BUILT-IN");
#endif

    /* Row4/5: 按键提示 (单击微调 / 长按连续 / 双击切换) */
    OLED_ShowStr(0, 4, (uint8_t *)"2/3:BRT 1:PWR");
    OLED_ShowStr(0, 5, (uint8_t *)"2x:TGT 3x:LIT");

    /* 画一遍动态数值, 避免首屏空白 */
    UI_RefreshValues();
}

/**
 * @brief 刷新数值区 (由主循环在 g_ui_req 置位时调用, 200ms 一次)
 * 只更新数值区域, 避免整屏重刷, 与 H563 OLED_Scan 思路一致
 */
void UI_RefreshValues(void)
{
    /* ---------- 电池告警页: 只刷电压 + (LOW 时标题闪烁) ---------- */
    if (g_bat_state != BAT_STATE_OK)
    {
        OLED_ShowVBat(30, 1, g_vbat_mv);
        if (g_bat_state == BAT_STATE_LOW)   /* LOW 页: 标题 0.2s 交替闪烁 */
            OLED_ShowStr(0, 0, (uint8_t *)(((g_ms_tick / 200U) & 1U)
                                          ? "BATTERY LOW!" : "            "));
        return;
    }

    /* Row0: 电压 + 电池状态灯 */
    OLED_ShowVBat(30, 0, g_vbat_mv);
    if (g_bat_state == BAT_STATE_LOW)
        OLED_ShowStr(66, 0, (uint8_t *)(((g_ms_tick / 200U) & 1U) ? "LOW" : "   "));
    else
        OLED_ShowStr(66, 0, (uint8_t *)"OK ");

    /* Row1: A/B 两组亮度 */
    OLED_ShowGroup(12, 1, (const LEDGroup_t *)&g_grp1);
    OLED_ShowGroup(54, 1, (const LEDGroup_t *)&g_grp2);

    /* Row2: 电源状态 + 当前调节对象 (A/B/AB) */
    OLED_ShowStr(24, 2, (uint8_t *)(g_power_on ? "ON " : "OFF"));
    OLED_ShowStr(68, 2, (uint8_t *)((s_dim_target == 0U) ? "A  " :
                                    (s_dim_target == 1U) ? "B  " : "AB "));

    /* Row3: 外挂款吸附检测状态 */
#if BSP_DETECT_ENABLED
    OLED_ShowDet(18, 3, g_det1);
    OLED_ShowDet(60, 3, g_det2);
#endif
}

/**
 * @brief 整屏切换 (正常页 <-> 电池告警页)
 */
static void UI_TurnPage(void)
{
    OLED_CLS();
    UI_StaticInit();
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

    /* ---- 时钟: 内部高速时钟 HSI 48MHz (无外部晶振) ---- */
    SYSCTRL_HSI_Enable(SYSCTRL_HSIOSC_DIV1);
    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();

    /* ---- PWM 输出引脚提前拉低 (最先配置) ----
     * 复位/初始化期间 GPIO 高阻悬空, SY7200 EN 被拉高会点亮 LED;
     * 先置低电平再配置为输出, 把"悬空点亮"缩短到启动代码的几百 us */
    PA03_SETLOW();
    PB01_SETLOW();
    {
        GPIO_InitTypeDef gpio = {0};
        gpio.IT   = GPIO_IT_NONE;
        gpio.Mode = GPIO_MODE_OUTPUT_PP;
        gpio.Pins = GPIO_PIN_3;
        GPIO_Init(CW_GPIOA, &gpio);     /* PA03 (PWM2) */
        gpio.Pins = GPIO_PIN_1;
        GPIO_Init(CW_GPIOB, &gpio);     /* PB01 (PWM1) */
    }

    /* ---- CE: LDO 使能 (PB04, 上电默认使能) ---- */
    gpio.IT   = GPIO_IT_NONE;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pins = CE_GPIO_PINS;
    GPIO_Init((GPIO_TypeDef *)CE_GPIO_PORT, &gpio);
    LDO_CE_Enable();
    g_power_on = 1;

    /* ---- 亮度记录: RTC(LSI) 初始化 + Flash 读取 ----
     * 距上次关机 <= 1 小时: 恢复保存亮度; 否则默认 10% */
    BSP_SAVE_Init();
    g_grp1.brightness = BSP_SAVE_GetBootBrightness();   /* 内部已做 3% 下限钳位 */
    g_grp2.brightness = BSP_SAVE_GetBootBrightness2();

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

    /* ---- 按当前状态输出 PWM (组默认亮 50%; 外挂款未吸附组不输出) ---- */
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

            /* 关机处理期间吞掉所有按键事件 (含松手回弹), 防止误翻回开机 */
            s_swallow_until = g_ms_tick + 100000U;

            /* 关机前保存两组亮度到 Flash (含 RTC 时间戳, 供 1 小时窗口恢复) */
            BSP_SAVE_StoreOnShutdown(g_grp1.brightness, g_grp2.brightness);
            s_save_dirty = 0;

            BSP_POWER_EnterStop();          /* 休眠, 唤醒后返回 */

            /* ============ 唤醒恢复 (按键按下) ============
             * 顺序要点: 先吞按键 -> 恢复时钟/时基 -> 上电 3V3 ->
             *           等 3V3 稳定后再初始化按键(吸收"唤醒那一按") */
            s_swallow_until = g_ms_tick + 1000; /* 先吞掉唤醒瞬间的按键事件 */
            BSP_POWER_WakeupInit();         /* 恢复时钟/时基 (不初始化按键) */
#if BSP_DETECT_ENABLED
            BSP_DETECT_Init();              /* [外挂款] 重新初始化吸附检测 */
#endif

            g_power_on = 1;
            LDO_CE_Enable();                /* CE 拉高, LDO 上电 */
            {
                volatile uint32_t k;
                for (k = 0; k < 480000U; k++);  /* 约 10~20ms: 等 3V3 建立 */
            }
            BSP_BTNs_Init();                /* 3V3 稳定后再初始化按键:
                                             * 正按着的键被预置为"已按下", 不产生事件 */
            s_swallow_until = g_ms_tick + 300;  /* 之后再保留 300ms 保护窗 */

            /* 唤醒后亮度恢复默认 10% (不再保持关机前值) */
            g_grp1.brightness = 100;
            g_grp2.brightness = 100;
            ApplyOutputs();
            UpdateDetect();                 /* 恢复吸附状态联动 */

            /* 屏幕延后恢复: 先禁刷屏, 等指定数量的 1ms 中断后再重新初始化
             * (屏在关机期间掉电; 立即刷屏会出现随机亮点/花屏) */
            g_disp_on = 0;                  /* 屏未就绪, 禁止刷屏 */
            s_wake_resume_at = g_ms_tick + WAKE_RESUME_TICKS;
        }

        /* ---------- 唤醒后延时屏幕恢复 (等 500 个 1ms 中断) ----------
         * 此时屏供电已稳定: 完整重新初始化 (含上电等待+清屏), 再整屏重绘 */
        if (s_wake_resume_at && (g_ms_tick >= s_wake_resume_at))
        {
            s_wake_resume_at = 0;
            OLED_Init();                    /* 屏曾掉电: 完整重新初始化 */
            g_disp_on   = 1;                /* 恢复刷屏 */
            g_ui_req    = 0;
            g_ui_redraw = 1;                /* 整屏重绘 (正常页/告警页) */
        }

        /* ---------- 亮度变更延时自动保存 (2s) ----------
         * 直接按 Reset / 断电重启时也能保留最近一次亮度设置 */
        if (s_save_dirty &&
            ((uint32_t)(g_ms_tick - s_save_tick) >= SAVE_DELAY_MS))
        {
            s_save_dirty = 0;
            BSP_SAVE_StoreOnShutdown(g_grp1.brightness, g_grp2.brightness);
        }

        /* ---------- 显示开关 (告警页按键关闭/重新点亮) ---------- */
        if (g_disp_change)
        {
            g_disp_change = 0;
            if (g_disp_on) OLED_ON();
            else           OLED_OFF();
        }

        /* ---------- 页面切换 (正常页 <-> 告警页) ---------- */
        if (g_ui_redraw)
        {
            g_ui_redraw = 0;
            g_ui_req = 0;
            if (g_disp_on)
                UI_TurnPage();
        }

        /* ---------- 界面刷新 (200ms 由 ISR 请求) ----------
         * OLED 写入耗时较长, 放主循环中执行, 避免阻塞 1ms 时基中断 */
        if (g_ui_req)
        {
            g_ui_req = 0;
            if (g_disp_on)
                UI_RefreshValues();
        }
    }
}