import os
import uuid
import cv2
import numpy as np
from skimage.restoration import denoise_tv_chambolle
from django.conf import settings

from .mse import calculate_mse
from .psnr_ import calculate_psnr
from .ssim import calculate_ssim
from ..models import Image

def total_variation_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    if original_img is None:
        return None

    # 转换颜色空间到RGB并归一化到[0,1]
    original_img_float = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB) / 255.0

    # 应用总变差降噪到每个颜色通道
    denoised_channels = []
    for channel in cv2.split(original_img_float):
        denoised_channel = denoise_tv_chambolle(channel, weight=0.1)
        denoised_channels.append(denoised_channel)

    # 合并所有通道
    denoised_img_float = cv2.merge(denoised_channels)

    # 将图像转换回0-255范围并转为uint8，再转换回BGR颜色空间
    denoised_img = np.clip(denoised_img_float * 255, 0, 255).astype(np.uint8)
    denoised_img = cv2.cvtColor(denoised_img, cv2.COLOR_RGB2BGR)

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
