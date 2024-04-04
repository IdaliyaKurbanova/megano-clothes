from rest_framework import serializers
from .models import Profile
from catalogs.serializers import ImageFieldSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя.
    """

    avatar = ImageFieldSerializer()

    class Meta:
        model = Profile
        fields = "fullName", "email", "phone", "avatar"
