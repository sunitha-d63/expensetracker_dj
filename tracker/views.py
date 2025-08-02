from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ExpenseForm
from .models import Expense
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Sum

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user, date__month=now().month)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    breakdown = expenses.values('category').annotate(total=Sum('amount'))
    return render(request, 'tracker/dashboard.html', {
        'expenses': expenses,
        'total': total,
        'breakdown': breakdown
    })

@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect('dashboard')
    return render(request, 'tracker/expense_form.html', {'form': form})

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'tracker/expense_form.html', {'form': form})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})

@login_required
def admin_view_all_expenses(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    users = User.objects.all()
    all_expenses = Expense.objects.all()
    return render(request, 'tracker/admin_all_expenses.html', {
        'users': users,
        'expenses': all_expenses
    })
