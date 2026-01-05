from django.db import models

class Bus(models.Model):
    bus_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    route = models.ForeignKey('routes.Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')

    def __str__(self):
        return f"Bus {self.bus_number} ({self.route.name if self.route else 'No Route'})"
