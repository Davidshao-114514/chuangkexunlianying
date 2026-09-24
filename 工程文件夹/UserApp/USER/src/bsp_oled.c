#include "bsp_oled.h"

/*******************************************************************************
 * BSP_OLED - SSD1306 OLED 驱动实现
 * 仅包含底层显示原语 (6x8 字符串); 屏幕内容刷新在 main.c 的 UI_* 函数中
 * 移植来源: H563 工程 Core/Src/bsp_oled.c, 底层 IIC 见 bsp_i2c.c
 * 面板切换: bsp_oled.h 的 OLED_PANEL_64
 ******************************************************************************/

/* 毫秒级延时 (48MHz 循环近似) */
/* 精确微秒延时: SysTick 硬件定时 (48MHz), 同 bsp_i2c.c (参考 H563) */
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

/**
 * @brief 写 SSD1306 命令字节
 * @param cmd 命令字节 (协议: D/C=0x00)
 */
uint8_t g_oled_addr = 0x3C;    /* SSD1306 I2C 地址: 自动探测, 默认0x3C */

void WriteCmd(uint8_t cmd)
{
    I2C_WriteData_8bit(g_oled_addr, 0x00, cmd);
}

/**
 * @brief 写 SSD1306 显示数据字节
 * @param dat 数据字节 (协议: D/C=0x40)
 */
void WriteDat(uint8_t dat)
{
    I2C_WriteData_8bit(g_oled_addr, 0x40, dat);
}

/**
 * @brief OLED 初始化
 * 时序要求: 上电后需稳定一段时间; RST 与芯片 NRST 并联, 由系统复位驱动
 */
void OLED_Init(void)
{
    delay_ms(300);                      /* 上电/复位稳定 (200ms+) */

    /* ---- 地址自动探测: 先试 0x3C, 再试 0x3D (默认0x3D的模块常见) ---- */
    if (I2C_Probe(0x3C) == 0)
    {
        if (I2C_Probe(0x3D) == 1)
            g_oled_addr = 0x3D;         /* 模块为 0x3D 地址 */
        else
            g_oled_addr = 0x3C;         /* 两个都无应答: 先用 0x3C (看波形排查硬件) */
    }

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
    WriteCmd(0xA8);                     /* 复用比 (面板相关) */
#if OLED_PANEL_64
    WriteCmd(0x3F);                     /* 0.96": 64 行 (64-1) */
#else
    WriteCmd(0x1F);                     /* 0.91": 32 行 (32-1) */
#endif
    WriteCmd(0xA4);                     /* 跟随 RAM 内容显示 */
    WriteCmd(0xD3);                     /* 显示偏移 */
    WriteCmd(0x00);                     /* 无偏移 */
    WriteCmd(0xD5);                     /* 时钟分频/振荡频率 */
#if OLED_PANEL_64
    WriteCmd(0xF0);                     /* 0.96" 常用 */
#else
    WriteCmd(0x80);                     /* 0.91" 常用: 分频8/1 */
#endif
    WriteCmd(0xD9);                     /* 预充电周期 */
#if OLED_PANEL_64
    WriteCmd(0x22);                     /* 0.96" 常用 */
#else
    WriteCmd(0xF1);                     /* 0.91" 常用: 长预充 */
#endif
    WriteCmd(0xDA);                     /* COM 引脚配置 (面板相关) */
#if OLED_PANEL_64
    WriteCmd(0x12);                     /* 0.96": COM5~COM12 交替 */
#else
    WriteCmd(0x02);                     /* 0.91": 32 行配置 */
#endif
    WriteCmd(0xDB);                     /* VCOMH */
    WriteCmd(0x40);                     /* 0.60xVcc */
    WriteCmd(0x8D);                     /* 电荷泵 */
    WriteCmd(0x14);                     /* 开启 */
    WriteCmd(0xAF);                     /* 开显示 */

    OLED_CLS();                         /* 清除显存; 若此处能整屏点亮则通信正常 */
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
 * @param y 页号 0..OLED_PAGES-1
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
    for (m = 0; m < OLED_PAGES; m++)    /* 遍历全部页 */
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
 * @param y 起始页 0..OLED_PAGES-1 (每页 8 行像素)
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
