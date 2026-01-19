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

    # 🔒 ADD THIS FIELD (IMPORTANT)
    last_moved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Prevents duplicate move calls"
    )

    is_moving_forward = models.BooleanField(
        default=True,
        help_text="True = Start to End, False = End to Start"
    )

    speed = models.IntegerField(
        default=40,
        help_text="Current speed in km/h"
    )

    crowding = models.CharField(
        max_length=10,
        default="Medium",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        help_text="Current crowding level"
    )

    stop_arrival_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time when bus arrived at current stop (for 2-second delay)"
    )

    class Meta:
        verbose_name = "Live Location"
        verbose_name_plural = "Live Locations"

    def __str__(self):
        return f"Bus {self.bus.bus_number} @ ({self.latitude}, {self.longitude})"
