from rest_framework import serializers
from .models import LiveLocation

class LiveLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveLocation
        fields = ['id', 'bus', 'latitude', 'longitude', 'current_stop_index', 'is_moving_forward', 'timestamp']
