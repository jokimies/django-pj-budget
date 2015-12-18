import datetime

#
from django import forms
from django.template.defaultfilters import slugify

#
from mptt.forms import TreeNodeChoiceField

#
from budget.models import Budget, BudgetEstimate
from budget.categories.models import Category

class BudgetForm(forms.ModelForm):
    start_date = forms.SplitDateTimeField(initial=datetime.datetime.now, required=False, widget=forms.SplitDateTimeWidget)
    
    class Meta:
        model = Budget
        fields = ('name', 'start_date')
    
    def save(self):
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data['name'])
        super(BudgetForm, self).save()


class BudgetEstimateForm(forms.ModelForm):

    error_css_class = 'alert alert-danger'
    required_css_class = 'alert alert-info'
    # Replace category in the model with hieararchial category list
    category = TreeNodeChoiceField(queryset=Category.objects.all())

    class Meta:
        model = BudgetEstimate
        fields = ('category', 'amount', 'occurring_month')
    
    def save(self, budget):
        self.instance.budget = budget
        super(BudgetEstimateForm, self).save()

    def clean(self):
        """
        Check if either 'repeat' or 'occurring_month' is given, but not
        both 
        """

        cleaned_data = super(BudgetEstimateForm, self).clean()
        repeat = cleaned_data.get('repeat')
        occurs = cleaned_data.get('occurring_month')

        if repeat and occurs:
            msg = u'Must select only one: Repeat or Occurring month'
            self._errors['repeat'] = self.error_class([msg])
            self._errors['occurring_month'] = self.error_class([msg])
            del cleaned_data['repeat']
            del cleaned_data['occurring_month']

        elif not repeat and not occurs:
            msg = u'Must select one: Repeat or Occurring month'
            self._errors['repeat'] = self.error_class([msg])
            self._errors['occurring_month'] = self.error_class([msg])
            del cleaned_data['repeat']
            del cleaned_data['occurring_month']
            
        return cleaned_data
