import os
import uuid
import cv2
import numpy as np
import pywt
from django.conf import settings
from ..models import Image


def non_local_means_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_GRAYSCALE)  # 假设图像为灰度图

    if original_img is None:
        return None

    # 进行多通道去噪（此处示例使用小波变换作为多通道去噪）
    coeffs = pywt.wavedec2(original_img, 'haar', level=2)
    denoised_coeffs = [(coeffs[0],)] + [(np.zeros_like(detail) for detail in details) for details in coeffs[1:]]
    multi_denoised_img = pywt.waverec2(denoised_coeffs, 'haar').astype(np.uint8)

    # 应用小波变换
    transformed_coeffs = pywt.wavedec2(original_img, 'haar', level=2)

    # 单通道去噪
    single_denoised_coeffs = [(transformed_coeffs[0],)] + [(np.zeros_like(detail) for detail in details) for details in transformed_coeffs[1:]]

    # 逆变换
    single_denoised_img = pywt.waverec2(single_denoised_coeffs, 'haar').astype(np.uint8)

    # 融合两个去噪结果
    final_denoised_img = ((multi_denoised_img.astype(np.float32) + single_denoised_img.astype(np.float32)) / 2).astype(
        np.uint8)

    # 保存降噪后的图像
    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, final_denoised_img)

    # 创建并保存图像记录
    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',
    )

    # 返回新图像的URL
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
    return denoised_image_url
