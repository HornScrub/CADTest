from django.contrib import admin
from .models import Vehicle

# Register your models here.

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner_name', 'vehicle_make', 'vehicle_model', 'is_stolen')
    search_fields = ('license_plate', 'owner_name', 'vehicle_make', 'vehicle_model')