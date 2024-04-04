from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth.models import User
from profile_user.models import Profile
from .serializers import ProfileSerializer


class ProfileApi(APIView):
    """
    API-класс с методами по работе с профилем пользователя
    """

    def get(self, request: Request) -> Response:
        """
        Метод для получения информации о профиле пользователя.
        :param request:
        :return:
        """
        profile = Profile.objects.get(user=request.user)
        serialized = ProfileSerializer(profile)
        return Response(serialized.data)

    def post(self, request: Request) -> Response:
        """
        Метод для обновления полного имени, эл.почты и телефона пользователя.
        Если введенные почта или email в БД уже существуют, то возвращается ответ со статусом 400.
        :param request:
        :return:
        """
        data: dict = request.data
        try:
            updated_lines = Profile.objects.filter(user=request.user).update(
                fullName=data["fullName"], email=data["email"], phone=data["phone"]
            )
        except IntegrityError:
            return Response(
                {"error": "E-mail или/и телефон с такими данными уже существуют"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.get(user=request.user)
        serialized = ProfileSerializer(profile)
        return Response(serialized.data)


class PasswordChangeAPI(APIView):
    """
    API-класс с методом post для обновления пароля пользователя.
    """

    def post(self, request: Request) -> Response:
        data = request.data.get("password", None)
        if data is not None:
            cur_user = User.objects.get(username=request.user.username)
            cur_user.set_password(data)
            cur_user.save()
        return Response(status=status.HTTP_200_OK)


class AvatarChangeAPI(APIView):
    """
    API-класс с методом post для обновления аватара пользователя.
    При загрузке файла более 2 мб возвращается сообщение об ошибке.
    """

    def post(self, request: Request) -> Response:
        user_profile = Profile.objects.get(user=request.user)
        file = request.FILES["avatar"]
        if file.size <= 2097152:
            user_profile.avatar = file
            user_profile.save()
            response_dict: dict = {
                "src": user_profile.avatar.url,
                "alt": user_profile.avatar.name,
            }
            return Response(response_dict, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Ошибка загрузки, размер файла не должен быть более 2 МБ"},
                status=status.HTTP_400_BAD_REQUEST,
            )
