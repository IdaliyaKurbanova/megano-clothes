import json
from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authentication import authenticate
from django.contrib.auth.models import User
from profile_user.models import Profile


class Login(APIView):
    """
    API-класс с методом post для аутентификации пользователя.
    """

    def post(self, request: Request) -> Response:
        data = json.loads(list(request.data.keys())[0])
        username = data["username"]
        password = data["password"]
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": "Введен неверный логин или пароль"},
        )


class Logout(APIView):
    """
    API-класс с методом post для прекращения аутентифицированной сессии пользователя.
    """

    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)


class Registration(APIView):
    """
    API-класс с методом post для регистрации нового пользователя.
    """

    def post(self, request: Request) -> Response:
        data = json.loads(list(request.data.keys())[0])
        username = data["username"]
        password = data["password"]
        if username and password:
            user = User.objects.create_user(username=username, password=password)
            if user:
                Profile.objects.create(user=user)
                login(request=request, user=user)
                return Response(status=status.HTTP_200_OK)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"Ошибка": "Некорректный логин для регистрации"},
        )
