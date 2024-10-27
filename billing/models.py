# billing/models.py
from django.db import models, transaction
from sellers.models import Seller


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
    amount = models.DecimalField(max_digits=15, decimal_places=2)
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
