from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from buses.models import Bus
from routes.models import Route
from stops.models import Stop
from .models import LiveLocation
from .serializers import LiveLocationSerializer
from .utils import haversine
from django.utils import timezone
from datetime import timedelta


# =========================
# UPDATE LIVE LOCATION
# =========================
class UpdateLocationView(APIView):
    """
    POST: driver/simulator sends latest lat/lng
    """
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = LiveLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# CURRENT BUS LOCATION
# =========================
class CurrentLocationView(APIView):
    """
    GET: frontend fetches current bus location
    """
    def get(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id)
        except Bus.DoesNotExist:
            return Response(
                {"detail": "Bus not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        location = LiveLocation.objects.filter(bus=bus).first()
        if not location:
            return Response(
                {"detail": "No live location yet"},
                status=status.HTTP_200_OK
            )

        serializer = LiveLocationSerializer(location)
        return Response(serializer.data)


# =========================
# BUS ETA (SIMPLE)
# =========================
class BusETAView(APIView):
    """
    GET: Returns next stop and ETA (in minutes)
    """

    AVG_SPEED_KMPH = 28

    def get(self, request, bus_no):
        try:
            bus = Bus.objects.get(bus_number=str(bus_no))
        except Bus.DoesNotExist:
            return Response({"detail": "Bus not found"}, status=404)

        live = LiveLocation.objects.filter(bus=bus).first()
        if not live:
            return Response({"detail": "No live location yet"}, status=200)

        route = Route.objects.filter(bus=bus).first()
        if not route:
            return Response({"detail": "No route assigned"}, status=200)

        stops = list(Stop.objects.filter(route=route).order_by("order"))
        if not stops:
            return Response({"detail": "No stops found"}, status=200)

        current_index = live.current_stop_index
        next_index = (current_index + 1) % len(stops)

        current_stop = stops[current_index]
        next_stop = stops[next_index]

        distance_km = haversine(
            live.latitude,
            live.longitude,
            next_stop.latitude,
            next_stop.longitude
        )

        eta_minutes = max(1, round((distance_km / self.AVG_SPEED_KMPH) * 60))

        return Response({
            "bus_no": bus.bus_number,
            "current_stop": current_stop.name,
            "next_stop": next_stop.name,
            "distance_km": round(distance_km, 2),
            "eta_minutes": eta_minutes
        })


# =========================
# BUS ROUTE (POLYLINE)
# =========================
class BusRouteView(APIView):
    """
    GET: Returns ordered stops for a bus route
    """
    def get(self, request, bus_no):
        try:
            bus = Bus.objects.get(bus_number=str(bus_no))
        except Bus.DoesNotExist:
            return Response({"detail": "Bus not found"}, status=404)

        route = Route.objects.filter(bus=bus).first()
        if not route:
            return Response({"detail": "No route assigned"}, status=200)

        stops = Stop.objects.filter(route=route).order_by("order")
        if not stops.exists():
            return Response({"detail": "No stops found"}, status=200)

        return Response({
            "bus_number": bus.bus_number,
            "stops": [
                {
                    "name": s.name,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "order": s.order
                }
                for s in stops
            ]
        })


# =========================
# MOVE BUS (SIMPLE CIRCULAR)
# =========================
class MoveBusView(APIView):
    """
    POST: Simulates bus moving stop-by-stop safely (LOCKED)
    """
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, bus_no):
        try:
            bus = Bus.objects.get(bus_number=str(bus_no))
        except Bus.DoesNotExist:
            return Response({"error": "Bus not found"}, status=404)

        route = Route.objects.filter(bus=bus).first()
        if not route:
            return Response({"error": "Route not assigned"}, status=404)

        stops = list(Stop.objects.filter(route=route).order_by("order"))
        if not stops:
            return Response({"error": "No stops found"}, status=404)

        live, _ = LiveLocation.objects.get_or_create(
            bus=bus,
            defaults={
                "latitude": stops[0].latitude,
                "longitude": stops[0].longitude,
                "current_stop_index": 0,
            }
        )

        # 🔒 LOCK START
        now = timezone.now()
        if live.last_moved_at and (now - live.last_moved_at) < timedelta(seconds=10):
            # ❌ ignore duplicate request
            return Response({
                "bus_no": bus.bus_number,
                "latitude": live.latitude,
                "longitude": live.longitude,
                "stop_name": stops[live.current_stop_index].name,
                "stop_index": live.current_stop_index,
                "locked": True,
            })
        # 🔒 LOCK END

        # ✅ SAFE MOVE
        next_index = (live.current_stop_index + 1) % len(stops)
        next_stop = stops[next_index]

        live.latitude = next_stop.latitude
        live.longitude = next_stop.longitude
        live.current_stop_index = next_index
        live.last_moved_at = now   # 🔒 update time
        live.save()

        return Response({
            "bus_no": bus.bus_number,
            "latitude": live.latitude,
            "longitude": live.longitude,
            "stop_name": next_stop.name,
            "stop_index": next_index,
            "locked": False,
        })
