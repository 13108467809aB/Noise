import numpy as np
import cv2
import pywt
import os
import uuid
from django.conf import settings
from ..models import Image


def wavelet_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path)

    if original_img is None:
        return None

    # 确保图像是彩色的
    if len(original_img.shape) != 3 or original_img.shape[2] != 3:
        return None

    # 转换颜色空间到YCrCb
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCrCb)
    channels = cv2.split(original_img)

    denoised_channels = []
    threshold_factor = 0.1

    for channel in channels:
        coeffs = pywt.wavedec2(channel, 'db1', level=2)
        coeffs = list(coeffs)
        cA, details = coeffs[0], coeffs[1:]

        for i, detail_level in enumerate(details):
            detail_level = list(detail_level)
            for j, coeff in enumerate(detail_level):
                sigma = np.std(coeff)
                threshold = sigma * threshold_factor
                detail_level[j] = pywt.threshold(coeff, threshold, mode='soft')
            details[i] = tuple(detail_level)

        coeffs[1:] = details
        denoised_channel = pywt.waverec2(coeffs, 'db1')
        denoised_channels.append(denoised_channel)

    # 合并通道并转换颜色空间回到BGR
    if len(denoised_channels) == 3:
        denoised_img = cv2.merge(denoised_channels)
        # 确保图像数据类型为 float32
        denoised_img = np.float32(denoised_img)
        denoised_img = cv2.cvtColor(denoised_img, cv2.COLOR_YCrCb2BGR)
    else:
        denoised_img = denoised_channels[0]
        denoised_img = np.float32(denoised_img)  # 同样确保单通道图像是 float32

    # 归一化到[0, 255]并转换为uint8
    denoised_img = cv2.normalize(denoised_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

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
