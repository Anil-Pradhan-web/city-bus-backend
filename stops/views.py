from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Stop
from .serializers import StopSerializer

class StopListCreateView(generics.ListCreateAPIView):
    queryset = Stop.objects.all().order_by('order')
    serializer_class = StopSerializer


# =========================
# UPDATE / DELETE STOP BY ID
# =========================
@api_view(['PUT', 'PATCH', 'DELETE'])
def update_stop(request, stop_id):
    """
    PUT/PATCH: Update a stop by stop ID
    DELETE: Delete a stop by stop ID
    Both methods support partial updates for flexibility
    """
    try:
        stop = Stop.objects.get(id=stop_id)
    except Stop.DoesNotExist:
        return Response(
            {"error": "Stop not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle DELETE request
    if request.method == 'DELETE':
        stop.delete()
        return Response(
            {"message": "Stop deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    # Handle PUT/PATCH requests
    # Allow partial updates for both PUT and PATCH (more flexible)
    serializer = StopSerializer(stop, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
