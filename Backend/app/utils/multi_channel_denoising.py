import os
import uuid
import cv2
import numpy as np
import bm3d
import pywt
from django.conf import settings
from ..models import Image


# 多通道联合分析降噪函数
def multi_channel_denoising(image_id, user, method):
    try:
        # 从数据库中根据图片ID获取图片对象
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        # 图片不存在则返回None
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    # 使用OpenCV读取图片，cv2.IMREAD_COLOR确保图像通道数为3
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    # 如果图片未能正确加载，则返回None
    if original_img is None:
        return None

    # 确保图片是三通道的
    if original_img.ndim == 3:
        # 将图像从BGR转换到YCrCb颜色空间
        img_y_cr_cb = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCrCb)
        # 分离出三个颜色通道
        channels = cv2.split(img_y_cr_cb)
        result_channels = []

        if method == "0":
            # 使用BM3D算法进行去噪
            sigma_est = 25  # 噪声估计
            bm3d_kwargs = {'sigma_psd': sigma_est, 'stage_arg': bm3d.BM3DStages.ALL_STAGES}
            for channel in channels:
                denoised_channel = bm3d.bm3d(channel, **bm3d_kwargs)
                denoised_channel = np.clip(denoised_channel, 0, 255).astype(np.uint8)
                result_channels.append(denoised_channel)
        elif method == "1":
            # 中值滤波
            kernel_size = 5  # 核大小,根据噪声程度调整
            for channel in channels:
                denoised_channel = cv2.medianBlur(channel, kernel_size)
                result_channels.append(denoised_channel)
        elif method == "2":
            # 高斯模糊
            kernel_size = (7, 7)  # 核大小
            sigma = 1.5  # 标准差根据噪声程度调整
            for channel in channels:
                denoised_channel = cv2.GaussianBlur(channel, kernel_size, sigma)
                result_channels.append(denoised_channel)
        elif method == "3":
            # 非局部均值去噪
            strength = 15  # 强度参数，根据噪声程度调整
            search_window = 21  # 搜索窗口大小，影响去噪效果和计算时间
            for channel in channels:
                denoised_channel = cv2.fastNlMeansDenoising(channel, None, strength, 7, search_window)
                result_channels.append(denoised_channel)
        elif method == "4":
            # 小波变换去噪
            wavelet = 'db1'  # 使用Daubechies小波
            mode = 'soft'  # 使用软阈值
            level = 2  # 小波分解的级别
            for channel in channels:
                # 多级小波分解
                coeffs = pywt.wavedec2(channel, wavelet, level=level)
                threshold = 2 * pywt.threshold_sigma(coeffs[-1])
                # 阈值处理
                coeffs = list(map(lambda x: pywt.threshold(x, threshold, mode=mode), coeffs))
                # 重构图像
                denoised_channel = pywt.waverec2(coeffs, wavelet)
                denoised_channel = np.clip(denoised_channel, 0, 255).astype(np.uint8)
                result_channels.append(denoised_channel)
        # 合并处理后的通道并将颜色空间从YCrCb转回BGR
        denoised_img_y_cr_cb = cv2.merge(result_channels)
        final_denoised_img = cv2.cvtColor(denoised_img_y_cr_cb, cv2.COLOR_YCrCb2BGR)

        # 生成唯一的文件名
        unique_filename = f'{uuid.uuid4().hex}.png'
        # 保存去噪后的图像到指定路径
        denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
        cv2.imwrite(denoised_image_path, final_denoised_img)

        # 在数据库中创建新的图片对象
        denoised_image = Image.objects.create(
            uploader=user,
            image_name=unique_filename,
            image_file=f'images/{unique_filename}',
        )

        # 构建响应，返回处理后的图片的HTTP地址
        denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
        return denoised_image_url

    return None
