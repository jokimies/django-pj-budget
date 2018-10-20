from django.conf.urls import url, include
from budget.transactions import views as budget_transactions_views

urlpatterns = [
    url(r'^$', budget_transactions_views.transaction_list,
        name='budget_transaction_list'),
    url(r'^add/$', budget_transactions_views.transaction_add,
        name='budget_transaction_add'),
    url(r'^edit/(?P<transaction_id>\d+)/$',
        budget_transactions_views.transaction_edit,
        name='budget_transaction_edit'),
    url(r'^delete/(?P<transaction_id>\d+)/$',
        budget_transactions_views.transaction_delete,
        name='budget_transaction_delete'),
]
