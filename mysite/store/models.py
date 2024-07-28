from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'

class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.user.username} - Balance: {self.balance}'

    def add_funds(self, amount):
        if amount <= 0:
            raise ValidationError("Amount to add should be positive.")
        self.balance += amount
        self.save()

    def subtract_funds(self, amount):
        if amount > self.balance:
            raise ValidationError("Insufficient funds.")
        self.balance -= amount
        self.save()

class Transfer(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transfers', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_transfers', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transfer from {self.sender.username} to {self.recipient.username} - {self.amount}'

    def save(self, *args, **kwargs):
        if self.sender == self.recipient:
            raise ValidationError("Sender and recipient cannot be the same user.")
        if self.amount <= 0:
            raise ValidationError("Transfer amount must be positive.")
        super().save(*args, **kwargs)
        sender_balance = UserBalance.objects.get(user=self.sender)
        recipient_balance = UserBalance.objects.get(user=self.recipient)
        sender_balance.subtract_funds(self.amount)
        recipient_balance.add_funds(self.amount)
