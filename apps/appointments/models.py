import uuid

from django.db import models

from apps.core.models import TimestampedModel


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    CANCELED = "CANCELED", "Canceled"


class Appointment(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        "professionals.Professional",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )

    class Meta:
        ordering = ["date"]
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"

    def __str__(self) -> str:
        return f"Appointment({self.professional.social_name}, {self.date})"
