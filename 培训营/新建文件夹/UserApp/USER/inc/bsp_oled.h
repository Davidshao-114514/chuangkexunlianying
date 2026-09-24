#ifndef __BSP_OLED_H
#define __BSP_OLED_H

#include "cw32l010.h"
#include "bsp_i2c.h"
#include "bsp_oled_text.h"

/*******************************************************************************
 * BSP_OLED - 0.91" 128x32 OLED (SSD1306) 显示驱动库
 *
 * 移植来源: H563 工程 Core/Src/bsp_oled.c (裁剪为 6x8 字符显示)
 * 接口层:   软件 IIC (bsp_i2c.c), SDA=PB05, SCL=PB06, 设备地址 0x3C
 * 职责:     仅提供"显示原语"; 屏幕内容(布局/数值)由 main.c 的 UI 层负责
 * 注意:     0.91" 屏为 128x32 -> 纵向 32 行像素 = 4 页 (y=0..3)
 ******************************************************************************/

#define OLED_DEV_ADDR      0x3C        /* SSD1306 (0x78 >> 1) */
#define OLED_WIDTH         128         /* 列数 0..127 */
#define OLED_HEIGHT        32          /* 行数(像素) 0..31 */
#define OLED_PAGES         4           /* 页数: 0..3, 每页 8 行像素 */

/* ---- 底层: 写命令/写数据 (IIC) ---- */
void WriteCmd(uint8_t cmd);                 /* 写 SSD1306 命令字节 */
void WriteDat(uint8_t dat);                 /* 写显示数据(SGRAM)字节 */

/* ---- 初始化/开关 ---- */
void OLED_Init(void);                       /* 上电初始化 (含清屏) */
void OLED_ON(void);                         /* 开启显示(含电荷泵) */
void OLED_OFF(void);                        /* 关闭显示 */

/* ---- 显存操作原语 ---- */
void OLED_SetPos(uint8_t x, uint8_t y);     /* 定位: x列0..127, y页0..3 */
void OLED_Fill(uint8_t fillData);           /* 全屏填充 */
void OLED_CLS(void);                        /* 清屏 (填充0x00) */

/* ---- 显示原语 (仅 6x8 字符) ---- */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[]);
                                            /* 字符串: 6x8, y=页号0..3,
                                             * 每页最多21字符, 无自动换行 */

#endif /* __BSP_OLED_H */
