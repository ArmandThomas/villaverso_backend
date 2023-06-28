
from django.urls import path
from .views import register, login, me, create_house

urlpatterns = [
    path('auth/login', login),
    path('auth/register', register),
    path('auth/me', me),

    path('house', create_house)
]
