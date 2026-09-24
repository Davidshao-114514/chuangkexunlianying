#ifndef __BSP_SAVE_H
#define __BSP_SAVE_H

#include "cw32l010.h"

/*******************************************************************************
 * BSP_SAVE - 关机亮度保存 / 开机恢复 (Flash + RTC 时间窗)
 *
 * 功能: 关机前把当前亮度(千分数)保存到 Flash 最后一页, 同时记录 RTC 时间;
 *       开机时若距上次关机 <= 1 小时, 恢复保存的亮度; 否则用默认 10%。
 * 计时: RTC 使用内部 LSI 时钟 (无外部晶振)。
 *       RTC 在系统复位(Reset键)后继续走时, 故可跨 Reset 计时;
 *       掉电(拔电池)后 RTC 归零, 时间戳比较自然判为"超时" -> 默认亮度。
 * 存储: Flash 第 127 页 (0xFE00), 12 字节记录 + magic 校验。
 ******************************************************************************/

#define BSP_SAVE_WINDOW_SEC     3600U   /* 恢复窗口: 1 小时 (秒) */
#define BSP_SAVE_DEFAULT_BRIGHT 100U    /* 默认亮度: 千分数 100 = 10% */

void     BSP_SAVE_Init(void);                       /* 上电: 启动 LSI/RTC, 读记录 */
uint16_t BSP_SAVE_GetBootBrightness(void);          /* 开机亮度: 窗口内恢复, 否则默认 */
void     BSP_SAVE_StoreOnShutdown(uint16_t brightness);  /* 保存亮度 (Flash) */
uint32_t BSP_SAVE_GetRtcSec(void);                  /* 调试: 当前 RTC 当天秒数 */

#endif /* __BSP_SAVE_H */
