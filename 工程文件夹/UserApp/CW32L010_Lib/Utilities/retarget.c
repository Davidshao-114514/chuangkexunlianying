/*  retarget.c  -----------------------------------------------------------
 *  一次编写，同时兼容
 *  Keil MDK : AC5  + AC6
 *  库       : MicroLib / standard lib
 *  功能     : printf/puts 映射到任意串口
 *  使用方法 :  __retarget_putchar() 实现自己的发送函数
 *------------------------------------------------------------------------*/
#include "stdio.h"
#include "cw32l010.h"

/* =============== 1. 关闭半主机模式 ================= */
#if !defined(__MICROLIB)          /* 若使用 MicroLib，Keil 会自动处理，以下不需要 */
/* AC6 不再支持 #pragma import(...) 语法，改用汇编声明 */
#if defined (__ARMCC_VERSION) && (__ARMCC_VERSION >= 6010050)
__asm(".global __use_no_semihosting\n\t");
__asm(".global __ARM_use_no_argv\n\t");   /* 避免链接 _sys_command_string */
#else                                  /* AC5 */
#pragma import(__use_no_semihosting)
#endif

/* 必须提供的三个“空”函数，否则链接报错 */
void _sys_exit(int x)
{
    (void)x;
}
void _ttywrch(int ch)
{
    (void)ch;
}
char *_sys_command_string(char *cmd, int len)
{
    return NULL;
}

/* 标准库需要 FILE * 句柄 */
#if !defined(__ARMCC_VERSION) || (__ARMCC_VERSION < 6010050)
struct __FILE
{
    int handle;
};   /* AC5 需要 */
#endif
FILE __stdout;
#endif   /* !__MICROLIB */

/* =============== 2. 统一 putchar 入口 ================= */
__WEAK int __retarget_putchar(int ch)
{
    /* 用户 TODO：改成自己的发送函数，下面用 HAL 举例 */
    
    return ch;
}

/* =============== 3. 根据编译器选择重定向方式 ======== */
#if defined (__MICROLIB)                 /* ----------- MicroLib 路径 ------------ */
/* MicroLib 只认 fputc/fgetc */
int fputc(int ch, FILE *f)
{
    return __retarget_putchar(ch);
}
int fgetc(FILE *f)        /* 如需 scanf，一并实现 */
{
    /* 用户可在此处补接收代码 */
    return 0;
}

#else                                    /* ------- 标准库路径（AC5/AC6 均走这里） -- */
/* AC6 使用 clang 前端，优先用 __io_putchar；AC5 用 fputc */
#if defined(__ARMCC_VERSION) && (__ARMCC_VERSION >= 6010050) && defined(__clang__)
int __io_putchar(int ch)           /* AC6 + standard lib */
{
    return __retarget_putchar(ch);
}
#else                              /* AC5 + standard lib */
int fputc(int ch, FILE *f)
{
    return __retarget_putchar(ch);
}
#endif
#endif  /* __MICROLIB */
