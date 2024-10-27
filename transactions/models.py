# transactions/models.py
from django.db import models
from sellers.models import Seller


class Transaction(models.Model):
    CREDIT = 'credit'
    RECHARGE = 'recharge'
    TRANSACTION_TYPES = [
        (CREDIT, 'Credit'),
        (RECHARGE, 'Recharge'),
    ]

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save to ensure positive amounts for credit and negative for recharges."""
        if self.transaction_type == self.CREDIT and self.amount < 0:
            raise ValueError("Credit transactions must have a positive amount.")
        elif self.transaction_type == self.RECHARGE and self.amount > 0:
            raise ValueError("Recharge transactions must have a negative amount.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount} for {self.seller.name}"
