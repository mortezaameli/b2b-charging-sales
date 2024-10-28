from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Seller


def process_recharge(user, data):
    """Process the recharge and update seller balance."""
    amount = abs(data['amount'])

    with transaction.atomic():
        # Lock the seller record until the transaction is complete
        seller = Seller.objects.select_for_update().get(user=user)

        if not seller.check_balance(amount):
            raise ValidationError("Insufficient balance.")

        # Update balance and create a debit transaction
        seller.update_balance(-amount, 'debit')
