#ifndef __OLED_TEXT_H
#define __OLED_TEXT_H

/* 字库点阵均为只读数据 -> const 放入 Flash, 节省 4KB RAM */
extern const unsigned char F6x8[][6];
extern const unsigned char F8X16[];
extern const unsigned char F16x16[];

#endif
