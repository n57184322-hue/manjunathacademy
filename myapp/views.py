from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import SignupForm
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
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return '/panel/'
        return super().get_success_url()


def logout_view(request):
    auth_logout(request)
    return redirect('index')


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_signups(request):
    users = CustomUser.objects.order_by('-date_joined')
    return render(request, 'myapp/panel/signups_list.html', {'users': users})


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
