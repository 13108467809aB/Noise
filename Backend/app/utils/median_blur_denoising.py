import os
import uuid
import cv2
from django.conf import settings

from .mse import calculate_mse
from .psnr_ import calculate_psnr
from .ssim import calculate_ssim
from ..models import Image


def median_blur_denoising(image_id, user):
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

    # 应用中值滤波去噪
    # 中值滤波的核大小必须是奇数，这里使用5x5核
    kernel_size = 5
    denoised_img = cv2.medianBlur(original_img, kernel_size)

    # 计算性能指标
    mse_value = calculate_mse(original_img, denoised_img)
    psnr_value = calculate_psnr(original_img, denoised_img)
    ssim_value = calculate_ssim(original_img, denoised_img)

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
    return {
        'denoised_image_url': denoised_image_url,
        'mse': mse_value,
        'psnr': psnr_value,
        'ssim': ssim_value
    }
