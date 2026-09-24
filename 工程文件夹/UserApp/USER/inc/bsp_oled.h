#ifndef __BSP_OLED_H
#define __BSP_OLED_H

#include "cw32l010.h"
#include "bsp_i2c.h"
#include "bsp_oled_text.h"

/*******************************************************************************
 * BSP_OLED - SSD1306 OLED 显示驱动库
 *
 * 移植来源: H563 工程 Core/Src/bsp_oled.c (裁剪为 6x8 字符显示)
 * 接口层:   软件 IIC (bsp_i2c.c), SDA=PB05, SCL=PB06, 设备地址 0x3C
 * 职责:     仅提供"显示原语"; 屏幕内容(布局/数值)由 main.c 的 UI 层负责
 *
 * [屏幕面板选择] 下方 OLED_PANEL_64 切换 (改后需重新编译):
 *   1 = 0.96" 128x64 (8 页, 每页 6x8 字体)
 *   0 = 0.91" 128x32 (4 页)
 ******************************************************************************/

#define OLED_PANEL_64       1       /* 1=0.96"(128x64), 0=0.91"(128x32) */

#if OLED_PANEL_64
/* 设备地址自动探测结果 (0x3C 或 0x3D), 见 bsp_oled.c */
extern uint8_t g_oled_addr;
#define OLED_WIDTH         128         /* 列数 0..127 */
#define OLED_HEIGHT        64          /* 行数(像素) 0..63 */
#define OLED_PAGES         8           /* 页数: 0..7, 每页 8 行像素 */
#else
/* 设备地址自动探测结果 (0x3C 或 0x3D), 见 bsp_oled.c */
extern uint8_t g_oled_addr;
#define OLED_WIDTH         128         /* 列数 0..127 */
#define OLED_HEIGHT        32          /* 行数(像素) 0..31 */
#define OLED_PAGES         4           /* 页数: 0..3, 每页 8 行像素 */
#endif

/* ---- 底层: 写命令/写数据 (IIC) ---- */
void WriteCmd(uint8_t cmd);                 /* 写 SSD1306 命令字节 */
void WriteDat(uint8_t dat);                 /* 写显示数据(SGRAM)字节 */

/* ---- 初始化/开关 ---- */
void OLED_Init(void);                       /* 上电初始化 (含清屏) */
void OLED_ON(void);                         /* 开启显示(含电荷泵) */
void OLED_OFF(void);                        /* 关闭显示 */

/* ---- 显存操作原语 ---- */
void OLED_SetPos(uint8_t x, uint8_t y);     /* 定位: x列0..127, y页0..OLED_PAGES-1 */
void OLED_Fill(uint8_t fillData);           /* 全屏填充 */
void OLED_CLS(void);                        /* 清屏 (填充0x00) */

/* ---- 显示原语 (仅 6x8 字符) ---- */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[]);
                                            /* 字符串: 6x8, y=页号, 无自动换行 */

#endif /* __BSP_OLED_H */
