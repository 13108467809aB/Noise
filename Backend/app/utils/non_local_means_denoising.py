import os
import uuid
import cv2
import numpy as np
from django.conf import settings
from ..models import Image

def non_local_means_denoising(image_id, user):
    try:
        # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回None
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    # 获取图片文件的绝对路径
    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)

    # 使用OpenCV加载原始图像
    original_img = cv2.imread(original_image_path)

    if original_img is None:
        return None

    # 确保图像是uint8类型，适用于OpenCV处理
    if original_img.dtype != np.uint8:
        original_img = np.clip(original_img, 0, 255).astype(np.uint8)

    # 参数设置
    h = 10  # 颜色分量的强度决定滤波强度
    hForColorComponents = 10  # 颜色组件的滤波强度
    templateWindowSize = 7  # 模板窗口大小，必须是奇数
    searchWindowSize = 21  # 搜索窗口大小，必须是奇数

    # 执行非局部均值降噪
    denoised_img = cv2.fastNlMeansDenoisingColored(
        original_img, None, h, hForColorComponents, templateWindowSize, searchWindowSize)

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
