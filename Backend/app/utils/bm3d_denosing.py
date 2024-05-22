import os
import uuid

import cv2
from django.conf import settings

from .bm3d_steps import BM3D_1st_step, BM3D_2nd_step
from ..models import Image


def bm3d_denoising(image_id, user):
    try:
        original_image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return None

    # 使用OpenCV读取图像（不转换为灰度图）
    original_image_path = original_image.image_file.path
    original_img = cv2.imread(original_image_path)  # 删除cv2.IMREAD_GRAYSCALE

    if original_img is None:
        return None

    # 分离颜色通道
    channels = cv2.split(original_img)
    denoised_channels = []

    # 对每个通道使用BM3D算法处理图像
    for channel in channels:
        basic_img = BM3D_1st_step(channel)
        final_img = BM3D_2nd_step(basic_img, channel)
        denoised_channels.append(final_img)

    # 合并处理后的通道
    denoised_img = cv2.merge(denoised_channels)

    # 保存降噪后的图像
    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)  # 保存彩色图像

    # 在Django中创建新的Image对象
    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )

    # 构建响应，返回处理后的图像的URL
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
    return denoised_image_url
