import os
import uuid
import cv2
import numpy as np
import bm3d
from django.conf import settings
from ..models import Image

def multi_channel_denoising(image_id, user):
    try:
        original_image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return None

    original_image_path = os.path.join(settings.MEDIA_ROOT, original_image.image_file.name)
    original_img = cv2.imread(original_image_path, cv2.IMREAD_COLOR)

    if original_img is None:
        return None

    if original_img.ndim == 3:
        img_y_cr_cb = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCrCb)
        channels = cv2.split(img_y_cr_cb)
        result_channels = []

        # Manually set the noise standard deviation
        sigma_est = 25  # This is an example value, you might need to adjust it based on your needs
        bm3d_kwargs = {'sigma_psd': sigma_est, 'stage_arg': bm3d.BM3DStages.ALL_STAGES}

        for channel in channels:
            denoised_channel = bm3d.bm3d(channel, **bm3d_kwargs)
            denoised_channel = np.clip(denoised_channel, 0, 255).astype(np.uint8)
            result_channels.append(denoised_channel)

        # Merge channels and convert back to BGR color space
        denoised_img_y_cr_cb = cv2.merge(result_channels)
        final_denoised_img = cv2.cvtColor(denoised_img_y_cr_cb, cv2.COLOR_YCrCb2BGR)

        unique_filename = f'{uuid.uuid4().hex}.png'
        denoised_image_path = os.path.join(settings.MEDIA_ROOT, 'images', unique_filename)
        cv2.imwrite(denoised_image_path, final_denoised_img)

        denoised_image = Image.objects.create(
            uploader=user,
            image_name=unique_filename,
            image_file=f'images/{unique_filename}',
        )

        denoised_image_url = os.path.join(settings.MEDIA_URL, 'images', unique_filename)
        return denoised_image_url

    return None
