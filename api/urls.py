
from django.urls import path
from .views import register, login, me, create_house, get_houses, get_one_house, get_house_disponibilities, create_disponibility, my_houses, upload_somes_images
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('auth/login', login),
    path('auth/register', register),
    path('auth/me', me),

    path('my_houses', my_houses),
    path('house', create_house),
    path('houses', get_houses),
    path('house/<int:id>', get_one_house),
    path('house/<int:id>/dispo', get_house_disponibilities),

    path('house/<int:id>/create_dispo', create_disponibility),

    path('house/<int:id>/upload_images', upload_somes_images),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
