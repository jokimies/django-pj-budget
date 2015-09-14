import datetime
from decimal import Decimal

# 3rd party
import factory

from django.template.defaultfilters import slugify

# own
from budget.categories.models import Category, get_queryset_descendants
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

def yearly_estimates_and_actuals():
    amount_groceries1 = Decimal('68.30')
    amount_groceries2 = Decimal('34.39')
    amount_loan = Decimal('800.0')
    total_groceries = amount_groceries1 + amount_groceries2
    total_transactions = total_groceries + amount_loan
    
    #Setup and crate needed budgets, estimates, etc.
    budget = BudgetFactory(start_date=datetime.datetime(2008, 1, 1))
    cat_food = CategoryFactory(name='Food')
    cat_groceries = CategoryFactory(name='Groceries',
                                    parent=cat_food,
                                )
    cat_loan = CategoryFactory(name='Loan')
    cat_mortgage = CategoryFactory(name='Mortgage',
                                   parent=cat_loan,
                               )
    est_loan = BudgetEstimateFactory(amount=Decimal('9600.0'),
                                     budget=budget,
                                     category=cat_mortgage,
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
                                          date=datetime.datetime(2008, 9, 15))
    
    trans_loan1 = TransactionFactory(amount=amount_loan, 
                                     category=cat_mortgage, 
                                     date=datetime.datetime(2008, 9, 20))
    root_nodes = Category.root_nodes.all()
    categories = get_queryset_descendants(root_nodes, include_self=True)
    
    year = "2008"
    yearly_things = budget.categories_yearly_estimates_and_actuals(categories,
                                                           budget, year)

    # Return yearly things and toral_transcations
    return yearly_things + (total_transactions, total_groceries)
