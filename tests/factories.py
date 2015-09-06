import datetime

# 3rd party
import factory

from django.template.defaultfilters import slugify

# own
from budget.categories.models import Category
from budget.models import BudgetEstimate, Budget
from budget.transactions.models import Transaction

class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating categories
    """

    class Meta:
        model = Category

    # Category names, when created will be 'Category 1' for the first,
    # 'Category 2' for the second, etc.
    name = factory.Sequence(lambda n: 'Category {0}'.format(n))

    # slugify each name and make that as slug field
    slug = factory.LazyAttribute(lambda a: '{0}'.format(slugify(a.name)))



class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    name = factory.Sequence(lambda n: 'Budget {0}'.format(n))
    start_date = datetime.datetime(2008, 1, 1)

class BudgetEstimateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetEstimate

    budget = factory.SubFactory(BudgetFactory)
    category = factory.SubFactory(CategoryFactory)

class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    notes = factory.Sequence(lambda n: 'Transaction {0}'.format(n))
    category = factory.SubFactory(CategoryFactory)
