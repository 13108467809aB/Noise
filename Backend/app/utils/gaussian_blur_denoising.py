import os
import uuid
import cv2
import numpy as np
from django.conf import settings
from ..models import Image

def gaussian_blur_denoising(image_id, user):
    try:
        # 从数据库获取原始图像
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        # 如果图像不存在，返回None
        return None

    # 获取图像文件的路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    # 加载图像，保留彩色信息
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    if original_img is None:
        # 如果图像未成功加载，返回None
        return None

    # 应用高斯滤波去噪
    # 可调整高斯核的大小和标准差来改变滤波效果
    kernel_size = (3, 3)
    sigma = 0.5
    denoised_img = cv2.GaussianBlur(original_img, kernel_size, sigma)

    # 保存降噪后的图像
    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    # 在数据库中创建新的图像记录
    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )

    # 构建并返回新图像的URL
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
    return denoised_image_url
