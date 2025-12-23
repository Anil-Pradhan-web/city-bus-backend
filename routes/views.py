from rest_framework import generics
from .models import Route
from .serializers import RouteSerializer

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
