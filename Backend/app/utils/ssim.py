import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_ssim(image_a, image_b):
    if image_a is None or image_b is None:
        print("One of the images is None, returning SSIM as 0")
        return 0

    if image_a.dtype != np.uint8 or image_b.dtype != np.uint8:
        image_a = np.clip(image_a, 0, 255).astype(np.uint8)
        image_b = np.clip(image_b, 0, 255).astype(np.uint8)


    min_dim = min(image_a.shape[0], image_a.shape[1], image_b.shape[0], image_b.shape[1])

    win_size = 7 if min_dim >= 7 else min_dim  # 使用7或更小的win_size
    if win_size < 3:
        print("Minimum dimension less than 3, unable to compute SSIM.")
        return 0

    if win_size % 2 == 0:  # 确保win_size是奇数
        win_size -= 1

    try:
        # 添加channel_axis参数，假设颜色通道在最后一个轴
        ssim_value = ssim(image_a, image_b, multichannel=True, win_size=win_size, channel_axis=-1)
        return ssim_value
    except Exception as e:
        print(f"Error calculating SSIM with win_size {win_size}: {e}")
        return 0
