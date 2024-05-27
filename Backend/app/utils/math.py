from skimage import io
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
import cv2

# 加载图像
A = io.imread('C:\\Users\\23103\\Pictures\\downloaded_image (29).jpg')  # 原图像A
C = io.imread('C:\\Users\\23103\\Pictures\\222.png')  # 滤波后图像C

# 确保图像维度一致
if A.shape != C.shape:
    C = cv2.resize(C, (A.shape[1], A.shape[0]))

# 计算MSE
mse_value = mse(A, C)

# 计算PSNR
psnr_value = psnr(A, C)

# 计算SSIM
# 手动设置窗口大小（例如，设置为7，确保小于图像的最小尺寸）
ssim_value, _ = ssim(A, C, full=True, win_size=7, channel_axis=2)

print(f"PSNR: {psnr_value} dB")
print(f"MSE: {mse_value}")
print(f"SSIM: {ssim_value}")
