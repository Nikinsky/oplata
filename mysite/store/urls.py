from django.urls import path
from .views import PlanListView, PurchaseCreateView, UserBalanceView, TransferView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('purchase/', PurchaseCreateView.as_view(), name='purchase-create'),
    path('balance/', UserBalanceView.as_view(), name='user-balance'),
    path('transfer/', TransferView.as_view(), name='transfer'),
]