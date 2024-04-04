from django.urls import path
from .views import ProfileApi, PasswordChangeAPI, AvatarChangeAPI

app_name = "site_auth"

urlpatterns = [
    path("api/profile/", ProfileApi.as_view()),
    path("api/profile/avatar/", AvatarChangeAPI.as_view()),
    path("api/profile/password/", PasswordChangeAPI.as_view()),
]
