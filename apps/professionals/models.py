import re
import uuid

from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import TimestampedModel


class Professional(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_name = models.CharField(max_length=255, unique=True)
    profession = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[\d\s\(\)-]{8,20}$",
                message="""O contato deve estar em um formato válido.
                Ex: (11) 91234-5678""",
            )
        ],
    )

    class Meta:
        ordering = ["social_name"]
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"

    def save(self, *args, **kwargs):
        if self.contact:
            # Mantém apenas os dígitos
            self.contact = re.sub(r"\D", "", str(self.contact))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.social_name} — {self.profession}"
