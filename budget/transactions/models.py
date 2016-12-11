import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _

from budget.categories.models import Category
from budget.base_models import ActiveManager, StandardMetadata


TRANSACTION_TYPES = (
    ('expense', _('Expense')),
    ('income', _('Income')),
)


class TransactionManager(ActiveManager):
    def get_latest(self, limit=10):
        return self.get_queryset().order_by('-date', '-created')[0:limit]

    def get_all(self, start_date, end_date):
        """
        Return queryset of all transactions between start_data and end_date
        """

        # Estimates should only report on expenses to prevent incomes from
        # (incorrectly) artificially inflating totals.
        return self.get_queryset().filter(date__range=(start_date, end_date)).order_by('date').select_related('budget')


class TransactionExpenseManager(TransactionManager):
    def get_queryset(self):
        return super(TransactionExpenseManager, self).get_queryset().filter(transaction_type='expense').select_related('category')

    def actual_transactions(self, start_date, end_date):
        """
        Return queryset of all expenses between start_date and end_date
        """

        return Transaction.expenses.filter(date__range=(start_date, end_date)).order_by('date')

    def actual_amount(self, start_date, end_date):
        """
        Sum of all expenses between given dates
        """

        total = Decimal('0.0')
        for transaction in self.actual_transactions(start_date, end_date):
            total += transaction.amount
        return total

    def actual_transactions_in_category(self, category, start_date, end_date):
        """
        Return queryset of all transactions for given gategory between
        given dates
        """

        return Transaction.expenses.filter(category=category, date__range=(start_date, end_date)).order_by('date')

    def actual_amount_in_category(self, category, start_date, end_date):
        """
        Sum of all transactions in given category between given dates
        """
        total = Decimal('0.0')
        for transaction in self.actual_transactions_in_category(category, start_date, end_date):
            total += transaction.amount
        return total


class TransactionIncomeManager(TransactionManager):
    def get_queryset(self):
        return super(TransactionIncomeManager, self).get_queryset().filter(transaction_type='income')


class Transaction(StandardMetadata):
    """
    Represents incomes/expenses for the party doing the budgeting.

    Transactions are not tied to individual budgets because this allows
    different budgets to applied (like a filter) to a set of transactions.
    It also allows for budgets to change through time without altering the
    actual incoming/outgoing funds.
    """
    transaction_type = models.CharField(_('Transaction type'),
                                        max_length=32,
                                        choices=TRANSACTION_TYPES,
                                        default='expense', db_index=True)
    notes = models.CharField(_('Notes'), max_length=255, blank=True)
    category = models.ForeignKey(Category, related_name='transactions',
                                 verbose_name=_('Category'))
    amount = models.DecimalField(_('Amount'), max_digits=11, decimal_places=2)
    date = models.DateField(_('Date'), default=datetime.date.today,
                            db_index=True)

    objects = models.Manager()
    active = ActiveManager()
    expenses = TransactionExpenseManager()
    incomes = TransactionIncomeManager()

    def __unicode__(self):
        return u"%s (%s) - %s" % (self.notes,
                                  self.get_transaction_type_display(),
                                  self.amount)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
