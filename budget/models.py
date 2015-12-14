import datetime
from decimal import Decimal
import calendar

from django.db import models
from django.db.models import Q


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

    def monthly_estimated_total(self):
        total = Decimal('0.0')
        for estimate in self.estimates.exclude(is_deleted=True):
            if estimate.repeat == 'MONTHLY':
                total += estimate.amount
            # If estimate is not monthly, it happens in certain month. Use
            # average for that estimate
            else:
                total += estimate.amount / 12
        return total

    def monthly_estimated_total_current_month(self, month):
        total = Decimal('0.0')
        for estimate in self.estimates.exclude(is_deleted=True):
            if estimate.repeat == 'MONTHLY':
                total += estimate.amount
            # If estimate is not monthly, it happens in certain month. Use
            # average for that estimate
            elif estimate.occurring_month == month:
                total += estimate.amount
        return total

    def yearly_estimated_total(self):
        return self.monthly_estimated_total() * 12

    def categories_estimates_and_transactions(self, start_date, end_date,
                                              categories,
                                              occurrence_query_list=Q()):

        categories_estimates_and_transactions = []

        actual_total = Decimal('0.0')
        for category in categories:
            actual_amount = Decimal('0.0')
            estimate_found = False

            # Search for each category, and where occurence match
            query_list = (Q(category=category) & occurrence_query_list)

            for estimate in self.estimates.filter(query_list).exclude(is_deleted=True):
                estimate_found = True
                actual_amount = estimate.actual_amount(start_date, end_date)
                actual_total += actual_amount
                categories_estimates_and_transactions.append({
                    'category': category,
                    'estimate': estimate,
                    'transactions': estimate.actual_transactions(start_date,
                                                                 end_date),
                    'actual_amount': actual_amount,
                })
            if not estimate_found:
                # Set estiamte and transactions to empty query set if no
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

        for estimate in self.estimates.filter(query_list).exclude(is_deleted=True):
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

    def categories_yearly_estimates_and_actuals(self, categories, budget, year):
        """
        :param budget.categories.Category categories: Category list
        :param budget.Budget budget: Budget to work on
        :param str year: Year of the budget
        :return: yearly estimates_and_actuals, actual_yearly_total, start_date
        """

        estimates_and_actuals = []

        # Total amount of money used in a year
        actual_yearly_total = Decimal(0.0)

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

                    estimated_yearly_total[category] += estimated_yearly_amount / Decimal(12)

                    # estimate.actual_amount return all transaction for the
                    # category
                    # Even if there's multiple estimates for the same
                    # category, actual_amount needs to be calculated only once
                    if actual_monthly_total[category] == Decimal(0.0):
                        actual_monthly_total[category] = estimate.actual_amount(start_date, end_date)

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

        return (estimates_and_actuals, actual_yearly_total)

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

    budget = models.ForeignKey(Budget, related_name='estimates', verbose_name=_('Budget'))
    category = models.ForeignKey(Category, related_name='estimates', verbose_name=_('Category'))
    amount = models.DecimalField(_('Amount'), max_digits=11, decimal_places=2)
    repeat = models.CharField(_('Repeat'), max_length=15, choices=REPEAT_CHOICES, blank=True)
    occurring_month = models.IntegerField(_('Occuring month'), null=True, blank=True, choices=MONTH_CHOICES)

    objects = models.Manager()
    active = ActiveManager()

    def __unicode__(self):
        return u"%s - %s" % (self.category.name, self.amount)

    def yearly_estimated_amount(self):
        if self.repeat == 'MONTHLY':
            return self.amount * 12
        else:
            # payment is estimated to happen only  in certain
            # month, use that value
            return self.amount

    def actual_transactions(self, start_date, end_date):
        # Estimates should only report on expenses to prevent incomes from
        # (incorrectly) artificially inflating totals.
        return Transaction.expenses.filter(category=self.category, date__range=(start_date, end_date)).order_by('date')

    def actual_amount(self, start_date, end_date):
        total = Decimal('0.0')
        for transaction in self.actual_transactions(start_date, end_date):
            total += transaction.amount
        return total

    class Meta:
        verbose_name = _('Budget estimate')
        verbose_name_plural = _('Budget estimates')
