from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

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
# GET / UPDATE / DELETE ROUTE BY ID
# =========================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def update_route(request, route_id):
    """
    GET: Get route details by route ID
    PUT/PATCH: Update a route by route ID
    DELETE: Delete a route by route ID
    Both methods support partial updates for flexibility
    """
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return Response(
            {"error": "Route not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Handle DELETE request
    if request.method == 'DELETE':
        route.delete()
        return Response(
            {"message": "Route deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    # Handle GET request
    if request.method == 'GET':
        serializer = RouteSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Handle PUT/PATCH requests
    # Allow partial updates for both PUT and PATCH (more flexible)
    serializer = RouteSerializer(route, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# GET ROUTE BY BUS NUMBER
# =========================
class BusRouteView(APIView):
    """
    GET route + stops for a given bus number (300 / 301)
    """

    def get(self, request, bus_no):
        bus = Bus.objects.filter(bus_number=str(bus_no)).first()
        if not bus:
            return Response(
                {
                    "error": "Bus not found",
                    "bus_number": str(bus_no),
                    "detail": f"Bus number {bus_no} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Check ForeignKey (bus.route)
        route = bus.route
        if not route:
            return Response(
                {
                    "error": "No route assigned",
                    "bus_number": bus.bus_number,
                    "detail": f"No route assigned to bus {bus.bus_number}",
                    "stops": []
                },
                status=status.HTTP_200_OK
            )

        stops = Stop.objects.filter(route=route).order_by("order")
        if not stops.exists():
            return Response(
                {
                    "error": "No stops found",
                    "bus_number": bus.bus_number,
                    "route_name": route.name,
                    "detail": f"No stops found for route {route.name}",
                    "stops": []
                },
                status=status.HTTP_200_OK
            )

        return Response({
            "bus_no": bus.bus_number,
            "stops": [
                {
                    "stop_name": stop.name,
                    "latitude": stop.latitude,
                    "longitude": stop.longitude,
                }
                for stop in stops
            ]
        })
