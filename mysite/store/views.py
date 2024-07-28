from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Plan, Purchase, UserBalance, Transfer
from .serializers import PlanSerializer, PurchaseSerializer, UserBalanceSerializer, TransferSerializer
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]

class PurchaseCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        try:
            user_balance = UserBalance.objects.get(user=user)
        except UserBalance.DoesNotExist:
            return Response({"error": "User balance not found"}, status=status.HTTP_404_NOT_FOUND)

        if user_balance.balance < plan.price:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        expiration_date = datetime.now() + timedelta(days=plan.duration_days)
        user_balance.subtract_funds(plan.price)

        purchase = Purchase.objects.create(user=user, plan=plan, expiration_date=expiration_date)
        serializer = PurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except UserBalance.DoesNotExist:
            return Response({"error": "User balance not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserBalanceSerializer(user_balance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except UserBalance.DoesNotExist:
            user_balance = UserBalance.objects.create(user=request.user, balance=0.00)

        user_balance.add_funds(amount)
        serializer = UserBalanceSerializer(user_balance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {
            'sender': request.user.id,
            'recipient': request.data.get('recipient_id'),
            'amount': request.data.get('amount')
        }
        serializer = TransferSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)