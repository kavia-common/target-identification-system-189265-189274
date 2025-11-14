from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Target(TimeStampedModel):
    """A target entity for identification and analysis."""
    class Status(models.TextChoices):
        NEW = "new", _("New")
        UNDER_REVIEW = "under_review", _("Under Review")
        CONFIRMED = "confirmed", _("Confirmed")
        REJECTED = "rejected", _("Rejected")

    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    priority = models.PositiveIntegerField(default=0, db_index=True)
    tags = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated tags string. e.g. 'alpha,beta,gamma'",
        db_index=True,
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["confidence"]),
            models.Index(fields=["updated_at"]),
        ]
        ordering = ["-updated_at", "-priority", "-confidence"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class Source(TimeStampedModel):
    """Information source for indicators."""
    class SourceType(models.TextChoices):
        OSINT = "osint", _("OSINT")
        SIGINT = "sigint", _("SIGINT")
        HUMINT = "humint", _("HUMINT")
        OTHER = "other", _("Other")

    name = models.CharField(max_length=255, unique=True, db_index=True)
    type = models.CharField(max_length=10, choices=SourceType.choices, db_index=True)
    url = models.URLField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


class Indicator(TimeStampedModel):
    """An indicator extracted from a source."""
    class IndicatorType(models.TextChoices):
        KEYWORD = "keyword", _("Keyword")
        PATTERN = "pattern", _("Pattern")
        FEATURE = "feature", _("Feature")

    type = models.CharField(max_length=10, choices=IndicatorType.choices, db_index=True)
    value = models.TextField(db_index=True)
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
        db_index=True,
    )
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="indicators", db_index=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["score"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at", "-score"]

    def __str__(self) -> str:
        return f"{self.type}:{self.value[:30]}..."


class Association(TimeStampedModel):
    """Link between a Target and an Indicator with rationale/notes."""
    target = models.ForeignKey(
        Target, on_delete=models.CASCADE, related_name="associations", db_index=True
    )
    indicator = models.ForeignKey(
        Indicator, on_delete=models.CASCADE, related_name="associations", db_index=True
    )
    rationale = models.TextField(blank=True, default="")
    analyst_notes = models.TextField(blank=True, default="")
    weight = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["target", "indicator"]),
            models.Index(fields=["target", "weight"]),
        ]
        unique_together = ("target", "indicator")
        ordering = ["-created_at", "-weight"]

    def __str__(self) -> str:
        return f"Assoc(Target={self.target_id}, Indicator={self.indicator_id}, weight={self.weight})"
