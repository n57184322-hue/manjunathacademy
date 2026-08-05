from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (
    AccountUpdateForm,
    AdmissionRegistrationForm,
    BannerSlideForm,
    CategoryForm,
    ChatbotQuestionForm,
    ChatbotSettingsForm,
    CourseForm,
    DailyUpdateCardForm,
    DailyUpdatePostForm,
    EmailAuthenticationForm,
    GalleryImageForm,
    HeroSectionForm,
    NavbarCustomizationForm,
    NotificationForm,
    PWASettingsForm,
    QuestionForm,
    SignupForm,
)
from .models import (
    AdmissionRegistration,
    BannerSlide,
    Category,
    ChatbotQuestion,
    ChatbotSettings,
    Course,
    CourseEnrollment,
    CustomUser,
    DailyUpdateCard,
    DailyUpdatePost,
    GalleryImage,
    HeroSection,
    Notification,
    PWASettings,
    Question,
    SiteSettings,
)


def index(request):
    banner_slides = BannerSlide.objects.filter(is_active=True)

    test_series_courses = Course.objects.filter(course_type=Course.TEST_SERIES, is_active=True)
    video_courses = Course.objects.filter(course_type=Course.VIDEO_COURSE, is_active=True)
    elibrary_items = Course.objects.filter(course_type=Course.ELIBRARY, is_active=True)
    test_series_categories = Category.objects.filter(courses__in=test_series_courses).distinct()

    return render(request, 'myapp/index.html', {
        'banner_slides': banner_slides,
        'test_series_courses': test_series_courses,
        'video_courses': video_courses,
        'elibrary_items': elibrary_items,
        'test_series_categories': test_series_categories,
    })


def pwa_manifest(request):
    pwa = PWASettings.load()
    icons = []
    if pwa.android_icon:
        icons.append({'src': pwa.android_icon.url, 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'})
        icons.append({'src': pwa.android_icon.url, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'})

    return JsonResponse({
        'name': pwa.app_name,
        'short_name': pwa.short_name,
        'description': pwa.description,
        'start_url': '/',
        'scope': '/',
        'display': 'standalone',
        'background_color': pwa.background_color,
        'theme_color': pwa.theme_color,
        'icons': icons,
    })


def service_worker(request):
    js = (
        "self.addEventListener('install', function (e) { self.skipWaiting(); });\n"
        "self.addEventListener('activate', function (e) { self.clients.claim(); });\n"
        "self.addEventListener('fetch', function (e) {\n"
        "  e.respondWith(fetch(e.request).catch(function () { return caches.match(e.request); }));\n"
        "});\n"
    )
    return HttpResponse(js, content_type='application/javascript')


def daily_updates_page(request, category):
    if category not in dict(DailyUpdateCard.KEY_CHOICES):
        raise Http404

    card = DailyUpdateCard.load(category)
    posts = DailyUpdatePost.objects.filter(category=category, is_active=True)
    return render(request, 'myapp/daily_updates_page.html', {'card': card, 'posts': posts})


def gallery_page(request):
    images = GalleryImage.objects.filter(is_active=True)
    return render(request, 'myapp/gallery_page.html', {'images': images})


def admission_register(request):
    if request.method != 'POST':
        raise Http404

    form = AdmissionRegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


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
    enrollments = request.user.enrollments.select_related('course', 'course__category')
    return render(request, 'myapp/account/purchases.html', {'enrollments': enrollments})


@login_required(login_url='login')
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    enrollment, _ = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
    return render(request, 'myapp/course_detail.html', {'course': course, 'enrollment': enrollment})


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


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_updates(request):
    current_card = DailyUpdateCard.load(DailyUpdateCard.CURRENT_AFFAIRS)
    news_card = DailyUpdateCard.load(DailyUpdateCard.DAILY_NEWS)

    if request.method == 'POST' and request.POST.get('card') == DailyUpdateCard.CURRENT_AFFAIRS:
        current_form = DailyUpdateCardForm(request.POST, request.FILES, instance=current_card)
        news_form = DailyUpdateCardForm(instance=news_card)
        if current_form.is_valid():
            current_form.save()
            messages.success(request, 'Current Affairs card updated.')
            return redirect('panel_daily_updates')
    elif request.method == 'POST' and request.POST.get('card') == DailyUpdateCard.DAILY_NEWS:
        news_form = DailyUpdateCardForm(request.POST, request.FILES, instance=news_card)
        current_form = DailyUpdateCardForm(instance=current_card)
        if news_form.is_valid():
            news_form.save()
            messages.success(request, 'Daily News card updated.')
            return redirect('panel_daily_updates')
    else:
        current_form = DailyUpdateCardForm(instance=current_card)
        news_form = DailyUpdateCardForm(instance=news_card)

    posts = DailyUpdatePost.objects.all()
    return render(request, 'myapp/panel/daily_updates.html', {
        'current_form': current_form,
        'news_form': news_form,
        'posts': posts,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_add(request):
    if request.method == 'POST':
        form = DailyUpdatePostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post added.')
            return redirect('panel_daily_updates')
    else:
        form = DailyUpdatePostForm()

    return render(request, 'myapp/panel/daily_post_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_edit(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk)

    if request.method == 'POST':
        form = DailyUpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated.')
            return redirect('panel_daily_updates')
    else:
        form = DailyUpdatePostForm(instance=post)

    return render(request, 'myapp/panel/daily_post_form.html', {'form': form, 'is_new': False, 'post': post})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_daily_post_delete(request, pk):
    post = get_object_or_404(DailyUpdatePost, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('panel_daily_updates')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_admissions(request):
    registrations = AdmissionRegistration.objects.all()
    week_ago = timezone.now() - timezone.timedelta(days=7)
    stats = {
        'total': registrations.count(),
        'this_week': registrations.filter(created_at__gte=week_ago).count(),
    }
    return render(request, 'myapp/panel/admissions_list.html', {'registrations': registrations, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_admission_delete(request, pk):
    registration = get_object_or_404(AdmissionRegistration, pk=pk)
    if request.method == 'POST':
        registration.delete()
        messages.success(request, 'Registration deleted.')
    return redirect('panel_admissions')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_pwa_settings(request):
    pwa = PWASettings.load()
    if request.method == 'POST':
        form = PWASettingsForm(request.POST, request.FILES, instance=pwa)
        if form.is_valid():
            form.save()
            messages.success(request, 'App settings saved.')
            return redirect('panel_pwa_settings')
    else:
        form = PWASettingsForm(instance=pwa)

    return render(request, 'myapp/panel/pwa_settings.html', {'form': form, 'pwa': pwa})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_list(request):
    images = GalleryImage.objects.all()
    return render(request, 'myapp/panel/gallery_list.html', {'images': images})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_add(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image added.')
            return redirect('panel_gallery_list')
    else:
        form = GalleryImageForm(initial={'order': GalleryImage.objects.count()})

    return render(request, 'myapp/panel/gallery_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_edit(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)

    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image updated.')
            return redirect('panel_gallery_list')
    else:
        form = GalleryImageForm(instance=image)

    return render(request, 'myapp/panel/gallery_form.html', {'form': form, 'is_new': False, 'image': image})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_gallery_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted.')
    return redirect('panel_gallery_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_list(request):
    categories = Category.objects.all()
    return render(request, 'myapp/panel/category_list.html', {'categories': categories})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('panel_category_list')
    else:
        form = CategoryForm(initial={'order': Category.objects.count()})

    return render(request, 'myapp/panel/category_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('panel_category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'myapp/panel/category_form.html', {'form': form, 'is_new': False, 'category': category})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('panel_category_list')


COURSE_TYPE_LABELS = dict(Course.TYPE_CHOICES)


def _course_type_or_404(course_type):
    if course_type not in COURSE_TYPE_LABELS:
        raise Http404


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_list(request, course_type):
    _course_type_or_404(course_type)
    courses = Course.objects.filter(course_type=course_type)
    return render(request, 'myapp/panel/course_list.html', {
        'courses': courses,
        'course_type': course_type,
        'type_label': COURSE_TYPE_LABELS[course_type],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_add(request, course_type):
    _course_type_or_404(course_type)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.course_type = course_type
            course.save()
            messages.success(request, 'Course added.')
            return redirect('panel_course_list', course_type=course_type)
    else:
        form = CourseForm(initial={'order': Course.objects.filter(course_type=course_type).count()})

    return render(request, 'myapp/panel/course_form.html', {
        'form': form, 'is_new': True, 'course_type': course_type, 'type_label': COURSE_TYPE_LABELS[course_type],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_edit(request, course_type, pk):
    _course_type_or_404(course_type)
    course = get_object_or_404(Course, pk=pk, course_type=course_type)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated.')
            return redirect('panel_course_list', course_type=course_type)
    else:
        form = CourseForm(instance=course)

    return render(request, 'myapp/panel/course_form.html', {
        'form': form, 'is_new': False, 'course': course, 'course_type': course_type, 'type_label': COURSE_TYPE_LABELS[course_type],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_course_delete(request, course_type, pk):
    _course_type_or_404(course_type)
    course = get_object_or_404(Course, pk=pk, course_type=course_type)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
    return redirect('panel_course_list', course_type=course_type)


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    questions = course.questions.all()
    return render(request, 'myapp/panel/question_list.html', {'course': course, 'questions': questions})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_add(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.course = course
            question.save()
            messages.success(request, 'Question added.')
            return redirect('panel_question_list', course_pk=course.pk)
    else:
        form = QuestionForm(initial={'order': course.questions.count()})

    return render(request, 'myapp/panel/question_form.html', {'form': form, 'is_new': True, 'course': course})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_edit(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    question = get_object_or_404(Question, pk=pk, course=course)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated.')
            return redirect('panel_question_list', course_pk=course.pk)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'myapp/panel/question_form.html', {'form': form, 'is_new': False, 'course': course, 'question': question})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_question_delete(request, course_pk, pk):
    course = get_object_or_404(Course, pk=course_pk, course_type=Course.TEST_SERIES)
    question = get_object_or_404(Question, pk=pk, course=course)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('panel_question_list', course_pk=course.pk)





