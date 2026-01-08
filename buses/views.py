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


# =========================
# GET BUS SCHEDULE
# =========================
@api_view(['GET'])
def get_bus_schedule(request, bus_no):
    """
    GET: Returns schedule for a bus
    Format: [{"time": "08:00 AM", "stop": "Name", "type": "Start"}, ...]
    """
    try:
        # Get the first bus with this number (assuming schedules are similar if multiple)
        # Or better, fetch all schedules for this bus number
        # Dealing with duplicate buses: We pick one to show schedule.
        bus = Bus.objects.filter(bus_number=str(bus_no)).first()
        if not bus:
            return Response({"error": "Bus not found"}, status=404)
        
        schedules = list(bus.schedules.all().order_by('arrival_time'))
        
        results = []
        total = len(schedules)
        
        for index, sch in enumerate(schedules):
            # Determine Type
            if index == 0:
                stop_type = "Start"
            elif index == total - 1:
                stop_type = "End"
            else:
                stop_type = "Stop"
            
            results.append({
                "time": sch.arrival_time.strftime("%I:%M %p"), # 12-hour format with AM/PM
                "stop": sch.stop.name,
                "type": stop_type
            })
            
        return Response(results)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
