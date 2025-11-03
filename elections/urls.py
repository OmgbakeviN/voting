from django.urls import path
from .views import ActiveElectionView, AggregatesView, OpenElectionView, CloseElectionView, VoteView

urlpatterns = [
    path("active/", ActiveElectionView.as_view()),
    path("<int:pk>/aggregates/", AggregatesView.as_view()),
    path("<int:pk>/open/", OpenElectionView.as_view()),
    path("<int:pk>/close/", CloseElectionView.as_view()),
    path("<int:pk>/vote/", VoteView.as_view()),
]
