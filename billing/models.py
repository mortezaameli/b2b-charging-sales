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

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve_request(self):
        """Approve the balance request and update seller balance with logging."""

        # Check if any transactions already exist for this balance request
        if hasattr(self, 'credit_transaction') and self.credit_transaction is not None:
            raise ValueError("This balance request has already been processed.")

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


class RechargeRequest(models.Model):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name='recharge_requests'
    )
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def process_recharge(self):
        """Process the recharge request and update seller balance."""
        # Ensure recharge hasn't already succeeded
        if self.status != self.PENDING:
            raise ValueError("Recharge request has already been processed.")

        # Check seller's balance
        if not self.seller.check_balance(self.amount):
            self.status = self.FAILED
            self.save()
            raise ValueError("Insufficient balance for recharge.")

        # Deduct balance and mark as success
        self.seller.update_balance(-self.amount)
        self.status = self.SUCCESS
        self.save()

    def __str__(self):
        return f"Recharge {self.amount} for {self.phone_number} - Status: {self.status}"
