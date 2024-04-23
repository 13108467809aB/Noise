import os
import uuid

import cv2
import numpy as np
from django.conf import settings

from ..models import Image


def add_motion_blur_noise(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    # 添加运动模糊噪声
    size = 15  # 模糊核大小
    angle = np.random.uniform(low=0, high=180)  # 随机生成模糊方向
    kernel = np.zeros((size, size), dtype=np.float32)
    kernel[int((size - 1) / 2), :] = np.ones(size, dtype=np.float32) / size
    motion_blur = cv2.warpAffine(original_img, cv2.getRotationMatrix2D((size // 2, size // 2), angle, 1.0), (size, size))
    motion_blur = cv2.filter2D(original_img, -1, kernel)

    # 生成新的文件名，避免命名冲突
    unique_filename = f'{uuid.uuid4().hex}.png'

    # 保存加噪后的图像到media文件夹中
    noisy_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(noisy_image_path, motion_blur)

    # 创建新的图片对象，并与用户关联
    noisy_image = Image.objects.create(
        uploader=user,  # 将图像与用户关联
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',  # 更新文件路径
    )

    # 构建响应，返回处理后的图片的HTTP地址
    noisy_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return noisy_image_url

