# ads/urls.py

from django.urls import path
from .views import (
    AdListView,
    AdDetailView,
    AdCreateView,
    AdUpdateView,
    AdDeleteView,
    ProposalCreateView,
    ProposalListView,
    update_proposal_status
)

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/new/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),

    # Маршруты для предложений
    path('proposals/', ProposalListView.as_view(), name='proposal_list'),
    path('ad/<int:ad_receiver_id>/propose/', ProposalCreateView.as_view(), name='proposal_create'),
    path('proposal/<int:pk>/<str:status>/', update_proposal_status, name='proposal_update_status'),
]