from rest_framework import serializers
from django.utils import timezone
from .models import Election, Candidate, VoteAggregate

class CandidateSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(source="aggregate.count", read_only=True)
    class Meta:
        model = Candidate
        fields = ["id", "number", "name", "photo_url", "count"]

class ElectionPublicSerializer(serializers.ModelSerializer):
    remaining_seconds = serializers.SerializerMethodField()
    candidates = CandidateSerializer(many=True, read_only=True)
    class Meta:
        model = Election
        fields = ["id", "title", "status", "start_at", "end_at", "remaining_seconds", "candidates"]

    def get_remaining_seconds(self, obj):
        if obj.end_at:
            now = timezone.now()
            delta = (obj.end_at - now).total_seconds()
            return max(0, int(delta))
        return 0