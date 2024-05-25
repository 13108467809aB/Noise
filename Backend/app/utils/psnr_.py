import numpy as np
import math


def calculate_psnr(image_a, image_b):
    """
    计算两幅图像之间的峰值信噪比（PSNR）。
    这个函数不调用外部的 calculate_mse 函数，直接在内部计算 MSE。
    """
    # 将图像数据转换为 float 类型，以防止溢出
    img1 = np.float32(image_a)
    img2 = np.float32(image_b)
    # 计算 MSE
    mse = np.mean((img1 - img2) ** 2)

    # 如果 MSE 为零，则 PSNR 是无穷大
    if mse == 0:
        return float('inf')

    # 定义图像可能的最大像素值
    max_pixel = 255.0
    # 计算 PSNR
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr
