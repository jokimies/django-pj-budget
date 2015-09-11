from django.test import TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse

# Own 
from .basetest import BaseTest

class CategoryListTest(TestCase, BaseTest):

    #fixtures = ['category_estimate.json']

    def setUp(self):
        self.c = Client()
        self.url = reverse('budget_category_list')

    def test_entries_access(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_invalid_page(self):
        """
        Test non-existing paginator page
        """

        response = self.c.get(self.url + '?page=100')
        self.assertEqual(response.status_code, 404)


class CategoryAddTest(TestCase, BaseTest):
    def setUp(self):
        self.c = Client()
        self.url = reverse('budget_category_add')

    def test_category_add_access(self):
        response = self.c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_category_add(self):
        response = self.c.post(self.url, { 'name': 'TestCat'}, follow=True)

        # Adding should redirect to category list view
        self.assertRedirects(response,reverse('budget_category_list'))
        self.assertContains(response, 'TestCat')

