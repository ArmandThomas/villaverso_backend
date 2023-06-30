from django.db import models


# Create your models here.

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class VillaversoUser(models.Model):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=500)

    def __str__(self):
        return self.email


class ImageHouse(models.Model):
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    house = models.ForeignKey('House', on_delete=models.CASCADE)

    def __str__(self):
        return self.image.name


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
    description = models.TextField()

    def __str__(self):
        return str(self.id) + " " + self.name + " " + self.owner.email


class Deal(models.Model):
    house_receiver = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_receiver')
    house_client = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_client')
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.CharField(max_length=30)
    nbr_people = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + " " + self.house_receiver.name + " " + self.house_client.name


class Disponibility(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.house.name + " " + str(self.id)
