import os
import uuid

import cv2
import numpy as np
from django.conf import settings

from ..models import Image


def add_gaussian_noise(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    # 添加高斯噪声
    mean = 0
    sigma = 25
    gauss = np.random.normal(mean, sigma, original_img.shape)
    noisy_img = original_img + gauss

    # 生成新的文件名，避免命名冲突
    unique_filename = f'{uuid.uuid4().hex}.png'

    # 保存加噪后的图像到media文件夹中
    noisy_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(noisy_image_path, noisy_img)

    # 创建新的图片对象，并与用户关联
    noisy_image = Image.objects.create(
        uploader=user,  # 将图像与用户关联
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',  # 更新文件路径
    )

    # 构建响应，返回处理后的图片的HTTP地址
    noisy_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return noisy_image_url
