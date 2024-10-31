from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import BalanceRequest, Seller, Transaction
from django.db.models import Sum, OuterRef, Subquery


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


def approve_balance_request(pk):
    # Retrieve the balance request object
    balance_request = get_object_or_404(BalanceRequest, pk=pk)

    # Check if the balance request is in "pending" status
    if balance_request.status == BalanceRequest.PENDING:
        balance_request.status = BalanceRequest.APPROVED
        balance_request.save()


def check_db_consistency():
    # Subquery to get the total approved amount for each seller
    approved_amount_subquery = (
        BalanceRequest.objects.filter(
            seller=OuterRef('pk'), status=BalanceRequest.APPROVED
        )
        .values('seller')
        .annotate(total=Sum('amount'))
        .values('total')
    )

    # Subquery to get the total credit amount for each seller
    credit_amount_subquery = (
        Transaction.objects.filter(
            seller=OuterRef('pk'), transaction_type=Transaction.CREDIT
        )
        .values('seller')
        .annotate(total=Sum('amount'))
        .values('total')
    )

    # Subquery to get the total debit amount for each seller
    debit_amount_subquery = (
        Transaction.objects.filter(
            seller=OuterRef('pk'), transaction_type=Transaction.DEBIT
        )
        .values('seller')
        .annotate(total=Sum('amount'))
        .values('total')
    )

    # Now annotate the Seller queryset with these subqueries
    sellers_with_totals = Seller.objects.annotate(
        total_approved_amount=Subquery(approved_amount_subquery),
        total_credit_amount=Subquery(credit_amount_subquery),
        total_debit_amount=Subquery(debit_amount_subquery),
    )

    # Check conditions on balance and transactions results
    for seller in sellers_with_totals:
        total_approved_amount = seller.total_approved_amount or 0
        total_credit_amount = seller.total_credit_amount or 0
        total_debit_amount = seller.total_debit_amount or 0
        balance = seller.balance or 0

        if (total_approved_amount != total_credit_amount) or (
            total_approved_amount + total_debit_amount != balance
        ):
            return False
    return True
