
from django.contrib import admin
from django.urls import path, include

import app.views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path("api-token-auth/", views.obtain_auth_token),  # 获取Token的接口
    path('', app.views.my_page, name='my_page'),
    path("api-auth/", include("rest_framework.urls")),  # DRF的登录退出
    path("admin/", admin.site.urls),
    path('login/', app.views.user_login, name='user_login'),
    path('register/', app.views.user_register, name='user_register'),
    path('logout/', app.views.user_logout, name='user_logout'),
    path('upload/', app.views.upload_image, name='upload_image'),
    path('list/', app.views.list_images, name='list_images'),
    path('delete/<int:image_id>/', app.views.delete_image, name='delete_image'),
    path('count/', app.views.user_image_count,name='image_count'),
    path('info/', app.views.user_info, name='user_info'),
    path('save_panels/', app.views.save_user_panels, name='save_user_panels'),
    path('get_panels/', app.views.get_user_panels, name='get_user_panels'),
    path('delete_panels/', app.views.delete_user_panels, name='delete_user_panels'),
    path('get_image_url/<int:image_id>/', app.views.get_image_url, name='get_image_url'),
    path('gauss/', app.views.add_gaussian_noise_to_image, name='add_gaussian_noise'),
    path('little/', app.views.wavelet_denoising_view, name='wavelet_denoising'),
    path('many/', app.views.multi_channel_denoising_view, name='multi_channel_denoising'),
    path('NL/', app.views.non_local_means_denoising_view, name='non_local_means_denoising'),
    path('Total/', app.views.total_variation_denoising_view, name='total_variation_denoising'),
    path('pepper/', app.views.add_salt_pepper_noise_view, name='add_salt_pepper_noise'),
    path('salt/', app.views.add_salt_noise_view, name='add_salt_noise'),
    path('Poisson/', app.views.add_poisson_noise_view, name='add_poisson_noise'),
    path('uniform/', app.views.add_uniform_noise_view, name='add_uniform_noise'),
    path('motion_blur/', app.views.add_motion_blur_noise_view, name='add_motion_blur_noise'),
    path('bm3d/', app.views.bm3d_denoising_view, name='bm3d_denoising'),
    path('gauss_denoising/', app.views.gaussian_denoising_view, name='gaussian_denoising'),
    path('median/', app.views.median_denoising_view, name='median_denoising'),
    path('delall/', app.views.delete_all_images, name='delall'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
