from django import forms

#
from mptt.forms import TreeNodeChoiceField

#
from budget.transactions.models import Transaction
from budget.categories.models import Category

class TransactionForm(forms.ModelForm):

    # Replace category in the model with hieararchial category list
    category = TreeNodeChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Transaction
        fields = ('transaction_type', 'notes', 'category', 'amount', 'date')
