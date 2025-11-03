from django.contrib import admin
from .models import Election, Candidate, VoteAggregate, VoteEvent

# Register your models here.

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "start_at", "end_at", "created_at"]

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ["id", "election", "number", "name"]

@admin.register(VoteAggregate)
class VoteAggregateAdmin(admin.ModelAdmin):
    list_display = ["id", "election", "candidate", "count"]

@admin.register(VoteEvent)
class VoteEventAdmin(admin.ModelAdmin):
    list_display = ["id", "election", "candidate", "device_hash", "ip", "created_at"]