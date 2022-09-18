from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import DepositForm, WithdrawalForm

from bson.decimal128 import Decimal128, create_decimal128_context
import decimal

D128_CTX = create_decimal128_context()


@login_required()
def deposit_view(request):
    form = DepositForm(request.POST or None)

    if form.is_valid():
        deposit = form.save(commit=False)
        deposit.user = request.user
        deposit.save()
        # adds users deposit to balance.
        with decimal.localcontext(D128_CTX):
            d1 = Decimal128(str(deposit.user.account.balance))
            d2 = Decimal128(deposit.amount)
            d3 = Decimal128(d1.to_decimal() + d2.to_decimal())
        deposit.user.account.balance = d3.to_decimal()
        deposit.user.account.save()
        messages.success(request, 'You Have Deposited {} $.'
                         .format(deposit.amount))
        return redirect("home")

    context = {
        "title": "Deposit",
        "form": form
    }
    return render(request, "transactions/form.html", context)


@login_required()
def withdrawal_view(request):
    form = WithdrawalForm(request.POST or None, user=request.user)

    if form.is_valid():
        withdrawal = form.save(commit=False)
        withdrawal.user = request.user
        withdrawal.save()
        # subtracts users withdrawal from balance.
        with decimal.localcontext(D128_CTX):
            d1 = Decimal128(str(withdrawal.user.account.balance))
            d2 = Decimal128(withdrawal.amount)
            d3 = Decimal128(d1.to_decimal() - d2.to_decimal())
        withdrawal.user.account.balance = d3.to_decimal()
        withdrawal.user.account.save()

        messages.success(
            request, 'You Have Withdrawn {} $.'.format(withdrawal.amount)
        )
        return redirect("home")

    context = {
        "title": "Withdraw",
        "form": form
    }
    return render(request, "transactions/form.html", context)
