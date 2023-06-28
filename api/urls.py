
from django.urls import path
from .views import register, login, me

urlpatterns = [
    path('auth/login', login),
    path('auth/register', register),
    path('auth/me', me)
]
