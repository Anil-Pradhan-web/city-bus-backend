from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Route
from .serializers import RouteSerializer

from buses.models import Bus
from stops.models import Stop


# =========================
# LIST / CREATE ROUTES
# =========================
class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


# =========================
# GET ROUTE BY BUS NUMBER
# =========================
class BusRouteView(APIView):
    """
    GET route + stops for a given bus number (300 / 301)
    """

    def get(self, request, bus_no):
        try:
            bus = Bus.objects.get(bus_number=str(bus_no))
        except Bus.DoesNotExist:
            return Response(
                {"detail": "Bus not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        route = Route.objects.filter(bus=bus).first()
        if not route:
            return Response(
                {"detail": "No route assigned"},
                status=status.HTTP_200_OK
            )

        stops = Stop.objects.filter(route=route).order_by("order")
        if not stops.exists():
            return Response(
                {"detail": "No stops found"},
                status=status.HTTP_200_OK
            )

        return Response({
            "bus_number": bus.bus_number,
            "stops": [
                {
                    "name": stop.name,
                    "latitude": stop.latitude,
                    "longitude": stop.longitude,
                    "order": stop.order
                }
                for stop in stops
            ]
        })
