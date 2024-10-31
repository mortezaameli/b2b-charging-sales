from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from billing.models import BalanceRequest, Transaction
from sellers.models import Seller
from rest_framework.test import APIClient
from django.db.models import Sum

User = get_user_model()


class BillingAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.seller = Seller.objects.create(user=self.user, balance=0)
        self.client.force_authenticate(self.user)

    def test_create_balance_request(self):
        url = reverse('balance-request')

        # Create a balance request
        response = self.client.post(url, {'amount': 200}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check has pending status at the beginning
        balance_req = BalanceRequest.objects.get(id=response.data['id'])
        self.assertEqual(balance_req.status, 'pending')

        # approve balance request and check transaction and increace balance happen
        balance_req.status = BalanceRequest.APPROVED
        balance_req.save()

        trx = Transaction.objects.get(
            transaction_type=Transaction.CREDIT, amount=200, balance_request=balance_req
        )
        self.assertEqual(trx.seller, self.seller)

        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 200)

    def test_mobiles_recharge(self):
        url = reverse('recharge_mobile')

        self.seller.balance = 1000
        self.seller.save()

        # Spend all balance and recharge phones
        for _ in range(9):
            response = self.client.post(
                url, {'phone_number': '09181112266', 'amount': 100}, format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if seller balance is consumed
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 100)

        # check DEBIT transaction is saved or not
        trxs = Transaction.objects.filter(
            seller=self.seller, transaction_type=Transaction.DEBIT
        )
        self.assertEqual(len(trxs), 9)

        # Check total charge sales were equal to the initial balance
        sum_spends = 0
        for trx in trxs:
            sum_spends += trx.amount
        self.assertEqual(sum_spends, -900)

        # seller balance is 100 and check can spend 101 ?
        response = self.client.post(
            url, {'phone_number': '09181112266', 'amount': 101}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient balance', response.json().get('error', ''))

        # The seller's balance must not have decreased after the failed charge sale
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 100)


class BillingHighNumberAPIsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpassword1'
        )
        self.seller1 = Seller.objects.create(user=self.user1, balance=0)
        self.client1 = APIClient()
        self.client1.force_authenticate(self.user1)

        self.user2 = User.objects.create_user(
            username='testuser2', password='testpassword2'
        )
        self.seller2 = Seller.objects.create(user=self.user2, balance=0)
        self.client2 = APIClient()
        self.client2.force_authenticate(self.user2)

    def test_create_balance_request(self):
        CREDIT_AMOUNT = 100
        CREDIT_NUM = 20
        SUM_CREDITS = CREDIT_AMOUNT * CREDIT_NUM

        url = reverse('balance-request')

        # Create balance requests
        for _ in range(CREDIT_NUM):
            response1 = self.client1.post(url, {'amount': CREDIT_AMOUNT}, format='json')
            response2 = self.client2.post(url, {'amount': CREDIT_AMOUNT}, format='json')
            self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Check has pending status at the beginning
        balance_reqs1 = BalanceRequest.objects.filter(
            seller=self.seller1, status=BalanceRequest.PENDING
        )
        balance_reqs2 = BalanceRequest.objects.filter(
            seller=self.seller2, status=BalanceRequest.PENDING
        )
        self.assertEqual(len(balance_reqs1), CREDIT_NUM)
        self.assertEqual(len(balance_reqs2), CREDIT_NUM)

        # aproved status of balance requests
        for br in balance_reqs1:
            br.status = BalanceRequest.APPROVED
            br.save()
        for br in balance_reqs2:
            br.status = BalanceRequest.APPROVED
            br.save()

        # now, we dont have any pending balance request
        balance_reqs1 = BalanceRequest.objects.filter(
            seller=self.seller1, status=BalanceRequest.PENDING
        )
        balance_reqs2 = BalanceRequest.objects.filter(
            seller=self.seller2, status=BalanceRequest.PENDING
        )
        self.assertEqual(len(balance_reqs1), 0)
        self.assertEqual(len(balance_reqs2), 0)

        # all pending request change into approved?
        balance_reqs1 = BalanceRequest.objects.filter(
            seller=self.seller1, status=BalanceRequest.APPROVED
        )
        balance_reqs2 = BalanceRequest.objects.filter(
            seller=self.seller2, status=BalanceRequest.APPROVED
        )
        self.assertEqual(len(balance_reqs1), CREDIT_NUM)
        self.assertEqual(len(balance_reqs2), CREDIT_NUM)

        # check for every increase balance register one transaction
        trxs1 = Transaction.objects.filter(
            seller=self.seller1,
            transaction_type=Transaction.CREDIT,
        )
        trxs2 = Transaction.objects.filter(
            seller=self.seller2,
            transaction_type=Transaction.CREDIT,
        )
        self.assertEqual(len(trxs1), CREDIT_NUM)
        self.assertEqual(len(trxs2), CREDIT_NUM)

        # check sum amount of all transactions
        total_amount1 = trxs1.aggregate(total=Sum('amount'))['total'] or 0
        total_amount2 = trxs2.aggregate(total=Sum('amount'))['total'] or 0
        self.assertEqual(total_amount1, SUM_CREDITS)
        self.assertEqual(total_amount2, SUM_CREDITS)

        # check seller balance update correctly?
        self.seller1.refresh_from_db()
        self.seller2.refresh_from_db()
        self.assertEqual(self.seller1.balance, SUM_CREDITS)
        self.assertEqual(self.seller2.balance, SUM_CREDITS)

    def test_mobiles_recharge(self):
        START_BALANCE = 2000
        RECHARGE_NUM = 500
        RECHARGE_AMOUNT = 4
        url = reverse('recharge_mobile')

        #  set START_BALANCE for init balance of sellers
        self.seller1.balance = START_BALANCE
        self.seller1.save()
        self.seller2.balance = START_BALANCE
        self.seller2.save()

        # Spend all balance and recharge phones
        for _ in range(RECHARGE_NUM):
            response1 = self.client1.post(
                url,
                {'phone_number': '09181112266', 'amount': RECHARGE_AMOUNT},
                format='json',
            )
            response2 = self.client2.post(
                url,
                {'phone_number': '09181112266', 'amount': RECHARGE_AMOUNT},
                format='json',
            )
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # check if sellers balance is consumed?
        self.seller1.refresh_from_db()
        self.seller2.refresh_from_db()
        self.assertEqual(self.seller1.balance, 0)
        self.assertEqual(self.seller1.balance, 0)

        # check DEBIT transaction is saved or not
        trxs1 = Transaction.objects.filter(
            seller=self.seller1, transaction_type=Transaction.DEBIT
        )
        trxs2 = Transaction.objects.filter(
            seller=self.seller2, transaction_type=Transaction.DEBIT
        )
        self.assertEqual(len(trxs1), RECHARGE_NUM)
        self.assertEqual(len(trxs2), RECHARGE_NUM)

        # Check total charge sales were equal to the initial balance
        total_amount1 = trxs1.aggregate(total=Sum('amount'))['total'] or 0
        total_amount2 = trxs2.aggregate(total=Sum('amount'))['total'] or 0
        self.assertEqual(total_amount1, -START_BALANCE)
        self.assertEqual(total_amount2, -START_BALANCE)

        # The seller's balance must not have decreased after the failed charge sale
        self.seller1.refresh_from_db()
        self.seller2.refresh_from_db()
        self.assertEqual(self.seller1.balance, 0)
        self.assertEqual(self.seller1.balance, 0)

        # seller balance is 0 and check can spend another sale ?
        response1 = self.client1.post(
            url, {'phone_number': '09181112266', 'amount': 1}, format='json'
        )
        response2 = self.client2.post(
            url, {'phone_number': '09181112266', 'amount': 1}, format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient balance', response1.json().get('error', ''))
        self.assertIn('Insufficient balance', response2.json().get('error', ''))
