from django.db import models

# Create your models here.

class VillaversoUser(models.Model):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=500)

    def __str__(self):
        return self.email


class House(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(VillaversoUser, on_delete=models.CASCADE)
    nbr_rooms = models.IntegerField(default=0)
    nbr_people = models.IntegerField(default=0)
    m2_house = models.IntegerField(default=0)
    m2_garden = models.IntegerField(default=0)
    pool = models.BooleanField(default=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    localisation = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name - self.owner.email

class ImageHouse(models.Model):
    image = models.ImageField(upload_to='images/')
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return self.house.name