import os

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.middleware.csrf import rotate_token
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Image, UserPanel
from .serializers import UserSerializer, ImageSerializer, UserPanelSerializer
from django.conf import settings
from .utils.add_gaussian_noise import add_gaussian_noise
from .utils.wavelet_denoising import wavelet_denoising
from .utils.multi_channel_denoising import multi_channel_denoising
from .utils.non_local_means_denoising import non_local_means_denoising
from .utils.total_variation_denoising import total_variation_denoising
from .utils.add_salt_pepper_noise import add_salt_pepper_noise
from .utils.add_salt_noise import add_salt_noise
from .utils.add_poisson_noise import add_poisson_noise
from .utils.add_uniform_noise import add_uniform_noise
from .utils.add_motion_blur_noise import add_motion_blur_noise
from .utils.bm3d_denosing import bm3d_denoising


@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def user_info(request):
    # 检查用户是否已登录
    if request.user.is_authenticated:
        # 获取当前登录用户
        user = request.user
        # 提取用户信息
        user_info_msg = {
            'username': user.username,
            'id': user.id
        }
        # 返回用户信息作为 JSON 响应
        return Response(user_info_msg, status=status.HTTP_200_OK)
    else:
        # 如果用户未登录，返回未授权错误
        return Response({'error': '用户未登录'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def user_register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': '账号注册成功'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_logout(request):
    # 执行 Django 默认的用户登出操作
    django_logout(request)
    # 旋转 CSRF 令牌以确保下一个请求会生成新的令牌
    rotate_token(request)
    return Response({'message': '账号退出成功'}, status=status.HTTP_200_OK)
    # logout(request)
    # return Response({'message': '账号退出成功'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_image(request):
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(uploader=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_images(request):
    query_param = request.query_params.get('query', None)
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 10)

    images = Image.objects.all()
    if query_param:
        images = images.filter(image_name__icontains=query_param)

    paginator = Paginator(images, per_page)
    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)

    # 序列化图片对象列表
    serializer = ImageSerializer(images_page, many=True)
    # 提取每个图片对象的URL，并添加端口号
    data = [{
        'image_id': image['image_id'],
        'image_name': image['image_name'],
        'image_file_url': request.build_absolute_uri(image['image_file'])  # 构建图片文件的绝对路径URL
        # 'image_file_url': f"http://{request.get_host()}:{server_port}{image['image_file']}"
    } for image in serializer.data]

    return Response(data)


@api_view(['GET'])
def get_image_url(request, image_id):
    # 根据图片ID从数据库中获取对应的图片对象，如果不存在则返回404错误
    image = get_object_or_404(Image, image_id=image_id)

    # 获取图片文件的文件名
    image_file_name = os.path.basename(image.image_file.name)

    # 构建图片文件的HTTP访问链接，并添加端口号
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'images/' + image_file_name)

    # 构建响应数据
    response_data = {
        'image_id': image_id,
        'image_url': image_url
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_image_count(request):
    # 获取当前登录的用户
    current_user = request.user

    # 如果用户未登录，返回错误信息
    if not current_user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=401)

    # 使用当前用户过滤图像对象
    user_images = Image.objects.filter(uploader=current_user)

    # 计算属于当前用户的图像总数
    image_count = user_images.count()

    # 构建响应，将图像总数作为数据发送回前端
    return Response({"image_count": image_count})


@api_view(['DELETE'])
def delete_image(request, image_id):
    try:
        image = Image.objects.get(image_id=image_id)
    except Image.DoesNotExist:
        return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    # 获取图片文件路径
    image_file_path = image.image_file.path

    # 删除数据库中的图片记录
    image.delete()

    # 检查并删除对应的媒体文件
    if os.path.exists(image_file_path):
        os.remove(image_file_path)
        return Response({'message': 'Image and file deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'message': 'Image deleted from database, but file not found'},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def save_user_panels(request):
    try:
        user_panel = UserPanel.objects.get(user=request.user)
        # 获取现有数据
        panels_data = user_panel.panels
        # 获取新数据
        new_panel_data = request.data
        if new_panel_data:
            # 如果已存在数据，则将新数据添加到现有数据中
            panels_data.append(new_panel_data)
        else:
            # 如果新数据为空，则返回错误响应
            return Response({'error': 'No panel data provided'}, status=status.HTTP_400_BAD_REQUEST)
        # 更新 panels 字段并保存
        user_panel.panels = panels_data
        user_panel.save()
        # 返回更新后的数据
        serializer = UserPanelSerializer(user_panel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except UserPanel.DoesNotExist:
        # 如果用户没有 UserPanel 对象，则创建一个新的对象并保存新数据
        serializer = UserPanelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_panels(request):
    try:
        user_panel = UserPanel.objects.get(user=request.user)
        serializer = UserPanelSerializer(user_panel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserPanel.DoesNotExist:
        return Response({'panels': []}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_user_panels(request):
    try:
        user_panel = UserPanel.objects.get(user=request.user)
        panels = user_panel.panels  # 获取用户面板的 JSON 数据列表

        # 检查请求中是否包含要删除的索引数组
        indexes_to_delete = request.data.get('indexes', [])

        # 删除指定索引处的数据
        remaining_panels = [panel for index, panel in enumerate(panels) if index not in indexes_to_delete]

        # 更新用户面板的 JSON 数据
        user_panel.panels = remaining_panels
        user_panel.save()

        # 返回剩余的数据作为响应
        serializer = UserPanelSerializer(user_panel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except UserPanel.DoesNotExist:
        return Response({'message': 'User panel not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_gaussian_noise_to_image(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 调用添加高斯噪声的函数，并传递用户参数
    noisy_image_url = add_gaussian_noise(image_id, user)

    if noisy_image_url:
        # 将反斜杠替换为正斜杠
        noisy_image_url = noisy_image_url.replace("\\", "/")
        # 拼接完整的 HTTP 地址
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def wavelet_denoising_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 执行小波变换降噪
    denoised_image_url = wavelet_denoising(image_id, user)

    if denoised_image_url:
        denoised_image_url = denoised_image_url.replace("\\", "/")
        full_denoised_image_url = settings.BACKEND_BASE_URL + denoised_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_denoised_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def multi_channel_denoising_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 执行多通道联合分析的图像降噪
    denoised_image_url = multi_channel_denoising(image_id, user)

    if denoised_image_url:
        denoised_image_url = denoised_image_url.replace("\\", "/")
        full_denoised_image_url = settings.BACKEND_BASE_URL + denoised_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_denoised_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def non_local_means_denoising_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 执行非局部均值降噪
    denoised_image_url = non_local_means_denoising(image_id, user)

    if denoised_image_url:
        denoised_image_url = denoised_image_url.replace("\\", "/")
        full_denoised_image_url = settings.BACKEND_BASE_URL + denoised_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_denoised_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def total_variation_denoising_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 执行总差变换降噪
    denoised_image_url = total_variation_denoising(image_id, user)

    if denoised_image_url:
        denoised_image_url = denoised_image_url.replace("\\", "/")
        full_denoised_image_url = settings.BACKEND_BASE_URL + denoised_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_denoised_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def bm3d_denoising_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 执行BM3D降噪
    denoised_image_url = bm3d_denoising(image_id, user)

    if denoised_image_url:
        denoised_image_url = denoised_image_url.replace("\\", "/")
        full_denoised_image_url = settings.BACKEND_BASE_URL + denoised_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_denoised_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_salt_pepper_noise_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 添加椒噪声
    noisy_image_url = add_salt_pepper_noise(image_id, user)

    if noisy_image_url:
        noisy_image_url = noisy_image_url.replace("\\", "/")
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_salt_noise_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 添加盐噪声
    noisy_image_url = add_salt_noise(image_id, user)

    if noisy_image_url:
        noisy_image_url = noisy_image_url.replace("\\", "/")
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_poisson_noise_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 添加泊松噪声
    noisy_image_url = add_poisson_noise(image_id, user)

    if noisy_image_url:
        noisy_image_url = noisy_image_url.replace("\\", "/")
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_uniform_noise_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 添加均匀噪声
    noisy_image_url = add_uniform_noise(image_id, user)

    if noisy_image_url:
        noisy_image_url = noisy_image_url.replace("\\", "/")
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_motion_blur_noise_view(request):
    image_id = request.data.get('image_id')
    user = request.user  # 获取当前登录的用户

    # 添加运动模糊噪声
    noisy_image_url = add_motion_blur_noise(image_id, user)

    if noisy_image_url:
        noisy_image_url = noisy_image_url.replace("\\", "/")
        full_noisy_image_url = settings.BACKEND_BASE_URL + noisy_image_url
        # 返回降噪后的图片URL
        return Response({'noisy_image_url': full_noisy_image_url}, status=status.HTTP_200_OK)
    else:
        return Response({'message': '未找到图片'}, status=status.HTTP_404_NOT_FOUND)


def my_page(request):
    return render(request, 'home.html')
