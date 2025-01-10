from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vehicle
from .serializers import VehicleSerializer

## Test Views ##


class PlateCheckView(APIView):
    '''
    Usage: GET /api/plate_check?license_plate={license_plate}

    Vehicle Model:

    license_plate
        owner_name
        owner_address
        vehicle_make
        vehicle_model
        is_stolen
        outstanding_warrants

    Example:
        
        Input: GET /api/plate_check?license_plate=ABC123
        
        Output: {
        "id": 1,
        "license_plate": "ABC123",
        "owner_name": "John Doe",
        "owner_address": "123 N Street\r\nAustin TX\r\n78723",
        "vehicle_make": "Ford",
        "vehicle_model": "Focus",
        "is_stolen": false,
        "outstanding_warrants": ""
        }
    '''
    def get(self, request, *args, **kwargs):
        # Get the 'license_plate' parameter from the query string
        license_plate = request.query_params.get('license_plate')
        if not license_plate:
            return Response({'error': 'License plate is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the vehicle with the specified license plate
            vehicle = Vehicle.objects.get(license_plate=license_plate.upper())
            serializer = VehicleSerializer(vehicle)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)