from django.db import models
from django.db import transaction


class Seller(models.Model):
    name = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_balance(self, amount):
        """Check if the seller has enough balance for a transaction."""
        return self.balance >= amount

    @transaction.atomic
    def update_balance(self, amount):
        """
        Update the seller's balance by a given amount.
        Amount can be positive (for credit) or negative (for recharge).
        """
        if amount < 0 and not self.check_balance(-amount):
            raise ValueError("Insufficient balance")

        self.balance += amount
        self.save()

    def __str__(self):
        return f"{self.name} - Balance: {self.balance}"
