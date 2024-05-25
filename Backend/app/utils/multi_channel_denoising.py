import os
import uuid

import bm3d
import cv2
import numpy as np
import pywt
from django.conf import settings

from .mse import calculate_mse
from .psnr_ import calculate_psnr
from .ssim import calculate_ssim
from ..models import Image


def multi_channel_denoising(image_id, user, method):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    if original_img is None:
        return None

    img_y_cr_cb = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCrCb)
    channels = cv2.split(img_y_cr_cb)
    result_channels = []

    # Dictionary of denoising methods
    denoise_methods = {
        "0": ("BM3D", 25),
        "1": ("Median", 5),
        "2": ("Gaussian", (7, 7), 1.5),
        "3": ("NLM", 15, 21),
        "4": ("Wavelet", 'db1', 'soft', 2)
    }

    # Process each channel
    for channel in channels:
        if method == "0":
            sigma_est, bm3d_stage_arg = denoise_methods["0"][1], bm3d.BM3DStages.ALL_STAGES
            denoised_channel = bm3d.bm3d(channel, sigma_psd=sigma_est, stage_arg=bm3d_stage_arg)
        elif method == "1":
            kernel_size = denoise_methods["1"][1]
            denoised_channel = cv2.medianBlur(channel, kernel_size)
        elif method == "2":
            kernel_size, sigma = denoise_methods["2"][1:]
            denoised_channel = cv2.GaussianBlur(channel, kernel_size, sigma)
        elif method == "3":
            strength, search_window = denoise_methods["3"][1:]
            denoised_channel = cv2.fastNlMeansDenoising(channel, None, strength, 7, search_window)
        elif method == "4":
            wavelet, mode, level = denoise_methods["4"][1:]
            coeffs = pywt.wavedec2(channel, wavelet, level=level)
            threshold_factor = 0.1
            coeffs[1:] = [
                tuple(pywt.threshold(detail, np.std(detail) * threshold_factor, mode=mode) for detail in level) for
                level in coeffs[1:]]
            denoised_channel = pywt.waverec2(coeffs, wavelet)

        denoised_channel = np.clip(denoised_channel, 0, 255).astype(np.uint8)
        result_channels.append(denoised_channel)

    denoised_img_y_cr_cb = cv2.merge(result_channels)
    final_denoised_img = cv2.cvtColor(denoised_img_y_cr_cb, cv2.COLOR_YCrCb2BGR)

    # 调整尺寸以匹配原图
    if original_img.shape != final_denoised_img.shape:
        final_denoised_img = cv2.resize(final_denoised_img, (original_img.shape[1], original_img.shape[0]))

    mse_value = calculate_mse(original_img, final_denoised_img)
    psnr_value = calculate_psnr(original_img, final_denoised_img)
    ssim_value = calculate_ssim(original_img, final_denoised_img)

    unique_filename = f'{uuid.uuid4().hex}.png'
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, final_denoised_img)

    denoised_image = Image.objects.create(
        uploader=user,
        image_name=unique_filename,
        image_file=f'images/{unique_filename}'
    )

    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
    return {
        'denoised_image_url': denoised_image_url,
        'mse': mse_value,
        'psnr': psnr_value,
        'ssim': ssim_value
    }
