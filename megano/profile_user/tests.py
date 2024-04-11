import json
import os

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from django.test import TestCase
from django.urls import reverse

from megano import settings
from profile_user.models import Profile
from profile_user.serializers import ProfileSerializer


class ProfileApiTestCase(TestCase):
    """
    Класс с методами для тестирования представлений, связанных с профилем пользователя.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Метод для создания пользователя в базе данных, а также объявления необходимых атрибутов для тестирования.
        :return:
        """
        # объявляются пароль и логин и прочие данные для создания пользователя, который будет использоваться в тесте
        cls.credentials: dict = {'username': 'tester', 'password': 'Test24@'}
        cls.initial_profile_info: dict = {'fullName': 'Тестер', 'email': 'tester@mail.ru', 'phone': '8934090239'}

        # объявляются имя, почта и телефон для создания еще одного пользователя, который будет использоваться в тесте
        cls.extra_user_info: dict = {'fullName': 'Экстра', 'email': 'extra@mail.ru', 'phone': '44553322'}

        # данные для обновления профиля пользователя
        cls.changed_profile_info: dict = {'fullName': 'Тестерчик', 'email': 'testerchik@mail.ru', 'phone': '893409023'}

        # абсолютные пути к файлам, которые будут загружаться в тесте в качестве аватара
        cls.profile_avatar: str = os.path.join(settings.BASE_DIR, "uploads\\profiles\\Velli.jpg")
        cls.too_big_file: str = os.path.join(settings.BASE_DIR, "uploads\\profiles\\big_file.jpg")

        # новый пароль пользователя для обновления
        cls.new_password: str = '12345678'

        # создаются пользователь и профиль пользователя для тестирования
        cls.user = User.objects.create_user(**cls.credentials)
        cls.profile = Profile.objects.create(user=cls.user, **cls.initial_profile_info)

        # создается в БД еще один дополнительный пользователь
        cls.extra_user = User.objects.create_user(username='extra', password='extra24@')
        cls.extra_profile = Profile.objects.create(user=cls.extra_user,**cls.extra_user_info)

    def setUp(self) -> None:
        """
        Метод-настройка, который выполняется перед каждым тестом.
        :return:
        """
        self.client.force_login(self.user)

    def test_get_profile(self) -> None:
        """
        Тест для получения данных о текущем пользователе
        """
        response = self.client.get(reverse("profile_user:profile-info"))
        serialized = ProfileSerializer(self.profile)

        self.assertJSONEqual(response.content, serialized.data)

    def test_post_profile_info(self) -> None:
        """
        Тест для проверки обновление таких данных профиля, как имя, почта, телефон
        """
        response = self.client.post(reverse("profile_user:profile-info"), data=self.changed_profile_info)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        response_dict = {key: value for key, value in response_data.items() if key in self.changed_profile_info.keys()}
        self.assertEqual(response_dict, self.changed_profile_info)

    def test_for_profile_info_uniqueness(self) -> None:
        """
        Тест для проверки того, что в профиль можно добавить только такие данные, которых еще нет в базе данных.
        """
        response = self.client.post(reverse("profile_user:profile-info"), data=self.extra_user_info)
        self.assertEqual(response.status_code, 400)

    def test_avatar_change(self) -> None:
        """
        Тест для проверки представления со сменой аватара.
        """
        with open(self.profile_avatar, 'rb') as image_file:
            response = self.client.post(reverse("profile_user:avatar-change"), {"avatar": image_file})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.profile_avatar.split("\\")[-1][:-4], str(response.content))

    def test_big_file_avatar_change(self) -> None:
        """
        Тест для проверки того, что в качестве аватара нельзя загрузить файл больше 2 мб.
        """
        with open(self.too_big_file, 'rb') as image_file:
            response = self.client.post(reverse("profile_user:avatar-change"), {"avatar": image_file})

        self.assertEqual(response.status_code, 400)

    def test_password_change(self) -> None:
        """
        Тест для проверки представления со сменой пароля.
        """
        response = self.client.post(reverse("profile_user:password-change"), {"password": self.new_password})
        user = authenticate(username=self.credentials['username'], password=self.new_password)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user, self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Метод для удаления из БД созданных с целью тестирования пользователей.
        """
        cls.profile.delete()
        cls.user.delete()
        cls.extra_user.delete()
        cls.extra_profile.delete()
