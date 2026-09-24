#include "bsp_oled.h"

/*******************************************************************************
 * BSP_OLED - 0.91" 128x64 OLED (SSD1306) 驱动实现
 * 说明: 仅包含底层显示原语; 屏幕内容刷新在 main.c 的 UI_* 函数中
 * 移植来源: H563 工程 Core/Src/bsp_oled.c, 底层 IIC 见 bsp_i2c.c
 ******************************************************************************/

/* 毫秒级延时 (48MHz 循环近似, 仅在初始化/显示较慢场合使用) */
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
 * @brief OLED 初始化
 * 时序要求: 上电后需稳定一段时间 (本板 OLED RST 与芯片 NRST 接在一起,
 *           由系统复位驱动, 无需 GPIO 控制复位线)
 */
void OLED_Init(void)
{
    delay_ms(100);                      /* 上电/复位稳定 */

    WriteCmd(0xAE);                     /* 关显示 (初始化期间屏幕保持关闭) */
    WriteCmd(0x20);                     /* 设置内存寻址模式 */
    WriteCmd(0x10);                     /* 页寻址模式 (RESET: 页寻址) */
    WriteCmd(0xB0);                     /* 页起始地址 0 */
    WriteCmd(0xC8);                     /* COM 扫描方向 (自上而下) */
    WriteCmd(0x00);                     /* 低列地址 */
    WriteCmd(0x10);                     /* 高列地址 */
    WriteCmd(0x40);                     /* 起始行地址 */
    WriteCmd(0x81);                     /* 对比度控制器 */
    WriteCmd(0xFF);                     /* 对比度 0x00~0xFF, 0xFF=最亮 */
    WriteCmd(0xA1);                     /* 段重映射 (127 到 0) */
    WriteCmd(0xA6);                     /* 正常显示 (0xA7 反色) */
    WriteCmd(0xA8);                     /* 复用比 */
    WriteCmd(0x3F);                     /* 1~64 (128x64 屏须为 0x3F) */
    WriteCmd(0xA4);                     /* 跟随 RAM 内容显示 */
    WriteCmd(0xD3);                     /* 显示偏移 */
    WriteCmd(0x00);                     /* 无偏移 */
    WriteCmd(0xD5);                     /* 时钟分频/振荡频率 */
    WriteCmd(0xF0);                     /* 分频比 1, 频率默认 */
    WriteCmd(0xD9);                     /* 预充电周期 */
    WriteCmd(0x22);                     /* 第一相位 1时钟, 第二相位 2时钟 */
    WriteCmd(0xDA);                     /* COM 引脚硬件配置 */
    WriteCmd(0x12);                     /* 64行: COM 交替 */
    WriteCmd(0xDB);                     /* VCOMH 电平 */
    WriteCmd(0x20);                     /* 0.77 x VCC */
    WriteCmd(0x8D);                     /* 电荷泵设置 */
    WriteCmd(0x14);                     /* 开启电荷泵 (必须, 否则黑屏) */
    WriteCmd(0xAF);                     /* 开显示 */

    OLED_CLS();                         /* 清除显存 */
}

/**
 * @brief 开启显示
 */
void OLED_ON(void)
{
    WriteCmd(0x8D);                     /* 电荷泵设置 */
    WriteCmd(0x14);                     /* 开充电泵 */
    WriteCmd(0xAF);                     /* 开显示 */
}

/**
 * @brief 关闭显示
 */
void OLED_OFF(void)
{
    WriteCmd(0x8D);                     /* 电荷泵设置 */
    WriteCmd(0x10);                     /* 关充电泵 */
    WriteCmd(0xAE);                     /* 关显示 */
}

/**
 * @brief 显存光标定位 (页寻址模式)
 * @param x 列号 0..127
 * @param y 页号 0..7 (每页 8 行像素, 64/8=8 页)
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
    for (m = 0; m < 8; m++)             /* 遍历 8 页 */
    {
        WriteCmd(0xB0 + m);             /* 页起始 */
        WriteCmd(0x00);                 /* 低列起始 0 */
        WriteCmd(0x10);                 /* 高列起始 0 */
        for (n = 0; n < 128; n++)
            WriteDat(fillData);         /* 整页 128 列 */
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
 * @brief 显示字符串
 * @param x 起始列 0..127
 * @param y 起始页 0..7
 * @param ch[] 字符串 (ASCII, 已加结束符)
 * @param textSize 1=6x8(每页一行), 2=8x16(占两页)
 */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[], uint8_t textSize)
{
    uint8_t c = 0, i = 0, j = 0;

    switch (textSize)
    {
    case 1:                             /* ---------- 6x8 字体 ---------- */
        while (ch[j] != '\0')
        {
            c = ch[j] - 32;             /* 字库索引 = 字符码 - ASCII' ' */
            if (x > 126)                /* 换行保护 */
            {
                x = 0;
                y++;
                if (y > 7) y = 7;       /* 超出屏幕底部 */
            }
            OLED_SetPos(x, y);
            for (i = 0; i < 6; i++)     /* 每字符 6 列宽 */
                WriteDat(F6x8[c][i]);
            x += 6;
            j++;
        }
        break;

    case 2:                             /* ---------- 8x16 字体 ---------- */
        while (ch[j] != '\0')
        {
            c = ch[j] - 32;
            if (x > 120)                /* 换行保护 */
            {
                x = 0;
                y += 2;                 /* 16px 高占两页 */
                if (y > 6) y = 6;
            }
            OLED_SetPos(x, y);          /* 上半字节 (高 8 行) */
            for (i = 0; i < 8; i++)
                WriteDat(F8X16[c * 16 + i]);
            OLED_SetPos(x, y + 1);      /* 下半字节 (低 8 行) */
            for (i = 0; i < 8; i++)
                WriteDat(F8X16[c * 16 + i + 8]);
            x += 8;
            j++;
        }
        break;

    default:
        break;
    }
}

/**
 * @brief 显示无符号十进制数 (5 位, 高位补空格), 固定宽度便于界面刷新
 * @param x 起始列 0..127
 * @param y 起始页 0..7
 * @param v 数值 0..99999
 * @param textSize 1=6x8, 2=8x16
 */
void OLED_ShowU16(uint8_t x, uint8_t y, uint16_t v, uint8_t textSize)
{
    uint8_t buf[6] = { ' ', ' ', ' ', ' ', ' ', '\0' };
    uint16_t d = 10000;
    uint8_t i = 0;

    while (d != 0)
    {
        buf[i++] = (uint8_t)('0' + (v / d) % 10);   /* 逐位取数 */
        d /= 10;
    }
    OLED_ShowStr(x, y, buf, textSize);
}

/**
 * @brief 显示 16x16 中文点阵
 * @param x 起始列 0..127
 * @param y 起始页 0..7 (通常为偶页)
 * @param n 点阵索引 (见 bsp_oled_text.c F16x16, n<8)
 */
void OLED_ShowCN(uint8_t x, uint8_t y, uint8_t n)
{
    uint8_t wm;
    uint16_t adder = 32 * n;            /* 每个汉字 16x16 = 32 字节 */

    OLED_SetPos(x, y);                  /* 上半部 16 字节 */
    for (wm = 0; wm < 16; wm++)
        WriteDat(F16x16[adder++]);
    OLED_SetPos(x, y + 1);              /* 下半部 16 字节 */
    for (wm = 0; wm < 16; wm++)
        WriteDat(F16x16[adder++]);
}

/**
 * @brief 显示位图 (逐页按行方向写入)
 * @param x0 起始列 0..127
 * @param y0 起始页 0..7
 * @param x1 结束列 (1..128)
 * @param y1 结束页 (1..8)
 * @param bmp[] 位图数据, 按 y0~y1 页、每页 x1-x0 列排列
 */
void OLED_DrawBMP(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1, uint8_t bmp[])
{
    uint16_t j = 0;
    uint8_t x, y;

    y = (y1 % 8 == 0) ? y1 / 8 : y1 / 8 + 1;   /* 页数补齐 */
    for (; y < y1; y++)                         /* 逐页显示 */
    {
        OLED_SetPos(x0, y);
        for (x = x0; x < x1; x++)               /* 该页逐列显示 */
            WriteDat(bmp[j++]);
    }
}
