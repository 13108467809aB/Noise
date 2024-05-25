import numpy as np
import cv2
import uuid
import os
from django.conf import settings
from .mse import calculate_mse
from .psnr_ import calculate_psnr
from .ssim import calculate_ssim
from ..models import Image

def non_local_means_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)  # 保留彩色

    if original_img is None:
        return None

    # 应用非局部均值去噪
    denoised_img = cv2.fastNlMeansDenoisingColored(original_img, None, 10, 10, 7, 21)

    # 计算性能指标
    mse_value = calculate_mse(original_img, denoised_img)
    psnr_value = calculate_psnr(original_img, denoised_img)
    ssim_value = calculate_ssim(original_img, denoised_img)

    # 保存降噪后的图像
    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    # 创建并保存图像记录
    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )

    # 返回新图像的URL及性能指标
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
    return {
        'denoised_image_url': denoised_image_url,
        'mse': mse_value,
        'psnr': psnr_value,
        'ssim': ssim_value
    }
