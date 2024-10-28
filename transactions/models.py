# transactions/models.py
from django.db import models
from billing.models import BalanceRequest
from sellers.models import Seller


class Transaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    balance_request = models.OneToOneField(
        BalanceRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='credit_transaction',
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save to ensure positive amounts for credit and negative for recharges."""
        if self.transaction_type == self.CREDIT and self.amount < 0:
            raise ValueError("Credit transactions must have a positive amount.")
        elif self.transaction_type == self.DEBIT and self.amount > 0:
            raise ValueError("Debit transactions must have a negative amount.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount} for {self.seller.user.username}"
