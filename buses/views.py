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
        from datetime import datetime, timedelta
        from stops.models import Stop
        
        # Try to get bus and its route from database
        bus = Bus.objects.filter(bus_number=str(bus_no)).select_related('route').first()
        
        if bus and bus.route:
            # Get stops from database
            stops = list(Stop.objects.filter(route=bus.route).order_by('order'))
            
            if stops:
                # Generate schedule dynamically from database stops
                results = []
                
                # Start time (6:00 AM)
                start_time = datetime.strptime("06:00 AM", "%I:%M %p")
                interval_minutes = 10  # 10 minutes between stops
                
                # Forward journey (Start to End)
                current_time = start_time
                total_stops = len(stops)
                
                for index, stop in enumerate(stops):
                    if index == 0:
                        stop_type = "Start"
                    elif index == total_stops - 1:
                        stop_type = "End"
                    else:
                        stop_type = "Stop"
                    
                    results.append({
                        "time": current_time.strftime("%I:%M %p"),
                        "stop": stop.name,
                        "type": stop_type
                    })
                    
                    current_time += timedelta(minutes=interval_minutes)
                
                # Add 30 minute break at end stop
                current_time += timedelta(minutes=15)
                
                # Return journey (End to Start)
                for index in range(total_stops - 1, -1, -1):
                    stop = stops[index]
                    
                    if index == total_stops - 1:
                        stop_type = "Start"
                    elif index == 0:
                        stop_type = "End"
                    else:
                        stop_type = "Stop"
                    
                    results.append({
                        "time": current_time.strftime("%I:%M %p"),
                        "stop": stop.name,
                        "type": stop_type
                    })
                    
                    current_time += timedelta(minutes=interval_minutes)
                
                return Response(results)
        
        # Fallback schedules if no database stops found
        FALLBACK_SCHEDULES = {
            "200": [
                {"time": "06:00 AM", "stop": "Puri Beach", "type": "Start"},
                {"time": "06:15 AM", "stop": "Swargadwar", "type": "Stop"},
                {"time": "06:30 AM", "stop": "Sea Beach Road", "type": "Stop"},
                {"time": "06:45 AM", "stop": "Grand Road", "type": "Stop"},
                {"time": "07:00 AM", "stop": "Gundicha Temple", "type": "Stop"},
                {"time": "07:15 AM", "stop": "Balagandi", "type": "Stop"},
                {"time": "07:30 AM", "stop": "Puri Railway Station", "type": "Stop"},
                {"time": "07:45 AM", "stop": "Jagannath Temple", "type": "End"},
                {"time": "08:15 AM", "stop": "Jagannath Temple", "type": "Start"},
                {"time": "08:30 AM", "stop": "Puri Railway Station", "type": "Stop"},
                {"time": "08:45 AM", "stop": "Balagandi", "type": "Stop"},
                {"time": "09:00 AM", "stop": "Grand Road", "type": "Stop"},
                {"time": "09:15 AM", "stop": "Sea Beach Road", "type": "Stop"},
                {"time": "09:30 AM", "stop": "Swargadwar", "type": "Stop"},
                {"time": "09:45 AM", "stop": "Puri Beach", "type": "End"},
            ],
            "100": [
                {"time": "07:00 AM", "stop": "Bhubaneswar Station", "type": "Start"},
                {"time": "07:20 AM", "stop": "Kalpana Square", "type": "Stop"},
                {"time": "07:40 AM", "stop": "Patia", "type": "Stop"},
                {"time": "08:00 AM", "stop": "Nandankanan", "type": "End"},
            ],
            "300": [
                {"time": "06:30 AM", "stop": "Berhampur Bus Stand", "type": "Start"},
                {"time": "06:50 AM", "stop": "Silk City", "type": "Stop"},
                {"time": "07:10 AM", "stop": "Gopalpur", "type": "End"},
            ],
            "301": [
                {"time": "07:00 AM", "stop": "Berhampur University", "type": "Start"},
                {"time": "07:25 AM", "stop": "Berhampur Market", "type": "Stop"},
                {"time": "07:50 AM", "stop": "Berhampur Station", "type": "End"},
            ]
        }
        
        # Use fallback schedule if available
        if str(bus_no) in FALLBACK_SCHEDULES:
            return Response(FALLBACK_SCHEDULES[str(bus_no)])
        
        # No schedule found
        return Response({"error": "No schedule available for this bus"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
