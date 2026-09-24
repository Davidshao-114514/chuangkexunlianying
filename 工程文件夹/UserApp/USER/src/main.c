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
#define BAT_LOW_MV         3500U   /* 电压 < 3500mV: 电量低提醒 */
#define BAT_WARN_RECOVER_MV 3550U  /* 回升到 3550mV: 解除低电提醒 (滞回) */
#define BAT_CUT_MV         3200U   /* 电压 < 3200mV: 过放保护, 关断输出 */
#define BAT_CUT_RECOVER_MV 3350U   /* 回升到 3350mV: 恢复输出 (滞回) */
#define BAT_CHK_HOLD       40      /* 状态切换需连续 40 次采样 (50ms x 40 = 2s) */

/* 电池状态机 */
#define BAT_STATE_OK       0       /* 正常 */
#define BAT_STATE_LOW      1       /* 低电量 (3.5V~3.2V): 提醒 */
#define BAT_STATE_PROTECT  2       /* 过放保护 (<3.2V): 输出关断 */

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

/* 调试: 最近一次按键事件掩码 (页5 显示, 验证按键硬件) */
static volatile uint8_t s_last_evt = 0;

/* 亮度变更 -> 延时自动保存 (解决"直接按 Reset 不经过关机流程"的丢失问题) */
static volatile uint8_t  s_save_dirty = 0;   /* 1=亮度有变更待保存 */
static volatile uint32_t s_save_tick  = 0;   /* 最后一次变更的时刻 */
#define SAVE_DELAY_MS   2000U                /* 变更后 2s 无操作即写入 Flash */

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
 *   OK     -- 见 <3500mV 持续 2s --> LOW    (低电提醒, 输出不关)
 *   LOW    -- 回 >3550mV 持续 2s --> OK
 *   LOW    -- 见 <3200mV 持续 2s --> PROTECT (关断输出 + OLED 告警)
 *   PROTECT-- 回 >3350mV 持续 2s --> OK (自动恢复输出)
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
        {
            s_last_evt = evt;           /* 调试: 记录事件供页5显示 */
            HandleKey(evt);             /* 按键功能 (开关机/亮度) */
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
    uint16_t br;

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

    /* ---- BTN2/BTN3: 亮度-/+ (两组同步) ---- */
    if (evt & (BTN2_MASK | BTN3_MASK))
    {
        br = g_grp1.brightness;                 /* 两组共用亮度, 取自组1 */

        if (evt & BTN2_MASK)                    /* 亮度- */
            br = (br >= 100) ? (br - 100) : 100;    /* 下限 10% */
        if (evt & BTN3_MASK)                    /* 亮度+ */
            br = (br <= 900) ? (br + 100) : 1000;   /* 上限 100% */

        g_grp1.brightness = br;                 /* 同步两组 */
        g_grp2.brightness = br;
        g_ui_req = 1;
        ApplyOutputs();

        s_save_dirty = 1;                       /* 标记待保存 (2s 后写 Flash) */
        s_save_tick  = g_ms_tick;
    }
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
 * @brief 调试: 显示 4 位十进制原始值 (0..4095)
 */
static void OLED_ShowDec4(uint8_t x, uint8_t y, uint16_t v)
{
    uint8_t b[5];
    b[0] = (uint8_t)('0' + v / 1000 % 10);
    b[1] = (uint8_t)('0' + v / 100 % 10);
    b[2] = (uint8_t)('0' + v / 10 % 10);
    b[3] = (uint8_t)('0' + v % 10);
    b[4] = '\0';
    OLED_ShowStr(x, y, b);
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
        OLED_ShowStr(0, 3, (uint8_t *)"T");
        OLED_ShowDec4(12, 3, g_bgr_trim_mv);            /* 调试: BGR trim 值 (mV) */
        OLED_ShowStr(48, 3, (uint8_t *)"R");
        OLED_ShowDec4(60, 3, g_bgr_raw);                /* 调试: BGR 通道原始值 */
        UI_RefreshValues();             /* 画动态电压 */
        return;
    }

    /* Row0: VBAT 标签 (数值 x30, 电池状态 x72) */
    OLED_ShowStr(0, 0, (uint8_t *)"VBAT:");

    /* Row1: 组占空比标签 (数值 x24 / x78) */
    OLED_ShowStr(0, 1, (uint8_t *)"G1:");
    OLED_ShowStr(54, 1, (uint8_t *)"G2:");

    /* Row2: 电源 + 状态 (外挂款 D1/D2 检测, 内置款型号标识) */
    OLED_ShowStr(0, 2, (uint8_t *)"PWR:");
#if BSP_DETECT_ENABLED
    OLED_ShowStr(42, 2, (uint8_t *)"D1:");
    OLED_ShowStr(72, 2, (uint8_t *)"D2:");
#else
    OLED_ShowStr(42, 2, (uint8_t *)"BUILT-IN");
#endif

    /* Row3: 按键提示 (3 键: 开关机 / 亮度±) */
    OLED_ShowStr(0, 3, (uint8_t *)"1:PWR 2:BRT- 3:BRT+");

#if (OLED_PAGES >= 8)
    /* ---------- 0.96" 128x64: 下半屏(页5~7) ---------- */
    /* 页5 为按键调试行 (动态刷新, 见 UI_RefreshValues) */
    OLED_ShowStr(0, 6, (uint8_t *)"KEY2:PA4 BRT- KEY3:PA5 BRT+");
    OLED_ShowStr(0, 7, (uint8_t *)"DET:Hi=LINK 3.5V/3.2V");
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
    /* ---------- 电池告警页: 只刷电压 + (LOW 时标题闪烁) ---------- */
    if (g_bat_state != BAT_STATE_OK)
    {
        OLED_ShowVBat(30, 1, g_vbat_mv);
        OLED_ShowStr(72, 1, (uint8_t *)"raw");          /* 调试: 显示 ADC 原始值 */
        OLED_ShowDec4(90, 1, g_adc_raw);
        OLED_ShowStr(72, 2, (uint8_t *)"i12");          /* 调试: BGR1.2V raw */
        OLED_ShowDec4(90, 2, g_bgr_raw);
        if (g_bat_state == BAT_STATE_LOW)   /* LOW 页: 标题 0.2s 交替闪烁 */
            OLED_ShowStr(0, 0, (uint8_t *)(((g_ms_tick / 200U) & 1U)
                                          ? "BATTERY LOW!" : "            "));
        return;
    }

    /* Row0: 电压 + 电池状态灯 */
    OLED_ShowVBat(30, 0, g_vbat_mv);
    if (g_bat_state == BAT_STATE_LOW)
        OLED_ShowStr(72, 0, (uint8_t *)(((g_ms_tick / 200U) & 1U) ? "LOW " : "    "));
    else
        OLED_ShowStr(72, 0, (uint8_t *)"OK  ");

    /* Row1: 组1/组2 占空比 */
    OLED_ShowGroup(24, 1, (const LEDGroup_t *)&g_grp1);
    OLED_ShowGroup(78, 1, (const LEDGroup_t *)&g_grp2);

    /* Row2: 电源/吸附检测/当前组 */
    OLED_ShowStr(24, 2, (uint8_t *)(g_power_on ? "ON " : "OFF"));
#if BSP_DETECT_ENABLED
    OLED_ShowDet(60, 2, g_det1);
    OLED_ShowDet(90, 2, g_det2);
#endif

#if (OLED_PAGES >= 8)
    /* 页5: 按键调试 — 实时电平状态 ST 与最近事件 EV (各 3 位二进制位域)
     * 按住 KEY1 -> ST 显示 1; 按住 KEY2 -> 2; 按住 KEY3 -> 4 */
    OLED_ShowStr(0, 5, (uint8_t *)"ST:");
    OLED_ShowDec4(18, 5, BSP_BTNs_GetState());
    OLED_ShowStr(42, 5, (uint8_t *)"EV:");
    OLED_ShowDec4(60, 5, s_last_evt);
    OLED_ShowStr(84, 5, (uint8_t *)"S:");
    OLED_ShowDec4(96, 5, (uint16_t)(BSP_SAVE_GetRtcSec() % 10000U));  /* RTC秒(尾4位) */
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
    g_grp1.brightness = BSP_SAVE_GetBootBrightness();
    g_grp2.brightness = g_grp1.brightness;

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

            /* 关机前保存当前亮度到 Flash (含 RTC 时间戳, 供 1 小时窗口恢复) */
            BSP_SAVE_StoreOnShutdown(g_grp1.brightness);
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

            OLED_ON();                      /* 开屏 */
            UpdateDetect();                 /* 刷新吸附状态并联动输出 */
            g_ui_req = 1;                   /* 刷一次界面 */
        }

        /* ---------- 亮度变更延时自动保存 (2s) ----------
         * 直接按 Reset / 断电重启时也能保留最近一次亮度设置 */
        if (s_save_dirty &&
            ((uint32_t)(g_ms_tick - s_save_tick) >= SAVE_DELAY_MS))
        {
            s_save_dirty = 0;
            BSP_SAVE_StoreOnShutdown(g_grp1.brightness);
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
