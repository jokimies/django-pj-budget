from django import forms
from django.template.defaultfilters import slugify

#
from mptt.forms import TreeNodeChoiceField

#
from budget.categories.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        category_tree = TreeNodeChoiceField(queryset=Category.objects.all())
        fields = ('name',)
    
    def save(self):
        if not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data['name'])
        super(CategoryForm, self).save()
