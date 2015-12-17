import datetime
import calendar
from decimal import Decimal
#
#
# 3rd party
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Q

# Own
from .basetest import BaseTest
from .factories import *

from budget.views import summary_year_no_months
from budget.categories.models import Category, get_queryset_descendants
#
#


class BudgetDasboardTest(TestCase, BaseTest):

    def setUp(self):
        self.c = Client()
        self.url = reverse('budget_dashboard')

    def test_dasboard_empty(self):
        """
        If there's no budget, it should redirect to setup page
        """

        response = self.c.get(self.url, follow=True)
        self.assertRedirects(response, reverse('budget_setup'))


class BudgetYearlySummaryTest(TestCase):

    maxDiff = None

    def setUp(self):

        self.year = "2008"

        self.client = Client()
        self.url = reverse('budget_summary_year', args=(self.year,))

        amount_groceries1 = Decimal('68.30')
        amount_groceries2 = Decimal('34.39')
        amount_loan = Decimal('800.0')
        # total_groceries = amount_groceries1 + amount_groceries2
        # total_transactions = total_groceries + amount_loan

        self.start_date = datetime.date(int(self.year), 1, 1)
        self.end_date = datetime.date(int(self.year), 12, 31)

        # Setup and crate needed budgets, estimates, etc.
        self.budget = BudgetFactory(start_date=datetime.datetime(2008, 1, 1))
        cat_food = CategoryFactory(name='Food')
        cat_groceries = CategoryFactory(name='Groceries',
                                        parent=cat_food,)

        cat_loan = CategoryFactory(name='Loan')
        cat_mortgage = CategoryFactory(name='Mortgage',
                                       parent=cat_loan,)

        BudgetEstimateFactory(amount=Decimal('9600.0'),
                              budget=self.budget,
                              category=cat_mortgage,)

        BudgetEstimateFactory(amount=Decimal('800.0'),
                              budget=self.budget,
                              category=cat_groceries,)

        TransactionFactory(amount=amount_groceries1,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 2, 1))

        TransactionFactory(amount=amount_groceries2,
                           category=cat_groceries,
                           date=datetime.datetime(2008, 9, 15))

        TransactionFactory(amount=amount_loan,
                           category=cat_mortgage,
                           date=datetime.datetime(2008, 9, 20))
        root_nodes = Category.root_nodes.all()
        self.categories = get_queryset_descendants(root_nodes,
                                                   include_self=True)
        yearly_things = self.budget.yearly_data_per_category(self.categories,
                                                             self.budget,
                                                             self.year)
        self.estimates_and_actuals, self.actual_yearly_total = yearly_things

    def test_yearly_summary_without_months_returns_correct_page(self):
        request = HttpRequest()
        template = 'budget/summaries/summary_year.html'

        response = summary_year_no_months(request,
                                          self.year,
                                          template_name=template)
        categories_estimates_and_transactions, actual_total = self.budget.categories_estimates_and_transactions(self.start_date, self.end_date, self.categories, Q())

        expected_html = render_to_string(template, {
            'months': calendar.month_abbr[1:],
            'categories': self.categories,
            'categories_estimates_and_transactions': categories_estimates_and_transactions,
            'actual_total': actual_total,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': self.budget,
            'year': self.year,
        }, RequestContext(request))

        self.assertMultiLineEqual(response.content.decode(), expected_html)

    def test_summary_uses_summary_list_template(self):
        """
        Verifies 'main' summary page uses summary_list template
        """

        template = 'budget/summaries/summary_list.html'

        response = self.client.get(reverse('budget_summary_list'))
        self.assertTemplateUsed(response, template)

    def test_yearly_summary_uses_detailed_template(self):
        """
        Test yearlyl summary uses template with montly details
        """

        template = 'budget/summaries/summary_year_months.html'

        response = self.client.get(
            reverse(
                'budget_summary_year',
                kwargs={'year': self.year}
            )
        )
        self.assertTemplateUsed(response, template)
