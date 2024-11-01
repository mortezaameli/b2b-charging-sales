from django.db import models, transaction
from sellers.models import Seller
from django.apps import apps


class BalanceRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name='balancerequests'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve_request(self):
        """Approve the balance request and update seller balance with logging."""

        # Check if any transactions already exist for this balance request
        if hasattr(self, 'credit_transaction') and self.credit_transaction is not None:
            return

        self.seller.update_balance(self.amount, 'credit', balance_request=self)
        self.status = self.APPROVED

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:  # Check if this is an update (i.e., not a new object)
            old_status = BalanceRequest.objects.get(pk=self.pk).status
            if old_status != self.status and self.status == self.APPROVED:
                self.approve_request()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seller.user.username} - {self.amount} ({self.status})"

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
