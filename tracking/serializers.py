from rest_framework import serializers
from .models import LiveLocation

class LiveLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveLocation
        fields = ['id', 'bus', 'latitude', 'longitude', 'timestamp']
