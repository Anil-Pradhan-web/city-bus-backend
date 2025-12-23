from rest_framework import generics
from .models import Bus
from .serializers import BusSerializer   # 🔥 ye import important hai

class BusListCreateView(generics.ListCreateAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
