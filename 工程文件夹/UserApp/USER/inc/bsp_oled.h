#ifndef __BSP_OLED_H
#define __BSP_OLED_H

#include "cw32l010.h"
#include "bsp_i2c.h"
#include "bsp_oled_text.h"

/*******************************************************************************
 * BSP_OLED - 0.5" 88x48 OLED (CH1115) 显示驱动库
 *
 * 驱动 IC: CH1115 (指令集兼容 SSD1306 风格, 增加 0xAD IREF 命令)
 * 接口:    软件 IIC (bsp_i2c.c), SDA=PB05, SCL=PB06, 地址 0x3C (自动探测 0x3D)
 * 分辨率:  88 列 x 48 行 -> 6 页 (每页 8 行像素), 6x8 字体每行 14 字符
 ******************************************************************************/

/* 设备地址自动探测结果 (0x3C 或 0x3D), 见 bsp_oled.c */
extern uint8_t g_oled_addr;

#define OLED_WIDTH         88          /* 列数 0..87 */
#define OLED_HEIGHT        48          /* 行数(像素) 0..47 */
#define OLED_PAGES         6           /* 页数: 0..5, 每页 8 行像素 */
#define OLED_COL_OFFSET    0U          /* 列窗口偏移: 厂商官方 C51 驱动从列 0 开始 */

/* ---- 底层: 写命令/写数据 (IIC) ---- */
void WriteCmd(uint8_t cmd);                 /* 写命令字节 */
void WriteDat(uint8_t dat);                 /* 写显示数据(SGRAM)字节 */

/* ---- 初始化/开关 ---- */
void OLED_Init(void);                       /* 上电初始化 (含清屏) */
void OLED_ON(void);                         /* 开启显示(含电荷泵) */
void OLED_OFF(void);                        /* 关闭显示 */

/* ---- 显存操作原语 ---- */
void OLED_SetPos(uint8_t x, uint8_t y);     /* 定位: x列0..87, y页0..5 */
void OLED_Fill(uint8_t fillData);           /* 全屏填充 */
void OLED_CLS(void);                        /* 清屏 (填充0x00) */

/* ---- 显示原语 (仅 6x8 字符) ---- */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[]);
                                            /* 字符串: 6x8, y=页号0..5,
                                             * 每行最多 14 字符, 越界截断 */

#endif /* __BSP_OLED_H */
