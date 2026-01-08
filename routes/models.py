from django.db import models
from buses.models import Bus

class Route(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self):
        return self.name
