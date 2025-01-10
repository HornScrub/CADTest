from django.urls import path
from .views import PlateCheckView

urlpatterns = [
    path('check/', PlateCheckView.as_view(), name='plate_check'),
]
