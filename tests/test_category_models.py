import datetime
from decimal import Decimal

# 3rd party
from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse

# Own
from budget.transactions.models import Transaction

from .factories import *

class CategoryModelTest(TestCase):

    longMessage = True

    def create_categories(self):
        cat1 = CategoryFactory()
        cat2 = CategoryFactory()
        return cat1

    def create_transactions(self):

        amount1 = Decimal('28.65')
        amount2 = Decimal('36.12')
        amount3 = 1.6

        cat1 = CategoryFactory(name='Food')
        txn1 = TransactionFactory(amount=amount1, category=cat1, 
                                  date=datetime.datetime(2008, 2, 1))
        txn2 = TransactionFactory(amount=amount2, category=cat1,
                                  date=datetime.datetime(2008, 2, 28))
        txn3 = TransactionFactory(amount=amount3, 
                                  date=datetime.datetime(2008, 1, 28))

        return cat1, txn1, txn2, txn3


    def test_saving_retrieving_categories(self):
        self.create_categories()
        saved_items = Category.objects.all()
        self.assertEqual(saved_items.count(), 2, 
                         'Should be two categories in db')


    def test_deleting_categories(self):

        cat1 = self.create_categories()
        cat1.delete()
        remaining_categories = Category.objects.filter(is_deleted=False)
        self.assertEqual(remaining_categories.count(), 1, 
                         'Should be only  category in db')
        

    def test_estimates_and_transactions(self):

        estimate_amount = Decimal('200.0')

        start_year = 2008
        start_month = 2

        # From the beginning of a month
        start_date = datetime.date(start_year, start_month, 1)
        end_year, end_month = start_year, start_month + 1
        
        if end_month > 12:
            end_year += 1
            end_month = 1
            
        end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)

        cat1, txn1, txn2, txn3 = self.create_transactions()
        estimate = BudgetEstimateFactory(amount=estimate_amount, category=cat1)
        transactions = Category.estimates_and_transactions(cat1, start_date, end_date)
            
