from django.db import models
from django.contrib.auth.models import User


def get_avatar_file_name(instance: "Profile", filename) -> str:
    """
    Метод для создания пути файла с аватаром пользователя.

    :param instance: экземпляр профиля
    :param filename: название загруженного файла
    :return: путь к файлу с аватором пользователя в папке uploads
    """
    return "profiles/profile_{pk}/{filename}".format(
        pk=instance.user.pk, filename=filename
    )


class Profile(models.Model):
    """
    Модель профиля пользователя - расширение модели пользователя User.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    fullName = models.CharField(null=True, blank=True, max_length=200)
    email = models.EmailField(null=True, blank=True, unique=True, max_length=50)
    phone = models.CharField(null=True, blank=True, max_length=15, unique=True)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=get_avatar_file_name,
        default="profiles/no_avatar.jpg",
    )
