from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.apps import apps


class Seller(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile",
        null=True,
        blank=True,
    )
    balance = models.DecimalField(max_digits=11, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_balance(self, amount):
        """Check if the seller has enough balance for a transaction."""
        return self.balance >= amount

    @transaction.atomic
    def update_balance(self, amount, transaction_type, balance_request=None):
        
        if transaction_type == 'debit' and not self.check_balance(amount): # TODO: dont use hardcode
            raise ValueError("Insufficient balance")

        # Update balance
        self.balance += amount if transaction_type == 'credit' else -amount # TODO: dont use hardcode
        self.save()

        # Log the transaction with lazy loading of the Transaction model
        Transaction = apps.get_model('transactions', 'Transaction')
        Transaction.objects.create(
            seller=self,
            transaction_type=transaction_type,
            amount=abs(amount),
            description=f"{transaction_type.capitalize()} of {amount} processed.",
            balance_request=balance_request
        )


    def __str__(self):
        # return f"{self.user.username} - Balance({self.balance})"
        return f"{self.user.username}"
