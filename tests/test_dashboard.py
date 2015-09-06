import time

from django.test import TestCase
from django.test.client import Client

# Own
from .basetest import TestBase

class DashboardListTest(TestCase, TestBase):
    """
    This needs to be converted to use FactoryBoy for data
    """

    
    #fixtures = ['category_estimate.json']

    def setUp(self):
        self.c = Client()
        self.url = '/budget/'

    #def test_entries_access(self):
    #    response = self.c.get(self.url)

    ##   self.assertEqual(response.status_code, 200)
