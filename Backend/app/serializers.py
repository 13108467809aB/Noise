from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Image
from app.models import UserPanel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_id', 'image_name', 'image_file', 'uploader']


class UserPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPanel
        fields = ['panels']  # 确保只包含 panels 字段

    # 可以选择重写 create 方法以确保正确处理 panels 字段
    def create(self, validated_data):
        panels_data = validated_data.pop('panels', [])
        user_panel = UserPanel.objects.create(**validated_data)
        user_panel.panels = panels_data  # 设置 panels 字段的值
        user_panel.save()
        return user_panel
