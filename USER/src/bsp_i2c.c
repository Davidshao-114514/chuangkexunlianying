#include "bsp_i2c.h"
#include "bsp_pin.h"
#include "cw32l010_sysctrl.h"

static void delay_us(uint32_t n)
{
    /* 48MHz 系统时钟下的粗延时, 每 us 约 48 个循环 */
    uint32_t cnt = n * 48;
    while (cnt--);
}

/* SDA 引脚模式切换 */
static void I2C_SDA_In(void)
{
    GPIO_InitTypeDef s = {0};
    s.Pins = OLED_SDA_PIN;
    s.Mode = GPIO_MODE_INPUT_PULLUP;   /* 读总线时依赖板上拉/内部上拉 */
    s.IT   = GPIO_IT_NONE;
    GPIO_Init((GPIO_TypeDef *)OLED_SDA_PORT, &s);
}

static void I2C_SDA_Out(void)
{
    GPIO_InitTypeDef s = {0};
    s.Pins = OLED_SDA_PIN;
    s.Mode = GPIO_MODE_OUTPUT_OD;
    s.IT   = GPIO_IT_NONE;
    GPIO_Init((GPIO_TypeDef *)OLED_SDA_PORT, &s);
}

#define I2C_SCL_H()   (OLED_SCL_PORT->BSRR = OLED_SCL_PIN)
#define I2C_SCL_L()   (OLED_SCL_PORT->BRR  = OLED_SCL_PIN)
#define I2C_SDA_H()   (OLED_SDA_PORT->BSRR = OLED_SDA_PIN)
#define I2C_SDA_L()   (OLED_SDA_PORT->BRR  = OLED_SDA_PIN)
#define I2C_SDA_Read() ((OLED_SDA_PORT->IDR & OLED_SDA_PIN) != 0)

void I2C_GPIO_Init(void)
{
    GPIO_InitTypeDef s = {0};

    __SYSCTRL_GPIOA_CLK_ENABLE();
    __SYSCTRL_GPIOB_CLK_ENABLE();

    /* 保持 GPIO 功能 (AF=0) */
    PB05_AFx_GPIO();
    PB06_AFx_GPIO();

    /* SCL 输出开漏 */
    s.Pins = OLED_SCL_PIN;
    s.Mode = GPIO_MODE_OUTPUT_OD;
    s.IT   = GPIO_IT_NONE;
    GPIO_Init(CW_GPIOB, &s);

    /* SDA 输出开漏 */
    s.Pins = OLED_SDA_PIN;
    s.Mode = GPIO_MODE_OUTPUT_OD;
    s.IT   = GPIO_IT_NONE;
    GPIO_Init(CW_GPIOB, &s);

    I2C_SCL_H();
    I2C_SDA_H();
}

static void I2C_Start(void)
{
    I2C_SDA_Out();
    I2C_SDA_H();
    I2C_SCL_H();
    I2C_Delay();
    I2C_SDA_L();
    I2C_Delay();
    I2C_SCL_L();
    I2C_Delay();
}

static void I2C_Stop(void)
{
    I2C_SDA_Out();
    I2C_SCL_L();
    I2C_SDA_L();
    I2C_Delay();
    I2C_SCL_H();
    I2C_Delay();
    I2C_SDA_H();
    I2C_Delay();
}

static uint8_t I2C_WaitAck(void)
{
    uint16_t timeOut = 5000;
    I2C_SDA_H();
    I2C_SDA_In();
    I2C_SCL_H();
    I2C_Delay();
    while (I2C_SDA_Read())
    {
        if (--timeOut == 0)
        {
            I2C_Stop();
            return 1;
        }
    }
    I2C_SCL_L();
    I2C_Delay();
    return 0;
}

static void I2C_Ack(void)
{
    I2C_SDA_Out();
    I2C_SDA_L();
    I2C_Delay();
    I2C_SCL_H();
    I2C_Delay();
    I2C_SCL_L();
    I2C_Delay();
}

static void I2C_NAck(void)
{
    I2C_SDA_Out();
    I2C_SDA_H();
    I2C_Delay();
    I2C_SCL_H();
    I2C_Delay();
    I2C_SCL_L();
    I2C_Delay();
}

static void I2C_WriteBit(uint8_t data)
{
    uint8_t i;
    I2C_SDA_Out();
    I2C_SCL_L();
    for (i = 0; i < 8; i++)
    {
        if (data & 0x80)
            I2C_SDA_H();
        else
            I2C_SDA_L();
        data <<= 1;
        I2C_Delay();
        I2C_SCL_H();
        I2C_Delay();
        I2C_SCL_L();
        I2C_Delay();
    }
}

static uint8_t I2C_ReadBit(void)
{
    uint8_t i, data = 0;
    I2C_SDA_In();
    for (i = 0; i < 8; i++)
    {
        I2C_SCL_L();
        I2C_Delay();
        I2C_SCL_H();
        data <<= 1;
        if (I2C_SDA_Read())
            data++;
        I2C_Delay();
    }
    I2C_SCL_L();
    return data;
}

uint8_t I2C_WriteData_8bit(uint8_t addr, uint8_t reg, uint8_t data)
{
    I2C_Start();
    I2C_WriteBit(addr << 1);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit(reg);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit(data);
    if (I2C_WaitAck()) return 1;
    I2C_Stop();
    return 0;
}

uint8_t I2C_WriteData(uint8_t addr, uint8_t reg, uint16_t data)
{
    I2C_Start();
    I2C_WriteBit(addr << 1);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit(reg);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit((data >> 8) & 0xFF);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit(data & 0xFF);
    if (I2C_WaitAck()) return 1;
    I2C_Stop();
    return 0;
}

uint8_t I2C_ReadData(uint8_t addr, uint8_t reg, uint8_t *pdata)
{
    I2C_Start();
    I2C_WriteBit(addr << 1);
    if (I2C_WaitAck()) return 1;
    I2C_WriteBit(reg);
    if (I2C_WaitAck()) return 1;

    I2C_Start();
    I2C_WriteBit((addr << 1) + 1);
    if (I2C_WaitAck()) return 1;

    pdata[0] = I2C_ReadBit();
    I2C_Ack();
    pdata[1] = I2C_ReadBit();
    I2C_NAck();
    I2C_Stop();
    return 0;
}
