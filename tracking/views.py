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
        buses = Bus.objects.filter(bus_number=str(bus_no)).select_related('route')
        if not buses.exists():
            return Response({"detail": "Bus not found"}, status=404)

        results = []

        for bus in buses:
            live = LiveLocation.objects.filter(bus=bus).first()
            if not live:
                continue

            # Check ForeignKey (bus.route)
            route = bus.route
            if not route:
                continue

            stops = list(Stop.objects.filter(route=route).order_by("order"))
            if not stops:
                continue

            current_index = live.current_stop_index
            forward = live.is_moving_forward
            total_stops = len(stops)
            next_index = current_index

            if total_stops > 1:
                if forward:
                    if current_index < total_stops - 1:
                        next_index = current_index + 1
                    else:
                        next_index = current_index - 1
                else:
                    if current_index > 0:
                        next_index = current_index - 1
                    else:
                        next_index = current_index + 1

            current_stop = stops[current_index]
            next_stop = stops[next_index]

            distance_km = haversine(
                live.latitude,
                live.longitude,
                next_stop.latitude,
                next_stop.longitude
            )

            eta_minutes = max(1, round((distance_km / self.AVG_SPEED_KMPH) * 60))

            results.append({
                "bus_id": bus.id,
                "bus_no": bus.bus_number,
                "current_stop": current_stop.name,
                "next_stop": next_stop.name,
                "distance_km": round(distance_km, 2),
                "eta_minutes": eta_minutes,
                "is_moving_forward": forward
            })

        return Response(results)


# =========================
# BUS ROUTE (POLYLINE)
# =========================
class BusRouteView(APIView):
    """
    GET: Returns ordered stops for a bus route
    """
    def get(self, request, bus_no):
        # We assume all buses with the same number share the same route
        bus = Bus.objects.filter(bus_number=str(bus_no)).select_related('route').first()
        if not bus:
            return Response({"detail": "Bus not found"}, status=404)

        # Check ForeignKey (bus.route)
        route = bus.route
        if not route:
            return Response({"detail": "No route assigned"}, status=200)

        stops = Stop.objects.filter(route=route).order_by("order")
        if not stops.exists():
            return Response({"detail": "No stops found"}, status=200)

        return Response({
            "bus_number": bus.bus_number,
            "stops": [
                {
                    "stop_name": s.name,  # changed from 'name' to 'stop_name'
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
        buses = Bus.objects.filter(bus_number=str(bus_no)).select_related('route')
        if not buses.exists():
            return Response({"error": "Bus not found"}, status=404)

        results = []

        now = timezone.now()

        for bus in buses:
            # Check ForeignKey (bus.route)
            route = bus.route
            if not route:
                results.append({"bus_id": bus.id, "error": "Route not assigned"})
                continue

            stops = list(Stop.objects.filter(route=route).order_by("order"))
            if not stops:
                results.append({"bus_id": bus.id, "error": "No stops found"})
                continue

            live, _ = LiveLocation.objects.get_or_create(
                bus=bus,
                defaults={
                    "latitude": stops[0].latitude,
                    "longitude": stops[0].longitude,
                    "current_stop_index": 0,
                }
            )

            # 🔒 LOCK START
            if live.last_moved_at and (now - live.last_moved_at) < timedelta(seconds=10):
                results.append({
                    "bus_id": bus.id,
                    "bus_no": bus.bus_number,
                    "latitude": live.latitude,
                    "longitude": live.longitude,
                    "stop_name": stops[live.current_stop_index].name,
                    "stop_index": live.current_stop_index,
                    "is_moving_forward": live.is_moving_forward,
                    "locked": True,
                })
                continue
            # 🔒 LOCK END

            # ✅ SAFE MOVE (PING-PONG)
            total_stops = len(stops)
            current = live.current_stop_index
            forward = live.is_moving_forward

            if total_stops > 1:
                if forward:
                    if current < total_stops - 1:
                        next_index = current + 1
                    else:
                        # Turned around at End
                        forward = False
                        next_index = current - 1
                else:
                    if current > 0:
                        next_index = current - 1
                    else:
                        # Turned around at Start
                        forward = True
                        next_index = current + 1
            else:
                next_index = current

            # Safety Fallback
            if next_index < 0: next_index = 0
            if next_index >= total_stops: next_index = total_stops - 1

            next_stop = stops[next_index]

            live.latitude = next_stop.latitude
            live.longitude = next_stop.longitude
            live.current_stop_index = next_index
            live.is_moving_forward = forward
            live.last_moved_at = now
            live.save()

            results.append({
                "bus_id": bus.id,
                "bus_no": bus.bus_number,
                "latitude": live.latitude,
                "longitude": live.longitude,
                "stop_name": next_stop.name,
                "stop_index": next_index,
                "is_moving_forward": forward,
                "locked": False,
            })

        return Response(results)
