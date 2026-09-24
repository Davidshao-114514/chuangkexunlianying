#ifndef __BSP_I2C_H
#define __BSP_I2C_H

#include "cw32l010.h"

/* 软件 I2C 驱动, 参考 H563 工程 bsp_i2c (LL 版) 移植到 CW32L010
 * 引脚: SCL = PB06, SDA = PB05 (见 bsp_pin.h) */

#define I2C_Delay()          delay_us(5)      /* 约 100kHz */

uint8_t I2C_WriteData_8bit(uint8_t Addr, uint8_t Reg, uint8_t Data);
uint8_t I2C_WriteData(uint8_t Addr, uint8_t Reg, uint16_t Data);
uint8_t I2C_ReadData(uint8_t Addr, uint8_t Reg, uint8_t *pdata);

void I2C_GPIO_Init(void);
uint8_t I2C_Probe(uint8_t addr7);   /* 探测7位地址: 返回1=找到(有ACK), 0=未找到 */

#endif /* __BSP_I2C_H */
