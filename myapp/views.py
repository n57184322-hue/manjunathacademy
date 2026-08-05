from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import AccountUpdateForm, EmailAuthenticationForm, SignupForm
from .models import CustomUser


def index(request):
    return render(request, 'myapp/index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = SignupForm()

    return render(request, 'myapp/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'myapp/login.html'
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return '/panel/'
        return super().get_success_url()


def logout_view(request):
    auth_logout(request)
    return redirect('index')


@login_required(login_url='login')
def account_edit(request):
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account details have been updated.')
            return redirect('account_edit')
    else:
        form = AccountUpdateForm(instance=request.user)

    return render(request, 'myapp/account/edit.html', {'form': form})


class AccountPasswordChangeView(PasswordChangeView):
    template_name = 'myapp/account/password_change.html'
    success_url = reverse_lazy('account_password')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been changed.')
        return response


@login_required(login_url='login')
def account_purchases(request):
    return render(request, 'myapp/account/purchases.html')


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signups(request):
    users = CustomUser.objects.order_by('-date_joined')
    week_ago = timezone.now() - timezone.timedelta(days=7)
    stats = {
        'total': users.count(),
        'admins': users.filter(is_superuser=True).count(),
        'students': users.filter(is_superuser=False).count(),
        'this_week': users.filter(date_joined__gte=week_ago).count(),
    }
    return render(request, 'myapp/panel/signups_list.html', {'users': users, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signup_add(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('panel_signups')
    else:
        form = SignupForm()

    return render(request, 'myapp/panel/signup_add.html', {'form': form})
