import time

#
#
#
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

# Own
from .basetest import TestBase

#
#
#
#from budget.tests.factories import *

class BudgetDasboardsTest(TestCase, TestBase):

    # fixtures = ['category_estimate.json']

    def setUp(self):
        self.c = Client()
        self.url = reverse('budget_dashboard')

    def test_dasboard_empty(self):
        """
        If there's no budget, it should redirect to setup page
        """

        response = self.c.get(self.url, follow=True)
        self.assertRedirects(response, reverse('budget_setup'))

    
