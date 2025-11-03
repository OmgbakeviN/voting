from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Election, Candidate, VoteAggregate, VoteEvent
from .serializers import ElectionPublicSerializer

def client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

class ActiveElectionView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        qs = Election.objects.order_by("-created_at")
        e = None
        for item in qs[:5]:
            if item.status != Election.STATUS_CLOSED:
                e = item
                break
        if not e:
            return Response({"election": None})
        return Response({"election": ElectionPublicSerializer(e).data})

class AggregatesView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk):
        e = get_object_or_404(Election, pk=pk)
        data = ElectionPublicSerializer(e).data
        return Response(data)

class OpenElectionView(APIView):
    # permission_classes = [permissions.IsAdminUser]
    def post(self, request, pk):
        e = get_object_or_404(Election, pk=pk)
        now = timezone.now()
        e.start_at = now
        duration = getattr(settings, "ELECTION_WINDOW_SECONDS", 300)
        e.end_at = now + timezone.timedelta(seconds=duration)
        e.status = Election.STATUS_OPEN
        e.save()
        for c in e.candidates.all():
            VoteAggregate.objects.get_or_create(election=e, candidate=c, defaults={"count": 0})
        return Response({"ok": True, "election": ElectionPublicSerializer(e).data})

class CloseElectionView(APIView):
    # permission_classes = [permissions.IsAdminUser]
    def post(self, request, pk):
        e = get_object_or_404(Election, pk=pk)
        e.status = Election.STATUS_CLOSED
        if not e.end_at:
            e.end_at = timezone.now()
        e.save()
        return Response({"ok": True, "election": ElectionPublicSerializer(e).data})

class VoteView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, pk):
        e = get_object_or_404(Election, pk=pk)
        if not e.is_active():
            return Response({"detail": "Voting not active"}, status=status.HTTP_400_BAD_REQUEST)
        candidate_id = request.data.get("candidate_id")
        device_signature = (request.data.get("device_signature") or "").strip()
        if not candidate_id or not device_signature:
            return Response({"detail": "candidate_id and device_signature required"}, status=status.HTTP_400_BAD_REQUEST)
        candidate = get_object_or_404(Candidate, pk=candidate_id, election=e)
        ip = client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]
        with transaction.atomic():
            if VoteEvent.objects.filter(election=e, device_hash=device_signature).exists():
                return Response({"detail": "Already voted"}, status=status.HTTP_409_CONFLICT)
            agg, _ = VoteAggregate.objects.select_for_update().get_or_create(election=e, candidate=candidate, defaults={"count": 0})
            VoteEvent.objects.create(election=e, candidate=candidate, device_hash=device_signature, ip=ip, user_agent=ua)
            agg.count = agg.count + 1
            agg.save()
        data = ElectionPublicSerializer(e).data
        return Response({"ok": True, "election": data})
