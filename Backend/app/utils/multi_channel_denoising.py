import os
import uuid

import cv2
import numpy as np
import pywt
from django.conf import settings

from ..models import Image


def multi_channel_denoising(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    # 将图像转换为浮点型
    original_img = original_img.astype(np.float32)

    # 获取图像的通道数
    channels = cv2.split(original_img)

    # 对每个通道进行小波变换降噪
    denoised_channels = []
    for channel in channels:
        # 执行小波变换
        coeffs2 = pywt.dwt2(channel, 'haar')

        # 对小波系数进行降噪处理
        threshold = 20  # 设定阈值，根据实际情况调整
        coeffs2 = tuple(pywt.threshold(c, threshold, mode='soft') for c in coeffs2)

        # 重构通道
        denoised_channel = pywt.idwt2(coeffs2, 'haar')

        # 添加到降噪后的通道列表中
        denoised_channels.append(denoised_channel)

    # 合并降噪后的通道
    denoised_img = cv2.merge(denoised_channels)

    # 生成新的文件名，避免命名冲突
    unique_filename = f'{uuid.uuid4().hex}.png'

    # 保存降噪后的图像到media文件夹中
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    # 创建新的图片对象，并与用户关联
    denoised_image = Image.objects.create(
        uploader=user,  # 将图像与用户关联
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',  # 更新文件路径
    )

    # 构建响应，返回处理后的图片的HTTP地址
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return denoised_image_url
