#ifndef __APP_CONFIG_H
#define __APP_CONFIG_H

/*******************************************************************************
 * APP_CONFIG - 产品型号配置 (软件开关)
 *
 * [外挂款 PRODUCT_VARIANT_EXTERNAL]
 *   LED 为磁吸 4pin 外挂 (3V3/GND/LED-/DET), 使用吸附检测:
 *   PA01(OSC-) 检测组1, PA00(OSC+) 检测组2; 高电平=已吸附, 未吸附不输出
 *   按键: 5 个 (PA02 PA04 PA05 PA06 PB03)
 *
 * [内置款 PRODUCT_VARIANT_BUILTIN]
 *   LED 内置于整机, 无需检测: PA00/PA01 复位为普通按键
 *   按键: 7 个 (PA00 PA01 PA02 PA04 PA05 PA06 PB03)
 *
 * 烧录方法: 修改下方 APP_PRODUCT_VARIANT, 重新编译烧录即可
 ******************************************************************************/

#define PRODUCT_VARIANT_EXTERNAL     0   /* 外挂款: 磁吸外接 LED + 吸附检测 */
#define PRODUCT_VARIANT_BUILTIN      1   /* 内置款: 内置 LED, 无需检测 */

/* <------- 烧录前修改这里 -------> */
#define APP_PRODUCT_VARIANT          PRODUCT_VARIANT_BUILTIN
/* <--------------------------------> */

#if (APP_PRODUCT_VARIANT == PRODUCT_VARIANT_EXTERNAL)
#define BSP_DETECT_ENABLED           1   /* 启用磁吸吸附检测 (占用 PA00/PA01) */
#else
#define BSP_DETECT_ENABLED           0   /* 关闭检测 (PA00/PA01 作按键) */
#endif

#endif /* __APP_CONFIG_H */
