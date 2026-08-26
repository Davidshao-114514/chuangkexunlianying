#ifndef __BSP_OLED_H
#define __BSP_OLED_H

#include "cw32l010.h"
#include "bsp_i2c.h"
#include "bsp_oled_text.h"

/*******************************************************************************
 * BSP_OLED - 0.91" 128x64 OLED (SSD1306) 显示驱动库
 *
 * 移植来源: H563 工程 Core/Src/bsp_oled.c
 * 接口层:   软件 IIC (bsp_i2c.c), SDA=PB05, SCL=PB06, 设备地址 0x3C
 * 职责:     仅提供"显示原语" (命令/数据写、初始化、清屏、定位、字符串/图片显示)
 * 屏幕内容(刷新布局/数值)由 main.c 中的 UI 层负责, 与 H563 工程结构一致
 *          (H563: bsp_oled 提供底层, OLED_Scan 内容刷新在应用层)
 ******************************************************************************/

#define OLED_DEV_ADDR      0x3C        /* SSD1306 (0x78 >> 1) */
#define OLED_WIDTH         128         /* 列数 0..127 */
#define OLED_HEIGHT        64          /* 行数(像素) */
#define OLED_PAGES         8           /* 页数(行/8): 0..7, 每页 8 行像素 */

/* ---- 底层: 写命令/写数据 (IIC) ---- */
void WriteCmd(uint8_t cmd);                 /* 写 SSD1306 命令字节 */
void WriteDat(uint8_t dat);                 /* 写显示数据(SGRAM)字节 */

/* ---- 初始化/开关 ---- */
void OLED_Init(void);                       /* 上电初始化 (含清屏) */
void OLED_ON(void);                         /* 开启显示(含电荷泵) */
void OLED_OFF(void);                        /* 关闭显示 */

/* ---- 显存操作原语 ---- */
void OLED_SetPos(uint8_t x, uint8_t y);     /* 定位: x列0..127, y页0..7 */
void OLED_Fill(uint8_t fillData);           /* 全屏填充 */
void OLED_CLS(void);                        /* 清屏 (填充0x00) */

/* ---- 显示原语 ---- */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[], uint8_t textSize);
                                            /* 字符串: textSize 1=6x8, 2=8x16 */
void OLED_ShowU16(uint8_t x, uint8_t y, uint16_t v, uint8_t textSize);
                                            /* 十进制数(5位, 前导空格) */
void OLED_ShowCN(uint8_t x, uint8_t y, uint8_t n);  /* 16x16 中文点阵 (n<8) */
void OLED_DrawBMP(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1, uint8_t bmp[]);
                                            /* 位图: 从(x0,y0)页到(x1,y1)页 */

#endif /* __BSP_OLED_H */
