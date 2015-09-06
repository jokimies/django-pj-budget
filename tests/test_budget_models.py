from decimal import Decimal
import datetime

# 3rd party
from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse

# Own
from budget.categories.models import Category, get_queryset_descendants

from .utils import *
from .basetest import TestBase
from .factories import *
        
class BudgetModelTest(TestCase):
    longMessage = True

    def create_budgets(self):
        budget1 = BudgetFactory()

    def test_saving_retrieving_budgets(self):

        self.create_budgets()
        budgets_in_db = Budget.objects.all()
        self.assertEqual(budgets_in_db.count(), 1,
                         'Should be only one budget in db')

    def test_categories_estimates_and_transactions(self):

        amount_groceries1 = Decimal('68.30')
        amount_groceries2 = Decimal('34.39')
        total_transactions = amount_groceries1 + amount_groceries2

        #Setup and crate needed budgets, estimates, etc.
        budget = BudgetFactory(start_date=datetime.datetime(2008, 1, 1))
        start_date, end_date = calculate_start_end_date(2008, 2)
        cat_food = CategoryFactory(name='Food')
        cat_groceries = CategoryFactory(name='Groceries',
                                        parent=cat_food,
                                    )
        cat_loan = CategoryFactory(name='Loan')
        est_loan = BudgetEstimateFactory(amount=Decimal('1000.0'),
                                         budget=budget,
                                         category=cat_loan,
                                         )
        est_groceries = BudgetEstimateFactory(amount=Decimal('800.0'),
                                         budget=budget,
                                         category=cat_groceries,
                                          )

        trans_groceries1 = TransactionFactory(amount=amount_groceries1, 
                                             category=cat_groceries, 
                                             date=datetime.datetime(2008, 2, 1))
        trans_groceries2 = TransactionFactory(amount=amount_groceries2, 
                                             category=cat_groceries, 
                                             date=datetime.datetime(2008, 2, 1))

        root_nodes = Category.root_nodes.all()
        categories = get_queryset_descendants(root_nodes, include_self=True)

        cat_est_trans, actual_total = budget.categories_estimates_and_transactions(start_date, end_date, categories)
        self.assertEqual(total_transactions, actual_total, 
                         'Total amount does not match')

class BudgetEstimateModelTest(TestCase):

    def test_saving_retrieving_estimates(self):
        """
        Create an estimate and check is can be retrieved
        """

        amount = Decimal('200.0')

        estimate = BudgetEstimateFactory(amount=amount)

        estimates_in_db = Budget.objects.all()
        self.assertEqual(estimates_in_db.count(), 1,
                         'Should be only one estimate in db')
