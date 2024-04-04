from django.urls import path
from .views import Login, Logout, Registration


app_name = "site_auth"

urlpatterns = [
    path("api/sign-out/", Logout.as_view()),
    path("api/sign-in/", Login.as_view()),
    path("api/sign-up/", Registration.as_view()),
]
