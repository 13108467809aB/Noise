import os
import uuid

import cv2
import pywt

from ..models import Image
from django.conf import settings

def wavelet_denoising(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    # 执行小波变换
    coeffs2 = pywt.dwt2(original_img, 'haar')  # 这里使用haar小波作为示例，你可以根据需要选择其他小波基函数

    # 对小波系数进行降噪处理
    threshold = 20  # 设定阈值，根据实际情况调整
    coeffs2 = tuple(pywt.threshold(c, threshold, mode='soft') for c in coeffs2)

    # 重构图像
    denoised_img = pywt.idwt2(coeffs2, 'haar')

    # 生成新的文件名，避免命名冲突
    unique_filename = f'{uuid.uuid4().hex}.png'

    # 保存降噪后的图像到media文件夹中
    denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
    cv2.imwrite(denoised_image_path, denoised_img)

    # 创建新的图片对象，并与用户关联
    denoised_image = Image.objects.create(
        uploader=user,  # 将图像与用户关联
        image_name=unique_filename,
        image_file=f'images/{unique_filename}',  # 更新文件路径
    )

    # 构建响应，返回处理后的图片的HTTP地址
    denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)

    return denoised_image_url
