import numpy as np
import cv2
import pywt
import uuid
import os
from django.conf import settings
from .mse import calculate_mse
from .psnr_ import calculate_psnr
from .ssim import calculate_ssim
from ..models import Image

def wavelet_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    if original_img is None:
        return None

    # 转换颜色空间到YCrCb
    img_y_cr_cb = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCrCb)
    channels = cv2.split(img_y_cr_cb)

    denoised_channels = []
    threshold_factor = 0.1

    for channel in channels:
        coeffs = pywt.wavedec2(channel, 'db1', level=2)
        coeffs[1:] = [tuple(pywt.threshold(detail, np.std(detail)*threshold_factor, mode='soft') for detail in level) for level in coeffs[1:]]
        denoised_channel = pywt.waverec2(coeffs, 'db1')
        denoised_channels.append(denoised_channel)

    # 合并通道并转换颜色空间回到BGR
    denoised_img = cv2.merge(denoised_channels)
    denoised_img = np.clip(denoised_img, 0, 255)  # 确保像素值在0到255之间
    denoised_img = denoised_img.astype(np.uint8)  # 转换为uint8
    denoised_img = cv2.cvtColor(denoised_img, cv2.COLOR_YCrCb2BGR)  # 转换回BGR颜色空间

    # 调整尺寸以匹配原图
    if original_img.shape != denoised_img.shape:
        denoised_img = cv2.resize(denoised_img, (original_img.shape[1], original_img.shape[0]))

    # 计算性能指标
    mse_value = calculate_mse(original_img, denoised_img)
    psnr_value = calculate_psnr(original_img, denoised_img)
    ssim_value = calculate_ssim(original_img, denoised_img)

    # 保存降噪后的图像
    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return {
        'denoised_image_url': denoised_image_url,
        'mse': mse_value,
        'psnr': psnr_value,
        'ssim': ssim_value
    }
