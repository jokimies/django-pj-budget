import datetime
from decimal import Decimal
import calendar
from collections import namedtuple

from django.db import models
from django.db.models import Q

from multiselectfield import MultiSelectField

from budget.base_models import ActiveManager, StandardMetadata
from budget.categories.models import Category
from budget.transactions.models import Transaction
from django.utils.translation import ugettext_lazy as _


class BudgetManager(ActiveManager):
    def most_current_for_date(self, date):
        return super(BudgetManager, self).get_queryset().filter(start_date__lte=date).latest('start_date')


class Budget(StandardMetadata):
    """
    An object representing a budget.

    Only estimates are tied to a budget object, which allows different budgets
    to be applied to the same set of transactions for comparision.
    """
    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), unique=True)
    start_date = models.DateTimeField(_('Start Date'),
                                      default=datetime.datetime.now,
                                      db_index=True)

    objects = models.Manager()
    active = BudgetManager()

    def __unicode__(self):
        return self.name

    def yearly_estimated_total(self):
        """
        Sum of estimates for the current budget
        Budget is assumed to cover entire year
        """
        total = Decimal('0.0')
        for estimate in self.estimates.exclude(is_deleted=True):
            for month in estimate.occurring_month:
                total += estimate.amount
        return total

    def monthly_estimated_total_current_month(self, month):
        total = Decimal('0.0')
        for estimate in self.estimates.exclude(is_deleted=True):
            if str(month) in estimate.occurring_month:
                total += estimate.amount
        return total

    def categories_estimates_and_transactions(self, start_date, end_date,
                                              categories,
                                              month):

        """Return data for all the categories in given month, or entire
        year

        Args:
           start_date (datetime.datetime): Start of the date range
           end_date (datetime.datetime): End of the date range
           categories (mptt.TreeQuerySet): List of categories
           month (str): number of month as string, or 'all' for entire year

        Returns:
           A list. First item is list of dictionaries, each dictiory contains
                   - category (Category)
                   - estimate (BudgetEstimate)
                   - transactions (Queryset): Transactions for given period
                   - actual_amount (Decimal): Actual spent amount for the
                     estimate
                   The second item is total sum spent for the category in
                   the given time range
        """

        categories_estimates_and_transactions = []

        actual_total = Decimal('0.0')
        for category in categories:
            actual_amount = Decimal('0.0')
            estimate_found = False

            # Search for each category, and where occurence match
            query_list = Q(category=category)
            transactions =  Transaction.expenses.filter(query_list).order_by('date')
            for estimate in self.category_estimates(query_list):
                # As occurring_month is a string of comma separated list of
                # (month) number, there doesn't seem to be a way to make a
                # query that would return estimates having e.g '2' in
                # occurring_month. Hence doing that in Python
                # If month equals 'all',  accept all estimates for the category
                if month == 'all' or month in estimate.occurring_month:
                    estimate_found = True
                    actual_amount = estimate.actual_amount(start_date,
                                                           end_date,
                                                           transactions)
                    actual_total += actual_amount
                    categories_estimates_and_transactions.append({
                        'category': category,
                        'estimate': estimate,
                        'transactions': estimate.actual_transactions(start_date,
                                                                     end_date),
                        'actual_amount': actual_amount,
                    })
                if not estimate_found:
                    # Set estimate and transactions to empty query set if no
                    # estimate found
                    categories_estimates_and_transactions.append({
                        'category': category,
                        'estimate': self.estimates.none(),
                        'transactions': Transaction.objects.none(),
                        'actual_amount': actual_amount,
                    })

        return (categories_estimates_and_transactions, actual_total)

    def category_estimates(self, cat_query):
        """
        Returns a query list of estimates for certain category

        cat_query: Q() object containing wanted category 'category=<wanted_cat'
        """

        return (self.estimates.filter(cat_query).exclude(is_deleted=True))

    def actuals(self, start_date, end_date, estimate):
        """

        """
        estimates_and_actuals = []
        actual_amount = None
        actual_amount = estimate.actual_amount(start_date, end_date)
        estimates_and_actuals.append({
            'estimate': estimate,
            'actual_amount': actual_amount,
        })

    def estimates_and_actuals(self, start_date, end_date,
                              cat_query, occurrence_query_list=Q()):
        # Search for each category, and where occurence match
        query_list = (cat_query & occurrence_query_list)
        estimates_and_actuals = []
        actual_total = Decimal('0.0')
        estimate_found = False
        actual_amount = None

        for estimate in self.category_estimates(query_list):
            estimate_found = True
            actual_amount = estimate.actual_amount(start_date, end_date)
            actual_total += actual_amount
            estimates_and_actuals.append({
                'estimate': estimate,
                'actual_amount': actual_amount,
            })
        if not estimate_found:
            # Set estimate and transactions to empty query set if no
            # estimate found
            estimates_and_actuals.append({
                'estimate': self.estimates.none(),
                'actual_amount': actual_amount,
            })

        return (estimates_and_actuals, actual_total)

    def actual_total(self, start_date, end_date):
        actual_total = Decimal('0.0')

        for estimate in self.estimates.exclude(is_deleted=True):
            actual_amount = estimate.actual_amount(start_date, end_date)
            actual_total += actual_amount

        return actual_total

    def yearly_data_per_category(self, categories, budget, year):
        """
        :param budget.categories.Category categories: Category list
        :param budget.Budget budget: Budget to work on
        :param str year: Year of the budget
        :return: yearly estimates_and_actuals, actual_yearly_total, start_date
        """

        estimates_and_actuals = []

        # Total amount of money used in a year
        actual_yearly_total = Decimal(0.0)

        YearlyData = namedtuple('YearlyData',
                                ['estimates_and_actuals',
                                 'actual_yearly_total'])

        for category in categories:
            # Total used in year per category
            actual_yearly_total_in_cat = {}
            actual_monthly_total = {}
            actual_monthly_total[category] = Decimal(0.0)
            estimated_yearly_total = {}
            estimated_yearly_total[category] = Decimal(0.0)
            actual_monthly_total[category] = Decimal(0.0)
            actual_yearly_total_in_cat[category] = Decimal(0.0)

            monthly_data_per_category = []
            monthly_data_per_category.append(category)
            monthly_data = []

            category_query = Q(category=category)
            estimates = budget.category_estimates(category_query)
            transactions =  Transaction.expenses.filter(category=category).order_by('date')

            for month_number, month_name in enumerate(calendar.month_name):
                #
                actual_monthly_total[category] = Decimal(0.0)

                # month number 0 is empty string
                if month_number == 0:
                    continue

                start_date = datetime.date(int(year), month_number, 1)
                end_date = datetime.date(int(year),
                                         month_number,
                                         calendar.monthrange(int(year),
                                                             month_number)[1])
                for estimate in estimates:

                    estimated_yearly_amount = estimate.yearly_estimated_amount()

                    # Need refactoring, a better way to get monthly
                    # estimates for a category than just divide by 12
                    estimated_yearly_total[category] += estimated_yearly_amount / Decimal(12)

                    # estimate.actual_amount return all transaction for the
                    # category
                    # Even if there's multiple estimates for the same
                    # category, actual_amount needs to be calculated only once
                    if actual_monthly_total[category] == Decimal(0.0):
                        actual_monthly_total[category] = estimate.actual_amount(
                            start_date,
                            end_date,
                            transactions)

                    # Get estimates and actuals for the date range
                    # eaa, actual_monthly_total_cat =
                    # budget.estimates_and_actuals(start_date, end_date,
                    # category_query, Q())
                actual_yearly_total_in_cat[category] += actual_monthly_total[category]
                monthly_data.append({
                    'actual_monthly_total_in_category': actual_monthly_total[category],
                })

            actual_yearly_total += actual_yearly_total_in_cat[category]

            monthly_data_per_category.append(monthly_data)

            # Total per category within year
            monthly_data_per_category.append(actual_yearly_total_in_cat[category])
            monthly_data_per_category.append(estimated_yearly_total[category])
            # Store monthly data for current category
            estimates_and_actuals.append(monthly_data_per_category)

        return YearlyData(estimates_and_actuals=estimates_and_actuals,
                          actual_yearly_total=actual_yearly_total)

    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')


class BudgetEstimate(StandardMetadata):
    """
    The individual line items that make up a budget.

    Some examples include possible items like "Mortgage", "Rent", "Food",
    "Misc" and "Car Payment".
    """

    REPEAT_CHOICES = (
        ('BIWEEKLY', _('Every 2 Weeks')),
        ('MONTHLY', _('Every Month')),
    )

    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    MONTH_CHOICES = (
        (JANUARY, _('January')),
        (FEBRUARY, _('February')),
        (MARCH, _('March')),
        (APRIL, _('April')),
        (MAY, _('May')),
        (JUNE, _('June')),
        (JULY, _('July')),
        (AUGUST, _('August')),
        (SEPTEMBER, _('September')),
        (OCTOBER, _('October')),
        (NOVEMBER, _('November')),
        (DECEMBER, _('December')),
    )

    budget = models.ForeignKey(Budget, related_name='estimates',
                               verbose_name=_('Budget'))
    category = models.ForeignKey(Category, related_name='estimates',
                                 verbose_name=_('Category'))
    amount = models.DecimalField(_('Amount'), max_digits=11, decimal_places=2)
    occurring_month = MultiSelectField(_('Occuring month'),
                                       null=False, blank=False,
                                       choices=MONTH_CHOICES,
                                       default=u'1')

    objects = models.Manager()
    active = ActiveManager()

    def __unicode__(self):
        return u"%s - %s" % (self.category.name, self.amount)

    def yearly_estimated_amount(self):

        yearly_estimate = Decimal(0.0)
        for month in self.occurring_month:
            yearly_estimate += self.amount

        return yearly_estimate

    def actual_transactions(self, start_date=None, end_date=None):
        # Estimates should only report on expenses to prevent incomes from
        # (incorrectly) artificially inflating totals.
        if (start_date and end_date):
            return Transaction.expenses.filter(category=self.category, date__range=(start_date, end_date)).order_by('date').select_related('category')
        return Transaction.expenses.filter(category=self.category).order_by('date').select_related('category')

    def actual_amount(self, start_date, end_date, transactions=None):
        """Return actual spendings during the period

        :param start_date: start of range
        :param end_date: end of range
        :param transaction: queryset of all expenses in certain category

        Doing the date filtering in Python to avoid hitting database
        hundreds of times (this function is 12 (number of months in year) *
        number of categories).
        """

        total = Decimal('0.0')
        if transactions:
            for transaction in transactions:
                if start_date <= transaction.date <= end_date:
                    total += transaction.amount
        return total


    class Meta:
        verbose_name = _('Budget estimate')
        verbose_name_plural = _('Budget estimates')
