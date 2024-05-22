import os
import uuid
import cv2
import numpy as np
from django.conf import settings
from skimage.restoration import denoise_tv_chambolle  # 引入TV降噪函数
from ..models import Image

def total_variation_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)  # 确保总是读取彩色图像

    if original_img is None:
        return None

    # 彩色图像降噪
    if original_img.ndim == 3:
        # 将图像转换为float类型，范围0-1
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB) / 255.0
        denoised_img = denoise_tv_chambolle(original_img, weight=0.1)  # 移除multichannel参数
        # 将图像转换回0-255范围并转为uint8
        denoised_img = (denoised_img * 255).astype(np.uint8)
        denoised_img = cv2.cvtColor(denoised_img, cv2.COLOR_RGB2BGR)
    else:
        # 对于灰度图像也适用
        original_img = original_img / 255.0
        denoised_img = denoise_tv_chambolle(original_img, weight=0.1)
        denoised_img = (denoised_img * 255).astype(np.uint8)

    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return denoised_image_url
