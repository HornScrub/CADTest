from django.db import models

# For missing data, have to deside if we should use null or placeholder values for the API clients.

# Vehicle, needs VIN, descripton, augments maybe (spoilers, lights, decals), probably more?
class Vehicle(models.Model):
    # license_plate: Should make this a foreign key, and embed a function to check license plate validity (per state? county?)
    license_plate = models.CharField(max_length=10, unique=True) 
    # owner_name: 
    owner_name = models.models.ForeignKey('Person', on_delete=models.CASCADE, related_name='vehicles')
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='vehicles')  # Nullable if no address
    # vehicle_make, vehicle_model : Should standardize inputs (probably all inputs) using save() function eg. input- "Ford " " Focus" -> "FORD" "FOCUS"
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    # is_stolen : Should point to a member of an Incident() maybe?
    is_stolen = models.BooleanField(default=False)
    # outstanding warrents: This probably should point to the owner's warrents:
    outstanding_warrants = models.TextField(blank=True, null=True)

    # Use save() to standardize the input before we create the object. We could add more members here besides make and model

    def save(self, *args, **kwargs):
        # Standardize fields
        self.vehicle_make = self.vehicle_make.strip().upper()
        self.vehicle_model = self.vehicle_model.strip().upper()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.license_plate

# Address, should be owned by Persons, Vehicles, Incidents. Maybe modify this to have descriptions of locations if its incomplete
#   (like "Red house next to Eastwood Park", "10 miles before Exit 28", "Southbound I-5 by Long Beach", something like that, or
#   maybe that should be its own model)
class Address(models.Model):
    street = models.CharField(max_length=255, blank=True, null=True)  # e.g., "123 Elm St"
    apartment = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Apt 4B"
    city = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Austin"
    state = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Texas"
    country = models.CharField(max_length=50, default="USA")  # Default to USA
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # e.g., ZIP or international postal code
    owner = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='addresses') 
    residents = models.ManyToManyField('Person', related_name='residences', blank=True)

    # Use save() to standardize the input before we add the object to db
    def save(self, *args, **kwargs):
        # Standardize text fields
        if self.street:
            self.street = self.street.strip().upper()
        if self.apartment:
            self.apartment = self.apartment.strip().upper()
        if self.city:
            self.city = self.city.strip().upper()
        if self.state:
            self.state = self.state.strip().upper()
        if self.postal_code:
            self.postal_code = self.postal_code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        address = f"{self.street or 'UNKNOWN'}"
        if self.apartment:
            address += f", {self.apartment}"
        address += f", {self.city or 'UNKNOWN'}, {self.state or 'UNKNOWN'}, {self.country}, {self.postal_code or 'UNKNOWN'}"
        return address


