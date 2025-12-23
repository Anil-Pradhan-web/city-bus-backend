from django.db import models
from buses.models import Bus

class LiveLocation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bus {self.bus.bus_number} @ {self.timestamp}"
