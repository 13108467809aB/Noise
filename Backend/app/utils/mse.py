import numpy as np


def calculate_mse(image_a, image_b):
    """
    计算两幅图像之间的均方误差（MSE）
    """
    # 将图像转换为float类型以防止数据溢出
    img1 = np.float32(image_a)
    img2 = np.float32(image_b)
    mse = np.mean((img1 - img2) ** 2)
    return mse
