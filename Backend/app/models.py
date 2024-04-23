# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class Image(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=100, unique=True)
    image_file = models.ImageField(upload_to='images/')


class UserPanel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    panels = models.JSONField(default=list)
