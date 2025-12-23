from django.db import models

class Bus(models.Model):
    bus_number = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Bus {self.bus_number}"

