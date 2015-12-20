from decimal import Decimal
import datetime

# 3rd party
from django.test import TestCase

# Own
from budget.categories.models import Category, get_queryset_descendants
from budget.models import Budget

from .utils import *
from .factories import (BudgetFactory, BudgetEstimateFactory,
                        CategoryFactory, TransactionFactory,
                        yearly_estimates_and_actuals,)


class BudgetModelTest(TestCase):
    longMessage = True

    def create_budgets(self):
        BudgetFactory()

    def create_transactions(self):

        amount_groceries1 = Decimal('68.30')
        amount_groceries2 = Decimal('34.39')

        # Setup and crate needed budgets, estimates, etc.
        self.budget = BudgetFactory(start_date=datetime.datetime(2008, 1, 1))
        start_date, end_date = calculate_start_end_date(2008, 2)
        cat_food = CategoryFactory(name='Food')
        cat_groceries = CategoryFactory(name='Groceries',
                                        parent=cat_food,)
        cat_loan = CategoryFactory(name='Loan')
        entire_year = ",".join([str(x) for x in range(1,13)])
        loan_estimate = Decimal('1000.0')
        groceries_estimate = Decimal('800.0')
        self.total_estimate = 2 * loan_estimate + 12 * groceries_estimate
        self.estimate_march = loan_estimate + groceries_estimate
        BudgetEstimateFactory(amount=loan_estimate,
                              budget=self.budget,
                              category=cat_loan,
                              occurring_month='1,3')

        BudgetEstimateFactory(amount=groceries_estimate,
                              budget=self.budget,
                              category=cat_groceries,
                              occurring_month=entire_year)

        TransactionFactory(amount=amount_groceries1,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 2, 1))

        TransactionFactory(amount=amount_groceries2,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 2, 12))

    def test_saving_retrieving_budgets(self):

        self.create_budgets()
        budgets_in_db = Budget.objects.all()

        self.assertEqual(budgets_in_db.count(), 1,
                         'Should be only one budget in db')

    def test_categories_estimates_and_transactions(self):
        """
        This needs refactoring
        """

        amount_groceries1 = Decimal('68.30')
        amount_groceries2 = Decimal('34.39')
        total_transactions = amount_groceries1 + amount_groceries2

        # Setup and crate needed budgets, estimates, etc.
        budget = BudgetFactory(start_date=datetime.datetime(2008, 1, 1))
        start_date, end_date = calculate_start_end_date(2008, 2)
        cat_food = CategoryFactory(name='Food')
        cat_groceries = CategoryFactory(name='Groceries',
                                        parent=cat_food,)
        cat_loan = CategoryFactory(name='Loan')
        BudgetEstimateFactory(amount=Decimal('1000.0'),
                              budget=budget,
                              category=cat_loan,)

        BudgetEstimateFactory(amount=Decimal('800.0'),
                              budget=budget,
                              category=cat_groceries,)

        TransactionFactory(amount=amount_groceries1,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 2, 1))

        TransactionFactory(amount=amount_groceries2,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 2, 1))

        root_nodes = Category.root_nodes.all()
        categories = get_queryset_descendants(root_nodes, include_self=True)

        cat_est_trans, actual_total = (
            budget.categories_estimates_and_transactions(
                start_date, end_date, categories, 'all')
        )
        self.assertEqual(total_transactions, actual_total,
                         'Total amount does not match')

    def test_yearly_actual_total_is_calculated_correctly(self):
        """
        Test if total spent in a year is calculated correctly
        """

        calculated_data, real_data = yearly_estimates_and_actuals()
        self.assertEqual(real_data.total_transactions,
                         calculated_data.calculated_data.actual_yearly_total,
                         'Total amount does not match')

    def test_yearly_actual_per_category_is_calculated_correctly(self):
        """
        Tests if the yearly sum for certain category is calculated correctly
        """
        calculated_data, real_data = yearly_estimates_and_actuals()

        # Total for a category is stored into 3rd item of the category array

        # Not very flexible to use fixed indexes, but enough for now
        self.assertEqual(calculated_data.calculated_data.estimates_and_actuals[1][2],
                         real_data.total_groceries,
                         'Total amount does not match')

    def test_yearly_estimated_per_category_is_calculated_correctly(self):
        """
        Tests if the yearly estimate for certain category is correct.
        There might be multiple estimates for the same category
        """
        calculated_data, real_data = yearly_estimates_and_actuals()
        # Estimation for a category is stored into 4th item of the category
        # array
        # Not very flexible to use fixed indexes, but enough for now
        self.assertAlmostEqual(calculated_data.calculated_data.estimates_and_actuals[1][3],
                               real_data.groceries_estimate,
                               msg='Estimation does not match')

    def test_yearly_estimated_total_is_calculated_correctly(self):

        calculated_data, real_data = yearly_estimates_and_actuals()
        self.assertAlmostEqual(calculated_data.calculated_estimation,
                               real_data.yearly_estimated_total,
                               msg='Estimation does not match')

    def test_current_month_estimate_is_calulated_correcly(self):

        self.create_transactions()
        # Situation in March
        estimated_amount = self.budget.monthly_estimated_total_current_month(3)
        self.assertAlmostEqual(self.estimate_march, estimated_amount,
                               msg='Calculated estimation does not match')


class BudgetEstimateModelTest(TestCase):

    def test_saving_retrieving_estimates(self):
        """
        Create an estimate and check is can be retrieved
        """

        amount = Decimal('200.0')

        BudgetEstimateFactory(amount=amount)

        estimates_in_db = Budget.objects.all()
        self.assertEqual(estimates_in_db.count(), 1,
                         'Should be only one estimate in db')
