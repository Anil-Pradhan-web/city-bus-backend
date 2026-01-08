from django.db import models

class Bus(models.Model):
    bus_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    route = models.ForeignKey('routes.Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"Bus {self.bus_number} ({self.route.name if self.route else 'No Route'})"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    stop = models.ForeignKey('stops.Stop', on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    
    class Meta:
        ordering = ['arrival_time']
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def __str__(self):
        return f"{self.bus.bus_number} at {self.stop.name} ({self.arrival_time})"
