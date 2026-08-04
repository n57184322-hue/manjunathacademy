from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import SignupForm


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


def logout_view(request):
    auth_logout(request)
    return redirect('index')
