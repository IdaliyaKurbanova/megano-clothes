from django.urls import path
from .views import ProfileApi, PasswordChangeAPI, AvatarChangeAPI

app_name = "profile_user"

urlpatterns = [
    path("api/profile/", ProfileApi.as_view(), name="profile-info"),
    path("api/profile/avatar/", AvatarChangeAPI.as_view(), name='avatar-change'),
    path("api/profile/password/", PasswordChangeAPI.as_view(), name='password-change'),
]
