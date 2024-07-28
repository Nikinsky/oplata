from rest_framework import serializers
from .models import Plan, Purchase, UserBalance, Transfer

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalance
        fields = '__all__'

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'

    def validate(self, data):
        if data['sender'] == data['recipient']:
            raise serializers.ValidationError("Sender and recipient cannot be the same user.")
        if data['amount'] <= 0:
            raise serializers.ValidationError("Transfer amount must be positive.")
        if data['sender'].userbalance.balance < data['amount']:
            raise serializers.ValidationError("Insufficient funds.")
        return data