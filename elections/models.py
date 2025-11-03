from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

# Create your models here.

class Election(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_OPEN = "OPEN"
    STATUS_CLOSED = "CLOSED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "PENDING"),
        (STATUS_OPEN, "OPEN"),
        (STATUS_CLOSED, "CLOSED"),
    ]
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        now = timezone.now()
        return self.status == self.STATUS_OPEN and self.start_at and self.end_at and self.start_at <= now <= self.end_at

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    name = models.CharField(max_length=200)
    photo_url = models.URLField(blank=True, default="")
    bio = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("election", "number")]

class VoteAggregate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="aggregates")
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="aggregate")
    count = models.PositiveIntegerField(default=0)

class VoteEvent(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="votes")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    device_hash = models.CharField(max_length=128)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["election", "device_hash"]),
        ]
        unique_together = [("election", "device_hash")]

