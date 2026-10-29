#include "bsp_oled.h"

/*******************************************************************************
 * BSP_OLED - 0.91" 128x32 OLED (SSD1306) 驱动实现
 * 仅包含底层显示原语 (6x8 字符串); 屏幕内容刷新在 main.c 的 UI_* 函数中
 * 移植来源: H563 工程 Core/Src/bsp_oled.c, 底层 IIC 见 bsp_i2c.c
 ******************************************************************************/

/* 毫秒级延时 (48MHz 循环近似) */
static void delay_us(uint32_t n)
{
    uint32_t cnt = n * 48;              /* 48MHz 每us约48次循环 */
    while (cnt--);
}

static void delay_ms(uint32_t n)
{
    while (n--)
        delay_us(1000);
}

/**
 * @brief 写 SSD1306 命令字节
 * @param cmd 命令字节 (协议: D/C=0x00)
 */
void WriteCmd(uint8_t cmd)
{
    I2C_WriteData_8bit(OLED_DEV_ADDR, 0x00, cmd);
}

/**
 * @brief 写 SSD1306 显示数据字节
 * @param dat 数据字节 (协议: D/C=0x40)
 */
void WriteDat(uint8_t dat)
{
    I2C_WriteData_8bit(OLED_DEV_ADDR, 0x40, dat);
}

/**
 * @brief OLED 初始化 (128x32, SSD1306)
 * 时序要求: 上电后需稳定一段时间; RST 与芯片 NRST 并联, 由系统复位驱动
 */
void OLED_Init(void)
{
    delay_ms(100);                      /* 上电/复位稳定 */

    WriteCmd(0xAE);                     /* 关显示 */
    WriteCmd(0x20);                     /* 内存寻址模式 */
    WriteCmd(0x10);                     /* 页寻址 */
    WriteCmd(0xB0);                     /* 页起始地址 0 */
    WriteCmd(0xC8);                     /* COM 扫描方向 */
    WriteCmd(0x00);                     /* 低列地址 */
    WriteCmd(0x10);                     /* 高列地址 */
    WriteCmd(0x40);                     /* 起始行地址 */
    WriteCmd(0x81);                     /* 对比度 */
    WriteCmd(0xFF);                     /* 最亮 */
    WriteCmd(0xA1);                     /* 段重映射 */
    WriteCmd(0xA6);                     /* 正常显示 */
    WriteCmd(0xA8);                     /* 复用比: 128x32 -> 0x1F (32行) */
    WriteCmd(0x1F);                     /* 32-1=31 */
    WriteCmd(0xA4);                     /* 跟随 RAM 内容显示 */
    WriteCmd(0xD3);                     /* 显示偏移 */
    WriteCmd(0x00);                     /* 无偏移 */
    WriteCmd(0xD5);                     /* 时钟分频/振荡频率 */
    WriteCmd(0xF0);
    WriteCmd(0xD9);                     /* 预充电周期 */
    WriteCmd(0x22);
    WriteCmd(0xDA);                     /* COM 引脚配置: 128x32 -> 0x02 */
    WriteCmd(0x02);                     /* 32行: 实际引脚数30禁用, 其余不变 */
    WriteCmd(0xDB);                     /* VCOMH */
    WriteCmd(0x20);
    WriteCmd(0x8D);                     /* 电荷泵 */
    WriteCmd(0x14);                     /* 开启 */
    WriteCmd(0xAF);                     /* 开显示 */

    OLED_CLS();                         /* 清除显存 */
}

/**
 * @brief 开启显示
 */
void OLED_ON(void)
{
    WriteCmd(0x8D);
    WriteCmd(0x14);
    WriteCmd(0xAF);
}

/**
 * @brief 关闭显示
 */
void OLED_OFF(void)
{
    WriteCmd(0x8D);
    WriteCmd(0x10);
    WriteCmd(0xAE);
}

/**
 * @brief 显存光标定位 (页寻址模式)
 * @param x 列号 0..127
 * @param y 页号 0..3 (128x32 共 4 页)
 */
void OLED_SetPos(uint8_t x, uint8_t y)
{
    WriteCmd(0xB0 + y);                 /* 页地址 */
    WriteCmd(((x & 0xF0) >> 4) | 0x10); /* 列地址高位 */
    WriteCmd((x & 0x0F) | 0x01);        /* 列地址低位 */
}

/**
 * @brief 全屏填充
 * @param fillData 填充字节 (0x00=黑, 0xFF=全亮)
 */
void OLED_Fill(uint8_t fillData)
{
    uint8_t m, n;
    for (m = 0; m < OLED_PAGES; m++)    /* 遍历 4 页 (128x32) */
    {
        WriteCmd(0xB0 + m);
        WriteCmd(0x00);                 /* 低列起始 0 */
        WriteCmd(0x10);                 /* 高列起始 0 */
        for (n = 0; n < 128; n++)
            WriteDat(fillData);
    }
}

/**
 * @brief 清屏
 */
void OLED_CLS(void)
{
    OLED_Fill(0x00);
}

/**
 * @brief 显示字符串 (6x8, 无自动换行, 由调用者控制布局)
 * @param x 起始列 0..126 (每字符 6px, 最多 21 字符)
 * @param y 起始页 0..3 (每页 8 行像素)
 * @param ch[] 字符串 (ASCII c-32 索引, 需结束符)
 */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[])
{
    uint8_t c = 0, i = 0, j = 0;

    while (ch[j] != '\0')
    {
        c = ch[j] - 32;                 /* 字库索引 = 字符码 - ASCII' ' */
        if (x > 126) break;             /* 超出列宽截断 */
        OLED_SetPos(x, y);
        for (i = 0; i < 6; i++)         /* 每字符 6 列宽 */
            WriteDat(F6x8[c][i]);
        x += 6;
        j++;
    }
}
