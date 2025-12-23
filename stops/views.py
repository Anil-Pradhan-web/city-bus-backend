from rest_framework import generics
from .models import Stop
from .serializers import StopSerializer

class StopListCreateView(generics.ListCreateAPIView):
    queryset = Stop.objects.all().order_by('order')
    serializer_class = StopSerializer
