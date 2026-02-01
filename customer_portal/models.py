from django.db import models
from django.core.validators import *
from django.contrib.auth.models import User
from car_dealer_portal.models import *

# Create your models here.
from car_dealer_portal.models import Vehicles




class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(validators = [MinLengthValidator(10), MaxLengthValidator(13)], max_length = 13)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    car_dealer = models.ForeignKey(CarDealer, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT)
    
    # --- Mula sa RentalDetails, ilipat natin dito ---
    customer_name = models.CharField(max_length=255, null=True)
    customer_address = models.CharField(max_length=255, null=True)
    rental_date = models.DateField(null=True)
    return_date = models.DateField(null=True)
    description = models.TextField(null=True)
    payment_method = models.CharField(max_length=50, null=True)
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    
    # --- Existing fields ---
    rent = models.CharField(max_length=10) # Dito yung amount
    days = models.CharField(max_length=3)
    is_complete = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
status = models.CharField(max_length=20, default="Pending") # Pending, Returned, Cancelled
    




class RentalDetails(models.Model):
    vehicle = models.ForeignKey(Vehicles, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_address = models.CharField(max_length=255)
    rental_date = models.DateField()
    return_date = models.DateField()
    total_days = models.PositiveIntegerField()
    description = models.TextField()
    payment_method = models.CharField(max_length=50)
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


  