from django.contrib import admin
from .models import Vehicle

# Register your models here.

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'make', 'model', 'is_stolen')
    search_fields = ('license_plate', 'ownere', 'vmake', 'model')