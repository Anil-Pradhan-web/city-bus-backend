from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Bus
from .serializers import BusSerializer   # 🔥 ye import important hai

class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer


# =========================
# UPDATE / DELETE BUS BY ID
# =========================
@api_view(['PUT', 'PATCH', 'DELETE'])
def update_bus(request, bus_id):
    """
    PUT/PATCH: Update a bus by bus ID
    DELETE: Delete a bus by bus ID
    Both methods support partial updates for flexibility
    """
    try:
        bus = Bus.objects.get(id=bus_id)
    except Bus.DoesNotExist:
        return Response(
            {"error": "Bus not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle DELETE request
    if request.method == 'DELETE':
        bus.delete()
        return Response(
            {"message": "Bus deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    # Handle PUT/PATCH requests
    # Allow partial updates for both PUT and PATCH (more flexible)
    serializer = BusSerializer(bus, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
