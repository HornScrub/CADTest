from django.db import models

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10, unique=True)
    owner_name = models.CharField(max_length=255)
    owner_address = models.TextField()
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    is_stolen = models.BooleanField(default=False)
    outstanding_warrants = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.license_plate