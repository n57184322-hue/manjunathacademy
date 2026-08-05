from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (
    AccountUpdateForm,
    BannerSlideForm,
    ChatbotQuestionForm,
    ChatbotSettingsForm,
    EmailAuthenticationForm,
    HeroSectionForm,
    NavbarCustomizationForm,
    NotificationForm,
    SignupForm,
)
from .models import BannerSlide, ChatbotQuestion, ChatbotSettings, CustomUser, HeroSection, Notification, SiteSettings


def index(request):
    banner_slides = BannerSlide.objects.filter(is_active=True)
    return render(request, 'myapp/index.html', {'banner_slides': banner_slides})


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
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
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
    # Superadmin/admin accounts are internal and never listed as signups.
    students = CustomUser.objects.filter(is_superuser=False)
    week_ago = timezone.now() - timezone.timedelta(days=7)
    stats = {
        'total': students.count(),
        'admins': CustomUser.objects.filter(is_superuser=True).count(),
        'students': students.count(),
        'this_week': students.filter(date_joined__gte=week_ago).count(),
    }
    users = students.order_by('-date_joined')
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


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_navbar_customization(request):
    site_settings = SiteSettings.load()
    if request.method == 'POST':
        form = NavbarCustomizationForm(request.POST, request.FILES, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Navbar customization saved.')
            return redirect('panel_navbar_customization')
    else:
        form = NavbarCustomizationForm(instance=site_settings)

    return render(request, 'myapp/panel/navbar_customization.html', {'form': form, 'site_settings': site_settings})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_list(request):
    slides = BannerSlide.objects.all()
    return render(request, 'myapp/panel/banner_list.html', {'slides': slides})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_add(request):
    if request.method == 'POST':
        form = BannerSlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner slide added.')
            return redirect('panel_banner_list')
    else:
        form = BannerSlideForm(initial={'order': BannerSlide.objects.count()})

    return render(request, 'myapp/panel/banner_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_edit(request, pk):
    slide = get_object_or_404(BannerSlide, pk=pk)

    if request.method == 'POST':
        form = BannerSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner slide updated.')
            return redirect('panel_banner_list')
    else:
        form = BannerSlideForm(instance=slide)

    return render(request, 'myapp/panel/banner_form.html', {'form': form, 'is_new': False, 'slide': slide})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_banner_delete(request, pk):
    slide = get_object_or_404(BannerSlide, pk=pk)
    if request.method == 'POST':
        slide.delete()
        messages.success(request, 'Banner slide deleted.')
    return redirect('panel_banner_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_list(request):
    notifications = Notification.objects.all()
    return render(request, 'myapp/panel/notification_list.html', {'notifications': notifications})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_add(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification added.')
            return redirect('panel_notification_list')
    else:
        form = NotificationForm(initial={'order': Notification.objects.count()})

    return render(request, 'myapp/panel/notification_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification updated.')
            return redirect('panel_notification_list')
    else:
        form = NotificationForm(instance=notification)

    return render(request, 'myapp/panel/notification_form.html', {'form': form, 'is_new': False, 'notification': notification})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted.')
    return redirect('panel_notification_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_list(request):
    settings_obj = ChatbotSettings.load()
    if request.method == 'POST':
        settings_form = ChatbotSettingsForm(request.POST, instance=settings_obj)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Chatbot visibility updated.')
            return redirect('panel_chatbot_list')
    else:
        settings_form = ChatbotSettingsForm(instance=settings_obj)

    questions = ChatbotQuestion.objects.all()
    return render(request, 'myapp/panel/chatbot_list.html', {'settings_form': settings_form, 'questions': questions})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_add(request):
    if request.method == 'POST':
        form = ChatbotQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added.')
            return redirect('panel_chatbot_list')
    else:
        form = ChatbotQuestionForm(initial={'order': ChatbotQuestion.objects.count()})

    return render(request, 'myapp/panel/chatbot_question_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_edit(request, pk):
    question = get_object_or_404(ChatbotQuestion, pk=pk)

    if request.method == 'POST':
        form = ChatbotQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated.')
            return redirect('panel_chatbot_list')
    else:
        form = ChatbotQuestionForm(instance=question)

    return render(request, 'myapp/panel/chatbot_question_form.html', {'form': form, 'is_new': False, 'question': question})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_chatbot_question_delete(request, pk):
    question = get_object_or_404(ChatbotQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('panel_chatbot_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_hero_section(request):
    hero = HeroSection.load()
    if request.method == 'POST':
        form = HeroSectionForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section updated.')
            return redirect('panel_hero_section')
    else:
        form = HeroSectionForm(instance=hero)

    return render(request, 'myapp/panel/hero_section.html', {'form': form, 'hero': hero})





