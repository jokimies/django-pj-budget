from django.conf.urls import url, include
from budget.categories import views as budget_categories_views
urlpatterns = [
    url(r'^$', budget_categories_views.category_list,
        name='budget_category_list'),
    url(r'^add/$', budget_categories_views.category_add,
        name='budget_category_add'),
    url(r'^edit/(?P<slug>[\w_-]+)/$', budget_categories_views.category_edit,
        name='budget_category_edit'),
    url(r'^delete/(?P<slug>[\w_-]+)/$', budget_categories_views.category_delete,
        name='budget_category_delete'),
]
