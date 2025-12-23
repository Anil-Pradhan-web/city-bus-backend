from django.db import models
from buses.models import Bus


class LiveLocation(models.Model):
    """
    Stores current live position of a bus and its route progress.
    One row per bus.
    """

    bus = models.OneToOneField(
        Bus,
        on_delete=models.CASCADE,
        related_name="live_location"
    )

    latitude = models.FloatField(
        help_text="Current latitude of the bus"
    )

    longitude = models.FloatField(
        help_text="Current longitude of the bus"
    )

    current_stop_index = models.IntegerField(
        default=0,
        help_text="Index of the current stop in the route"
    )

    timestamp = models.DateTimeField(
        auto_now=True,
        help_text="Last updated time"
    )

    class Meta:
        verbose_name = "Live Location"
        verbose_name_plural = "Live Locations"

    def __str__(self):
        return f"Bus {self.bus.bus_number} @ ({self.latitude}, {self.longitude})"
