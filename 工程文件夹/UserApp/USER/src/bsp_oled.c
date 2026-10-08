#include "bsp_oled.h"

/*******************************************************************************
 * BSP_OLED - 0.5" 88x48 OLED (CH1115) 驱动实现
 * 仅包含底层显示原语 (6x8 字符串); 屏幕内容刷新在 main.c 的 UI_* 函数中
 * CH1115 指令集与 SSD1306 兼容, 差异: 增加 0xAD(IREF) 命令, MUX=0x2F(48行)
 ******************************************************************************/

/* 精确微秒延时: SysTick 硬件定时 (48MHz), 同 bsp_i2c.c */
static void delay_us(uint32_t n)
{
    uint32_t temp;

    SysTick->LOAD = n * 48U - 30U;
    SysTick->VAL  = 0x00;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;
    do
    {
        temp = SysTick->CTRL;
    } while ((temp & SysTick_CTRL_ENABLE_Msk) && !(temp & SysTick_CTRL_COUNTFLAG_Msk));
    SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;
    SysTick->VAL  = 0x00;
}

static void delay_ms(uint32_t n)
{
    while (n--)
        delay_us(1000);
}

uint8_t g_oled_addr = 0x3C;    /* CH1115 I2C 地址: 自动探测, 默认0x3C */

/**
 * @brief 写命令字节 (协议: D/C=0x00)
 */
void WriteCmd(uint8_t cmd)
{
    I2C_WriteData_8bit(g_oled_addr, 0x00, cmd);
}

/**
 * @brief 写显示数据字节 (协议: D/C=0x40)
 */
void WriteDat(uint8_t dat)
{
    I2C_WriteData_8bit(g_oled_addr, 0x40, dat);
}

/**
 * @brief OLED 初始化 (CH1115, 88x48)
 * 时序要求: 上电后需稳定一段时间; RST 与芯片 NRST 并联由系统复位驱动
 */
void OLED_Init(void)
{
    delay_ms(200);                      /* 上电稳定 (CH1115 要求 VCC 稳定后再初始化) */

    /* ---- 地址自动探测: 0x3C ~ 0x3F ---- */
    {
        uint8_t addrs[4] = { 0x3C, 0x3D, 0x3E, 0x3F };
        uint8_t i;
        uint8_t found = 0;

        for (i = 0; i < 4U; i++)
        {
            if (I2C_Probe(addrs[i]))
            {
                g_oled_addr = addrs[i];
                found = 1;
                break;
            }
        }
        if (!found)
            g_oled_addr = 0x3C;         /* 都无应答: 保持 0x3C (通信问题) */
    }

    /* ---- CH1115 初始化序列 (厂商官方 C51 驱动, 0.50" 88x48 I2C) ----
     * 来源: 商家资料 0.50iicc51 88x48.c (宽排14P/窄排14P/4针模组通用)
     * 注意: 官方使用 A0/C0 (方向) 与 D3=0x38 (显示偏移), 列地址从 0 起 */
    WriteCmd(0xAE);                     /* display off */
    WriteCmd(0x00);                     /* set lower column address */
    WriteCmd(0x10);                     /* set higher column address */
    WriteCmd(0x40);                     /* set display start line */
    WriteCmd(0xB0);                     /* set page address */
    WriteCmd(0x81);                     /* contract control */
    WriteCmd(0x80);                     /* 对比度 0x80 (默认) */
    WriteCmd(0x82);                     /* IREF 内置 */
    WriteCmd(0x00);
    WriteCmd(0x23);
    WriteCmd(0x01);
    WriteCmd(0xA0);                     /* set segment remap */
    WriteCmd(0xA2);
    WriteCmd(0xA4);
    WriteCmd(0xA6);                     /* normal / reverse */
    WriteCmd(0xA8);                     /* multiplex ratio */
    WriteCmd(0x2F);                     /* duty (48 行) */
    WriteCmd(0xC0);                     /* Com scan direction */
    WriteCmd(0xD3);                     /* set display offset */
    WriteCmd(0x38);                     /* 0x38 (官方值) */
    WriteCmd(0xD5);                     /* set osc division */
    WriteCmd(0x50);
    WriteCmd(0xD9);                     /* set pre-charge period */
    WriteCmd(0x22);
    WriteCmd(0xDB);                     /* set vcomh */
    WriteCmd(0x35);
    WriteCmd(0xAD);                     /* set charge pump enable */
    WriteCmd(0x8B);
    WriteCmd(0x33);                     /* 9V */
    WriteCmd(0xAF);                     /* display ON */

    OLED_CLS();                         /* 清除显存 (无开机动画) */
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
 * @param x 列号 0..87
 * @param y 页号 0..5 (88x48 共 6 页)
 */
void OLED_SetPos(uint8_t x, uint8_t y)
{
    uint16_t col = (uint16_t)x + OLED_COL_OFFSET;   /* 88 列窗口 -> 40..127 */

    WriteCmd(0xB0 + y);                             /* 页地址 */
    WriteCmd((uint8_t)(((col & 0xF0) >> 4) | 0x10));/* 列地址高位 */
    WriteCmd((uint8_t)((col & 0x0F) | 0x00));       /* 列地址低位 */
}

/**
 * @brief 全屏填充
 * @param fillData 填充字节 (0x00=黑, 0xFF=全亮)
 */
void OLED_Fill(uint8_t fillData)
{
    uint8_t m, n;

    for (m = 0; m < OLED_PAGES; m++)    /* 遍历 6 页 (88x48) */
    {
        WriteCmd(0xB0 + m);
        WriteCmd((uint8_t)(((OLED_COL_OFFSET & 0xF0) >> 4) | 0x10));    /* 高列起始 */
        WriteCmd((uint8_t)((OLED_COL_OFFSET & 0x0F) | 0x00));           /* 低列起始 */
        for (n = 0; n < OLED_WIDTH; n++)
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
 * @param x 起始列 0..(OLED_WIDTH-6)
 * @param y 起始页 0..5 (每页 8 行像素)
 * @param ch[] 字符串 (ASCII c-32 索引, 需结束符)
 */
void OLED_ShowStr(uint8_t x, uint8_t y, uint8_t ch[])
{
    uint8_t c = 0, i = 0, j = 0;

    while (ch[j] != '\0')
    {
        c = ch[j] - 32;                 /* 字库索引 = 字符码 - ASCII' ' */
        if (c >= 92U)                   /* 字库仅 92 行('|' 及以后无字形): 越界保护 */
            c = 0U;                     /* 按空格显示, 防止读到乱数据 */
        if (x > (OLED_WIDTH - 6U))      /* 超出列宽截断 */
            break;
        OLED_SetPos(x, y);
        for (i = 0; i < 6; i++)         /* 每字符 6 列宽 */
            WriteDat(F6x8[c][i]);
        x += 6;
        j++;
    }
}
