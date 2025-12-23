from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LiveLocation
from .serializers import LiveLocationSerializer
from buses.models import Bus

class UpdateLocationView(APIView):
    """
    POST: driver/simulator sends latest lat/lng
    """
    def post(self, request):
        serializer = LiveLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentLocationView(APIView):
    """
    GET: frontend fetches current bus location
    """
    def get(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            return Response({"detail": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

        location = bus.locations.order_by('-timestamp').first()
        if not location:
            return Response({"detail": "No live location yet"}, status=status.HTTP_200_OK)

        serializer = LiveLocationSerializer(location)
        return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from buses.models import Bus
from .models import LiveLocation
from routes.models import Route
from stops.models import Stop
from .utils import haversine


class BusETAView(APIView):
    """
    GET: Returns next stop and ETA (in minutes) for a bus
    """
    AVG_SPEED_KMPH = 30  # assumed average city speed

    def get(self, request, bus_id):
        # 1. Get bus
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            return Response({"detail": "Bus not found"}, status=status.HTTP_404_NOT_FOUND)

        # 2. Latest live location
        location = LiveLocation.objects.filter(bus=bus).order_by('-timestamp').first()
        if not location:
            return Response({"detail": "No live location yet"}, status=status.HTTP_200_OK)

        # 3. Route
        route = Route.objects.filter(bus=bus).first()
        if not route:
            return Response({"detail": "No route assigned"}, status=status.HTTP_200_OK)

        # 4. Stops (ordered)
        stops = Stop.objects.filter(route=route).order_by('order')
        if not stops.exists():
            return Response({"detail": "No stops found"}, status=status.HTTP_200_OK)

        # 5. Find nearest next stop
        next_stop = None
        min_distance = None

        for stop in stops:
            distance = haversine(
                location.latitude, location.longitude,
                stop.latitude, stop.longitude
            )
            if min_distance is None or distance < min_distance:
                min_distance = distance
                next_stop = stop

        # 6. ETA calculation
        eta_hours = min_distance / self.AVG_SPEED_KMPH
        eta_minutes = max(1, round(eta_hours * 60))

        return Response({
            "bus_id": bus.id,
            "next_stop": next_stop.name,
            "distance_km": round(min_distance, 2),
            "eta_minutes": eta_minutes
        })
from django.conf import settings
AVG_SPEED_KMPH = getattr(settings, 'AVG_BUS_SPEED_KMPH', 30)
