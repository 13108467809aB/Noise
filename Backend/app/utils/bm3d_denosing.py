import os
import uuid

import cv2
import numpy as np
import pybm3d
from django.conf import settings

from ..models import Image


def bm3d_denoising(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    # 如果是彩色图像，拆分为三个通道
    if len(original_img.shape) == 3:
        channels = cv2.split(original_img)
    else:
        channels = [original_img]

    denoised_channels = []

    # 对每个通道分别进行BM3D降噪处理
    for channel in channels:
        denoised_channel = pybm3d.bm3d(channel, sigma_psd=25/255.0)  # sigma_psd 参数需要根据图像噪声水平调整
        denoised_channels.append(denoised_channel)

    # 合并处理后的通道
    if len(denoised_channels) == 3:
        denoised_img = cv2.merge(denoised_channels)
    else:
        denoised_img = denoised_channels[0]

    # 生成新的文件名，避免命名冲突
    unique_filename = f'{uuid.uuid4().hex}.png'

    # 保存降噪后的图像到media文件夹中
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, np.uint8(denoised_img * 255))

    # 创建新的图片对象，并与用户关联
    denoised_image = Image.objects.create(
        uploader=user,  # 将图像与用户关联
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',  # 更新文件路径
    )

    # 构建响应，返回处理后的图片的HTTP地址
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return denoised_image_url
