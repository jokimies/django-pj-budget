from django.conf.urls import url, include
from budget import views as budget_views
"""
Needed Urls:
Dashboard
Year Summary
Month Summary
CRUD Budget
CRUD BudgetEstimates

Eventually:
Custom date range
Week Summary
Day Summary
...?
"""

urlpatterns = [
    url(r'^$', budget_views.dashboard, name='budget_dashboard'),
    url(r'^setup/$', budget_views.setup, name='budget_setup'),
    
    # Summaries
    url(r'^summary/$', budget_views.summary_list, name='budget_summary_list'),
    url(r'^summary/(?P<year>\d{4})/simple/$',
        budget_views.summary_year_no_months,
        name='budget_summary_year_no_months'),
    url(r'^summary/(?P<year>\d{4})/$',
        budget_views.summary_year_detail, name='budget_summary_year'),
    url(r'^summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        budget_views.summary_month, name='budget_summary_month'),
    
    # Categories
    url(r'^category/', include('budget.categories.urls')),
    
    # Budget
    url(r'^budget/$', budget_views.budget_list, name='budget_budget_list'),
    url(r'^budget/add/$', budget_views.budget_add, name='budget_budget_add'),
    url(r'^budget/edit/(?P<slug>[\w-]+)/$',
        budget_views.budget_edit, name='budget_budget_edit'),
    url(r'^budget/delete/(?P<slug>[\w-]+)/$',
        budget_views.budget_delete, name='budget_budget_delete'),
    
    # BudgetEstimates
    url(r'^budget/(?P<budget_slug>[\w-]+)/estimate/$',
        budget_views.estimate_list, name='budget_estimate_list'),
    url(r'^budget/(?P<budget_slug>[\w-]+)/estimate/add/$',
        budget_views.estimate_add, name='budget_estimate_add'),
    url(r'^budget/(?P<budget_slug>[\w-]+)/estimate/edit/(?P<estimate_id>\d+)/$',
        budget_views.estimate_edit, name='budget_estimate_edit'),
    url(r'^budget/(?P<budget_slug>[\w-]+)/estimate/delete/(?P<estimate_id>\d+)/$', budget_views.estimate_delete, name='budget_estimate_delete'),
    
    # Transaction
    url(r'^transaction/', include('budget.transactions.urls')),
]
