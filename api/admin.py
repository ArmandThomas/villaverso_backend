from django.contrib import admin

# Register your models here.

from .models import VillaversoUser, House, ImageHouse, Disponibility, Deal

admin.site.register(VillaversoUser)
admin.site.register(House)
admin.site.register(ImageHouse)

admin.site.register(Disponibility)
admin.site.register(Deal)
