from django.contrib import admin

# Register your models here.

from .models import VillaversoUser, House, ImageHouse

admin.site.register(VillaversoUser)
admin.site.register(House)
admin.site.register(ImageHouse)
