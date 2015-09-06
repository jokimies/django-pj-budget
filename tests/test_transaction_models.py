import datetime
from decimal import Decimal

# 3rd party
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

# Own
from .factories import *
from budget.transactions.models import Transaction
from .basetest import TestBase

class TransactionModelTest(TestCase):

    longMessage = True

    def create_transactions(self):

        txn1 = TransactionFactory(amount=amount1, 
                                  date=datetime.datetime(2008, 2, 1))
        txn2 = TransactionFactory(amount=amount2, 
                                  date=datetime.datetime(2008, 2, 28))
        txn3 = TransactionFactory(amount=amount3, 
                                  date=datetime.datetime(2008, 1, 28))

        return txn1, txn2, txn3

    def test_saving_retrieving_transactions(self):
        txn1 = TransactionFactory(amount=28.65, 
                                  date=datetime.datetime(2008, 1, 1))
        transactions = Transaction.objects.all()

        self.assertEqual(transactions.count(), 1, 
                         'Should be one transactions in db')

        
    def test_actual_total(self):
        amount1 = Decimal('28.65')
        amount2 = Decimal('36.12')
        amount3 = 1.6
        start_year = 2008
        start_month = 2

        txn1 = TransactionFactory(amount=amount1, 
                                  date=datetime.datetime(2008, 2, 1))
        txn2 = TransactionFactory(amount=amount2, 
                                  date=datetime.datetime(2008, 2, 28))
        txn3 = TransactionFactory(amount=amount3, 
                                  date=datetime.datetime(2008, 1, 28))
        
        # From the beginning of a month
        start_date = datetime.date(start_year, start_month, 1)
        end_year, end_month = start_year, start_month + 1

        if end_month > 12:
            end_year += 1
            end_month = 1

        end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)
        total_amount = Transaction.expenses.actual_amount(start_date, end_date)
        self.assertEqual(amount1 + amount2, total_amount,
                         'Total amount does not match')

    def test_actual_total_in_category(self):
        amount1 = Decimal('28.65')
        amount2 = Decimal('36.12')
        amount3 = 1.6
        start_year = 2008
        start_month = 2

        cat1 = CategoryFactory(name='Food')

        txn1 = TransactionFactory(amount=amount1, category=cat1,
                                  date=datetime.datetime(2008, 2, 1))
        txn2 = TransactionFactory(amount=amount2, category=cat1,
                                  date=datetime.datetime(2008, 2, 28))
        txn3 = TransactionFactory(amount=amount3, 
                                  date=datetime.datetime(2008, 1, 28))
        
        # From the beginning of a month
        start_date = datetime.date(start_year, start_month, 1)
        end_year, end_month = start_year, start_month + 1

        if end_month > 12:
            end_year += 1
            end_month = 1

        end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)
        total_amount = Transaction.expenses.actual_amount_in_category(cat1, start_date, end_date)
        self.assertEqual(amount1 + amount2, total_amount,
                         'Total amount does not match')
        
