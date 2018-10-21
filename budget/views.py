import datetime
import calendar

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from budget.models import Budget, BudgetEstimate
from budget.categories.models import Category, get_queryset_descendants
from budget.transactions.models import Transaction
from budget.forms import BudgetEstimateForm, BudgetForm


def dashboard(request, budget_model_class=Budget,
              transaction_model_class=Transaction,
              template_name='budget/dashboard.html'):
    """
    Provides a high-level rundown of recent activity and budget status.

    Template: ``budget/dashboard.html``
    Context:
        budget
            the most current budget object
        latest_expenses
            the most recent expenses (by default, the last 10)
        latest_incomes
            the most recent incomes (by default, the last 10)
        estimated_amount
            the budget's estimated total for the month
        amount_used
            the actual amount spent for the month
        progress_bar_percent
            the percentage of the budget actually spent so far
    """
    today = datetime.date.today()
    start_date = datetime.date(today.year, today.month, 1)
    end_year, end_month = today.year, today.month + 1

    if end_month > 12:
        end_year += 1
        end_month = 1

    end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)

    try:
        budget = budget_model_class.active.most_current_for_date(datetime.datetime.today())
    except ObjectDoesNotExist:
        # Since there are no budgets at this point, pass them on to setup
        # as this view is meaningless without at least basic data in place.
        return HttpResponseRedirect(reverse('budget_setup'))

    latest_expenses = transaction_model_class.expenses.get_latest()
    latest_incomes = transaction_model_class.incomes.get_latest()

    estimated_amount = budget.monthly_estimated_total_current_month(today.month)
    amount_used = budget.actual_total(start_date, end_date)

    if estimated_amount == 0:
        progress_bar_percent = 100
    else:
        progress_bar_percent = int(amount_used / estimated_amount * 100)

    if progress_bar_percent >= 100:
        progress_bar_percent = 100

    return render(request, template_name, {
        'budget': budget,
        'latest_expenses': latest_expenses,
        'latest_incomes': latest_incomes,
        'estimated_amount': estimated_amount,
        'amount_used': amount_used,
        'progress_bar_percent': progress_bar_percent,
    })


def setup(request, template_name='budget/setup.html'):
    """
    Displays a setup page which ties together the
    category/budget/budget estimate areas with explanatory text on how to use
    to set everything up properly.

    Templates: ``budget/setup.html``
    """
    return render(request, template_name, {})


def summary_list(request, transaction_model_class=Transaction,
                 template_name='budget/summaries/summary_list.html'):
    """
    Displays a list of all months that may have transactions for that month.

    Templates: ``budget/summaries/summary_list.html``
    Context:
        dates
            a list of datetime objects representing all years/months that
            have transactions
    """
    dates = transaction_model_class.active.all().dates('date', 'month')
    return render(request, template_name, {
        'dates': dates,
    })


def summary_year_no_months(request, year, budget_model_class=Budget,
                           template_name='budget/summaries/summary_year.html'):
    """
    Displays a budget report for the year to date.

    Templates: ``budget/summaries/summary_year.html``
    Context:
        budget
            the most current budget object for the year
        estimates_and_transactions
            a list of dictionaries containing each budget estimate, the
            corresponding transactions and total amount of the transactions
        actual_total
            the total amount of all transactions represented in the budget
            for the year
        start_date
            the first date for the year
        end_date
            the last date for the year
    """
    start_date = datetime.date(int(year), 1, 1)
    end_date = datetime.date(int(year), 12, 31)
    budget = budget_model_class.active.most_current_for_date(end_date)

    root_nodes = Category.root_nodes.all()
    categories = get_queryset_descendants(root_nodes, include_self=True)

    categories_estimates_and_transactions, actual_total = budget.categories_estimates_and_transactions(start_date, end_date, categories, 'all')
    return render(request, template_name, {
        'budget': budget,
        'categories_estimates_and_transactions': categories_estimates_and_transactions,
        'actual_total': actual_total,
        'year': year,
    })


def summary_year_detail(request, year, budget_model_class=Budget,
                        template_name='budget/summaries/summary_year_months.html'):
    """
    Displays a budget report for the year to date, month by month

    Templates: ``budget/summaries/summary_year_months.html``
    Context:
        budget
            the most current budget object for the year
        estimates_and_transactions
            a list of dictionaries containing each budget estimate, the
            corresponding transactions and total amount of the transactions
        actual_total
            the total amount of all transactions represented in the budget
            for the year
        start_date
            the first date for the year
        end_date
            the last date for the year
    """
    year_end_date = datetime.date(int(year), 12, 31)

    root_nodes = Category.root_nodes.all()
    categories = get_queryset_descendants(root_nodes, include_self=True)
    budget = budget_model_class.active.most_current_for_date(year_end_date)
    yearly_data = budget.yearly_data_per_category(categories, budget,
                                                  year)
    return render(request, template_name, {
        'months': calendar.month_abbr[1:],
        'categories': categories,
        'budget': budget,
        'estimates_and_actuals': yearly_data.estimates_and_actuals,
        'actual_yearly_total': yearly_data.actual_yearly_total,
        'year': year,
    })


def summary_month(request, year, month, budget_model_class=Budget,
                  template_name='budget/summaries/summary_month.html'):
    """
    Displays a budget report for the month to date.

    Templates: ``budget/summaries/summary_month.html``
    Context:
        budget
            the most current budget object for the month
        estimates_and_transactions
            a list of dictionaries containing each budget estimate, the
            corresponding transactions and total amount of the transactions
        actual_total
            the total amount of all transactions represented in the budget
            for the month
        start_date
            the first date for the month
        end_date
            the last date for the month
    """
    start_date = datetime.date(int(year), int(month), 1)
    end_year, end_month = int(year), int(month) + 1

    if end_month > 12:
        end_year += 1
        end_month = 1

    end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)
    # Search for monthly expenses and those estimated to happen in this month

    budget = budget_model_class.active.most_current_for_date(end_date)
    estimated_total = budget.monthly_estimated_total_current_month(int(month))

    root_nodes = Category.root_nodes.all()
    categories = get_queryset_descendants(root_nodes, include_self=True)

    categories_estimates_and_transactions, actual_total = budget.categories_estimates_and_transactions(start_date, end_date, categories, month)

    return render(request, template_name, {
        'budget': budget,
        'categories_estimates_and_transactions': categories_estimates_and_transactions,
        'actual_total': actual_total,
        'start_date': start_date,
        'end_date': end_date,
        'estimated_total': estimated_total,
        'categories': categories,
    })


def budget_list(request, model_class=Budget,
                template_name='budget/budgets/list.html'):
    """
    A list of budget objects.

    Templates: ``budget/budgets/list.html``
    Context:
        budgets
            paginated list of budget objects
        paginator
            A Django Paginator instance
        page
            current page of budget objects
    """
    budgets_list = model_class.active.all()
    try:
        paginator = Paginator(budgets_list,
                              getattr(settings, 'BUDGET_LIST_PER_PAGE', 50))
        page = paginator.page(request.GET.get('page', 1))
        budgets = page.object_list
    except InvalidPage:
        raise Http404('Invalid page requested.')
    return render(request, template_name, {
        'budgets': budgets,
        'paginator': paginator,
        'page': page,
    })


def budget_add(request, form_class=BudgetForm,
               template_name='budget/budgets/add.html'):
    """
    Create a new budget object.

    Templates: ``budget/budgets/add.html``
    Context:
        form
            a budget form
    """
    if request.POST:
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('budget_budget_list'))
    else:
        form = form_class()
    return render_to_response(request, template_name, {
        'form': form,
    })


def budget_edit(request, slug, model_class=Budget, form_class=BudgetForm,
                template_name='budget/budgets/edit.html'):
    """
    Edit a budget object.

    Templates: ``budget/budgets/edit.html``
    Context:
        budget
            the existing budget object
        form
            a budget form
    """
    budget = get_object_or_404(model_class.active.all(), slug=slug)
    if request.POST:
        form = form_class(request.POST, instance=budget)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('budget_budget_list'))
    else:
        form = form_class(instance=budget)
    return render(request, template_name, {
        'budget': budget,
        'form': form,
    })


def budget_delete(request, slug, model_class=Budget,
                  template_name='budget/budgets/delete.html'):
    """
    Delete a budget object.

    Templates: ``budget/budgets/delete.html``
    Context:
        budget
            the existing budget object
    """
    budget = get_object_or_404(model_class.active.all(), slug=slug)
    if request.POST:
        if request.POST.get('confirmed'):
            budget.delete()
        return HttpResponseRedirect(reverse('budget_budget_list'))
    return render(request, template_name, {
        'budget': budget,
    })


def estimate_list(request, budget_slug, budget_model_class=Budget,
                  model_class=BudgetEstimate,
                  template_name='budget/estimates/list.html'):
    """
    A list of estimate objects.

    Templates: ``budget/estimates/list.html``
    Context:
        budget
            the parent budget object for the estimates
        estimates
            paginated list of estimate objects
        paginator
            A Django Paginator instance
        page
            current page of estimate objects
    """
    budget = get_object_or_404(budget_model_class.active.all(),
                               slug=budget_slug)
    estimates_list = model_class.active.filter(budget__id=budget.id).all()
    try:
        paginator = Paginator(estimates_list,
                              getattr(settings, 'BUDGET_LIST_PER_PAGE', 50))
        page = paginator.page(request.GET.get('page', 1))
        estimates = page.object_list
    except InvalidPage:
        raise Http404('Invalid page requested.')
    return render(request, template_name, {
        'budget': budget,
        'estimates': estimates,
        'paginator': paginator,
        'page': page,
    })


def estimate_add(request, budget_slug, budget_model_class=Budget,
                 form_class=BudgetEstimateForm,
                 template_name='budget/estimates/add.html'):
    """
    Create a new estimate object.

    Templates: ``budget/estimates/add.html``
    Context:
        budget
            the parent budget object for the estimate
        form
            a estimate form
    """
    budget = get_object_or_404(budget_model_class.active.all(),
                               slug=budget_slug)
    if request.POST:
        form = form_class(request.POST)

        if form.is_valid():
            form.save(budget=budget)
            return HttpResponseRedirect(
                reverse('budget_estimate_list',
                        kwargs={'budget_slug': budget.slug})
            )
    else:
        form = form_class()
    return render(request, template_name, {
        'budget': budget,
        'form': form,
    })


def estimate_edit(request, budget_slug, estimate_id,
                  budget_model_class=Budget,
                  form_class=BudgetEstimateForm,
                  template_name='budget/estimates/edit.html'):
    """
    Edit a estimate object.

    Templates: ``budget/estimates/edit.html``
    Context:
        budget
            the parent budget object for the estimate
        estimate
            the existing estimate object
        form
            a estimate form
    """
    budget = get_object_or_404(budget_model_class.active.all(),
                               slug=budget_slug)
    try:
        estimate = budget.estimates.get(pk=estimate_id, is_deleted=False)
    except ObjectDoesNotExist:
        raise Http404("The requested estimate could not be found.")
    if request.POST:
        form = form_class(request.POST, instance=estimate)

        if form.is_valid():
            form.save(budget=budget)
            return HttpResponseRedirect(
                reverse('budget_estimate_list',
                        kwargs={'budget_slug': budget.slug})
            )
    else:
        form = form_class(instance=estimate)
    return render(request, template_name, {
        'budget': budget,
        'estimate': estimate,
        'form': form,
    })


def estimate_delete(request, budget_slug, estimate_id,
                    budget_model_class=Budget,
                    template_name='budget/estimates/delete.html'):
    """
    Delete a estimate object.

    Templates: ``budget/estimates/delete.html``
    Context:
        budget
            the parent budget object for the estimate
        estimate
            the existing estimate object
    """
    budget = get_object_or_404(budget_model_class.active.all(),
                               slug=budget_slug)
    try:
        estimate = budget.estimates.get(pk=estimate_id, is_deleted=False)
    except ObjectDoesNotExist:
        raise Http404("The requested estimate could not be found.")
    if request.POST:
        if request.POST.get('confirmed'):
            estimate.delete()
        return HttpResponseRedirect(
            reverse('budget_estimate_list',
                    kwargs={'budget_slug': budget.slug})
        )
    return render(request, template_name, {
        'budget': budget,
        'estimate': estimate,
    })
