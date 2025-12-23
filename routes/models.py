from django.db import models
from buses.models import Bus

class Route(models.Model):
    name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
