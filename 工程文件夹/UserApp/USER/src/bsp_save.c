#include "bsp_save.h"
#include "cw32l010_sysctrl.h"
#include "cw32l010_rtc.h"
#include "cw32l010_flash.h"

/*******************************************************************************
 * BSP_SAVE - 关机亮度保存 / 开机恢复 (Flash + RTC) 实现
 *
 * 参考: 官方 FLASH\flash_EraseWrite 例程 (最后一页 127 使用方式),
 *       RTC\RTC_Calendar 例程 (LSI 时钟源), PWR 例程说明
 *       ("RTC 初始化限制只能在上电复位时配置" -> 系统复位时库直接返回,
 *          RTC 走时保持连续, 这正是 1 小时窗口跨 Reset 可用的基础)
 ******************************************************************************/

#define SAVE_PAGE_NUM      127U
#define SAVE_ADDR          (FLASH_PAGE_SIZE * SAVE_PAGE_NUM)    /* 0xFE00 */
#define SAVE_MAGIC         0x5A5A2025UL

/* Flash 记录结构 (12 字节) */
typedef struct
{
    uint32_t magic;         /* = SAVE_MAGIC 表示记录有效 */
    uint16_t brightness;    /* 亮度千分数 100..1000 */
    uint16_t reserved;      /* 填充 */
    uint32_t rtc_sec;       /* 关机时刻: RTC 当天秒数 (00:00:00 起) */
} SaveRecord_t;

static uint16_t s_boot_brightness = BSP_SAVE_DEFAULT_BRIGHT;    /* 开机亮度 */

/**
 * @brief 读取 RTC 当前时间并换算为"当天秒数"
 * @return 0..86399 (BCD 时分秒 -> 十进制 -> 秒)
 * @note 跨天判定不做处理: 关机与开机跨越午夜时保守按"超时"处理
 */
static uint32_t RTC_GetDaySec(void)
{
    RTC_TimeTypeDef t;
    uint32_t h, m, s;

    RTC_GetTime(&t);
    h = ((uint32_t)(t.Hour >> 4) & 0xF) * 10U + (uint32_t)(t.Hour & 0xF);
    m = ((uint32_t)(t.Minute >> 4) & 0xF) * 10U + (uint32_t)(t.Minute & 0xF);
    s = ((uint32_t)(t.Second >> 4) & 0xF) * 10U + (uint32_t)(t.Second & 0xF);

    return h * 3600U + m * 60U + s;
}

/**
 * @brief 初始化 RTC (LSI) 并读取上次保存的亮度记录
 * @note RTC_Init 在非上电复位(如按 Reset)时不会重置 RTC, 走时连续;
 *       上电复位时从 00:00:00 重新开始
 */
void BSP_SAVE_Init(void)
{
    RTC_InitTypeDef rtc = {0};
    const SaveRecord_t *rec = (const SaveRecord_t *)SAVE_ADDR;
    uint32_t now, saved;

    /* ---- 1. 启动 LSI 时钟源 (RTC 使用, 无外部晶振) ---- */
    SYSCTRL_LSI_Enable();

    /* ---- 2. RTC 初始化 (仅上电复位真正配置; 其余复位保持走时) ---- */
    rtc.RTC_ClockSource   = RTC_RTCCLK_FROM_LSI;
    rtc.DateStruct.Year   = 0x25;
    rtc.DateStruct.Month  = 0x01;
    rtc.DateStruct.Day    = 0x01;
    rtc.DateStruct.Week   = 0;
    rtc.TimeStruct.Hour   = 0x00;
    rtc.TimeStruct.Minute = 0x00;
    rtc.TimeStruct.Second = 0x00;
    rtc.TimeStruct.AMPM   = 0;
    rtc.TimeStruct.H24    = 1;              /* 24 小时制 */
    RTC_Init(&rtc);

    /* ---- 3. 读取 Flash 记录, 判断是否在恢复窗口内 ---- */
    if ((rec->magic == SAVE_MAGIC) &&
        (rec->brightness >= 100U) && (rec->brightness <= 1000U))
    {
        now   = RTC_GetDaySec();
        saved = rec->rtc_sec;

        /* 同一时间轴且间隔 <= 1 小时 -> 恢复; 掉电重启(RTC 归零)时
         * now < saved, 自动落入"不恢复"分支 */
        if ((now >= saved) && ((now - saved) <= BSP_SAVE_WINDOW_SEC))
            s_boot_brightness = rec->brightness;
    }
}

/**
 * @brief 获取开机亮度 (窗口内为保存值, 否则默认 10%)
 */
uint16_t BSP_SAVE_GetBootBrightness(void)
{
    return s_boot_brightness;
}

/**
 * @brief 调试: 获取当前 RTC 当天秒数 (验证走时)
 */
uint32_t BSP_SAVE_GetRtcSec(void)
{
    return RTC_GetDaySec();
}

/**
 * @brief 保存亮度到 Flash (最后一页)
 * @param brightness 当前亮度千分数 (100..1000)
 * @note 调用后即进入关机流程; 擦写期间关中断防止取指/时序异常
 */
void BSP_SAVE_StoreOnShutdown(uint16_t brightness)
{
    SaveRecord_t rec;

    rec.magic      = SAVE_MAGIC;
    rec.brightness = brightness;
    rec.reserved   = 0xFFFFU;
    rec.rtc_sec    = RTC_GetDaySec();

    __disable_irq();
    FLASH_UnlockPages(SAVE_ADDR, SAVE_ADDR);                /* 解锁最后一页 */
    FLASH_ErasePages(SAVE_ADDR, SAVE_ADDR);                 /* 擦除 */
    FLASH_WriteBytes(SAVE_ADDR, (uint8_t *)&rec, (uint16_t)sizeof(rec)); /* 写入 */
    FLASH_LockAllPages();                                   /* 重新加锁 */
    __enable_irq();
}
