
from django.db import models
from django.core.validators import *
from django.contrib.auth.models import User

from django.utils import timezone
# Create your models here.

class Area(models.Model):
    pincode = models.CharField(validators = [MinLengthValidator(6), MaxLengthValidator(6)],max_length = 6,unique=True)
    city = models.CharField(max_length = 20)

class CarDealer(models.Model):
    car_dealer = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(validators = [MinLengthValidator(10), MaxLengthValidator(13)], max_length = 13)
    area = models.OneToOneField(Area, on_delete=models.CASCADE)
    wallet = models.IntegerField(default = 0)

def __str__(self):
    return self.car_dealer.username

    

class Vehicles(models.Model):
    car_name = models.CharField(max_length = 20)
    color = models.CharField(max_length = 10)
    dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null = True)
    capacity = models.CharField(max_length = 2)
    is_available = models.BooleanField(default = True)
    description = models.CharField(max_length = 100)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='vehicles/')

def __str__(self):
    return self.car_dealer.username













class Vehicle(models.Model):
    CATEGORY_CHOICES = [
        ('FAMILY', 'Family'),
        ('VAN', 'Van'),
        ('BUSINESS', 'Business & Professional'),
        ('WEDDING', 'Wedding'),
    ]

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    capacity = models.IntegerField()
    description = models.TextField()
    pincode = models.CharField(max_length=10)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='vehicles/')
    upload_date = models.DateField(default=timezone.now)  # auto-set sa current date

    def __str__(self):
        return self.name






    






