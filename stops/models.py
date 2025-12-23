from django.db import models
from routes.models import Route

class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.name
