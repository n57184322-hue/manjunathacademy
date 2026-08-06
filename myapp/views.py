from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import (
    AccountUpdateForm,
    AdmissionRegistrationForm,
    BannerSlideForm,
    BundleForm,
    CareerApplicationForm,
    CategoryForm,
    ChatbotQuestionForm,
    ChatbotSettingsForm,
    CourseForm,
    DailyUpdateCardForm,
    DailyUpdatePostForm,
    EligibilityCheckForm,
    EligibilityCriteriaForm,
    EmailAuthenticationForm,
    FeeInvoiceForm,
    FooterSettingsForm,
    GalleryImageForm,
    HeroSectionForm,
    HomepageContentForm,
    JobPostingForm,
    NavbarCustomizationForm,
    NotificationForm,
    ProductForm,
    PWASettingsForm,
    QuestionForm,
    QuizQuestionForm,
    RazorpaySettingsForm,
    ResultHighlightForm,
    SignupForm,
    StaffMemberForm,
    StoreCheckoutForm,
    StoreOrderStatusForm,
    TransactionForm,
)
from .models import (
    AdmissionRegistration,
    BannerSlide,
    Bundle,
    BundlePurchase,
    Category,
    ChatbotQuestion,
    ChatbotSettings,
    Course,
    CourseEnrollment,
    CustomUser,
    DailyUpdateCard,
    DailyUpdatePost,
    EligibilityCriteria,
    EligibilitySubmission,
    FeeInvoice,
    GalleryImage,
    HeroSection,
    HomepageContent,
    JobApplication,
    JobPosting,
    Notification,
    Product,
    PWASettings,
    Question,
    QuizQuestion,
    RazorpaySettings,
    ResultHighlight,
    SiteSettings,
    StaffAttendance,
    StaffMember,
    StoreOrder,
    TestAnswer,
    TestAttempt,
    Transaction,
)
from .razorpay_utils import RazorpayError, create_order, verify_payment_signature


def index(request):
    banner_slides = BannerSlide.objects.filter(is_active=True)

    test_series_courses = Course.objects.filter(course_type=Course.TEST_SERIES, is_active=True)
    video_courses = Course.objects.filter(course_type=Course.VIDEO_COURSE, is_active=True)
    elibrary_items = Course.objects.filter(course_type=Course.ELIBRARY, is_active=True)
    test_series_categories = Category.objects.filter(courses__in=test_series_courses).distinct()
    store_products = Product.objects.filter(is_active=True)
    jobs = JobPosting.objects.filter(is_active=True)
    bundles = Bundle.objects.filter(is_active=True).prefetch_related('courses')
    homepage_content = HomepageContent.load()
    result_highlights = ResultHighlight.objects.filter(is_active=True)
    gallery_preview = GalleryImage.objects.filter(is_active=True)[:5]

    return render(request, 'myapp/index.html', {
        'banner_slides': banner_slides,
        'test_series_courses': test_series_courses,
        'video_courses': video_courses,
        'elibrary_items': elibrary_items,
        'test_series_categories': test_series_categories,
        'store_products': store_products,
        'jobs': jobs,
        'bundles': bundles,
        'homepage_content': homepage_content,
        'result_highlights': result_highlights,
        'gallery_preview': gallery_preview,
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


def _get_or_create_free_enrollment(user, course):
    """Returns the enrollment for a course, auto-granting access if it's free."""
    enrollment = CourseEnrollment.objects.filter(user=user, course=course).first()
    if course.is_free and (not enrollment or not enrollment.is_paid):
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=user, course=course)
        if not enrollment.is_paid:
            enrollment.grant_paid_access(amount_paid=0)
    return enrollment


@login_required(login_url='login')
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    enrollment = _get_or_create_free_enrollment(request.user, course)

    if not enrollment or not enrollment.is_paid:
        return render(request, 'myapp/course_checkout.html', {'course': course})

    if request.method == 'POST' and enrollment.has_access:
        enrollment.is_completed = 'mark_incomplete' not in request.POST
        enrollment.save()
        return redirect('course_detail', pk=pk)

    return render(request, 'myapp/course_detail.html', {'course': course, 'enrollment': enrollment})


def _grade_answer(question, submitted):
    submitted = (submitted or '').strip()
    correct = (question.correct_answer or '').strip()
    if not submitted or not correct:
        return False
    if question.question_type == Question.MULTIPLE:
        submitted_set = {part.strip().upper() for part in submitted.split(',') if part.strip()}
        correct_set = {part.strip().upper() for part in correct.split(',') if part.strip()}
        return submitted_set == correct_set
    return submitted.strip().lower() == correct.strip().lower()


@login_required(login_url='login')
def test_attempt_start(request, pk):
    course = get_object_or_404(Course, pk=pk, course_type=Course.TEST_SERIES, is_active=True)
    enrollment = _get_or_create_free_enrollment(request.user, course)

    if not enrollment or not enrollment.is_paid:
        return render(request, 'myapp/course_checkout.html', {'course': course})

    if not enrollment.has_access:
        return render(request, 'myapp/test_expired.html', {'course': course, 'enrollment': enrollment})

    if not course.questions.exists():
        messages.info(request, 'No questions have been added to this test yet.')
        return redirect('index')

    attempt = TestAttempt.objects.filter(user=request.user, course=course, submitted_at__isnull=True).first()
    if not attempt:
        attempt = TestAttempt.objects.create(user=request.user, course=course)
    return redirect('test_attempt_take', pk=attempt.pk)


@login_required(login_url='login')
def test_attempt_take(request, pk):
    attempt = get_object_or_404(TestAttempt, pk=pk, user=request.user)
    if attempt.is_submitted:
        return redirect('test_attempt_result', pk=attempt.pk)

    questions = attempt.course.questions.all()

    if request.method == 'POST':
        total_marks = 0
        score = 0
        for question in questions:
            if question.question_type == Question.MULTIPLE:
                submitted = ','.join(request.POST.getlist(f'q_{question.id}'))
            else:
                submitted = request.POST.get(f'q_{question.id}', '')
            is_correct = _grade_answer(question, submitted)
            marks_awarded = question.marks if is_correct else 0
            TestAnswer.objects.update_or_create(
                attempt=attempt, question=question,
                defaults={'submitted_answer': submitted, 'is_correct': is_correct, 'marks_awarded': marks_awarded},
            )
            total_marks += question.marks
            score += marks_awarded

        attempt.total_marks = total_marks
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save()
        return redirect('test_attempt_result', pk=attempt.pk)

    return render(request, 'myapp/test_attempt_take.html', {'attempt': attempt, 'questions': questions})


@login_required(login_url='login')
def test_attempt_result(request, pk):
    attempt = get_object_or_404(TestAttempt, pk=pk, user=request.user)
    answers = attempt.answers.select_related('question')
    return render(request, 'myapp/test_attempt_result.html', {'attempt': attempt, 'answers': answers})


@login_required(login_url='login')
def razorpay_create_order(request):
    if request.method != 'POST':
        raise Http404

    settings_obj = RazorpaySettings.load()
    if not settings_obj.is_configured:
        return JsonResponse({'ok': False, 'error': 'Online payments are not set up yet. Please contact support.'}, status=400)

    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    timestamp = int(timezone.now().timestamp())

    if content_type == 'course':
        course = get_object_or_404(Course, pk=object_id, is_active=True)
        amount = course.current_price
        name = course.name
        receipt = f'course_{course.pk}_{request.user.pk}_{timestamp}'
    elif content_type == 'store':
        order = get_object_or_404(StoreOrder, pk=object_id, user=request.user, status=StoreOrder.STATUS_PENDING)
        amount = order.amount
        name = order.product.name
        receipt = f'store_{order.pk}_{timestamp}'
    elif content_type == 'bundle':
        bundle = get_object_or_404(Bundle, pk=object_id, is_active=True)
        amount = bundle.current_price
        name = bundle.name
        receipt = f'bundle_{bundle.pk}_{request.user.pk}_{timestamp}'
    else:
        raise Http404

    try:
        razorpay_order = create_order(settings_obj.key_id, settings_obj.key_secret, amount, receipt)
    except RazorpayError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=502)

    return JsonResponse({
        'ok': True,
        'order_id': razorpay_order['id'],
        'amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
        'key_id': settings_obj.key_id,
        'name': name,
        'prefill_name': request.user.name,
        'prefill_email': request.user.email,
        'prefill_contact': request.user.number,
    })


@login_required(login_url='login')
def razorpay_verify_payment(request):
    if request.method != 'POST':
        raise Http404

    settings_obj = RazorpaySettings.load()
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')
    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')

    if not verify_payment_signature(settings_obj.key_secret, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return JsonResponse({'ok': False, 'error': 'Payment verification failed.'}, status=400)

    if content_type == 'course':
        course = get_object_or_404(Course, pk=object_id)
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
        enrollment.grant_paid_access(
            amount_paid=course.current_price,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
        )
        if course.course_type == Course.TEST_SERIES:
            redirect_url = reverse('test_attempt_start', args=[course.pk])
        else:
            redirect_url = reverse('course_detail', args=[course.pk])
    elif content_type == 'store':
        order = get_object_or_404(StoreOrder, pk=object_id, user=request.user)
        order.status = StoreOrder.STATUS_PAID
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_payment_id = razorpay_payment_id
        order.save()
        redirect_url = reverse('store_order_success', args=[order.pk])
    elif content_type == 'bundle':
        bundle = get_object_or_404(Bundle, pk=object_id)
        BundlePurchase.objects.create(
            user=request.user, bundle=bundle, amount_paid=bundle.current_price,
            razorpay_order_id=razorpay_order_id, razorpay_payment_id=razorpay_payment_id,
        )
        for course in bundle.courses.all():
            enrollment, _ = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
            if not enrollment.is_paid:
                enrollment.grant_paid_access(amount_paid=0, razorpay_order_id=razorpay_order_id, razorpay_payment_id=razorpay_payment_id)
        redirect_url = reverse('bundle_success', args=[bundle.pk])
    else:
        raise Http404

    return JsonResponse({'ok': True, 'redirect_url': redirect_url})


@login_required(login_url='login')
def store_checkout(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    if request.method == 'POST':
        form = StoreCheckoutForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            order = StoreOrder.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                amount=product.current_price * quantity,
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                shipping_address=form.cleaned_data['shipping_address'],
            )
            return redirect('store_pay', pk=order.pk)
    else:
        form = StoreCheckoutForm(initial={'shipping_name': request.user.name, 'shipping_phone': request.user.number})

    return render(request, 'myapp/store_checkout.html', {'product': product, 'form': form})


@login_required(login_url='login')
def store_pay(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk, user=request.user)
    if order.status != StoreOrder.STATUS_PENDING:
        return redirect('store_order_success', pk=order.pk)
    return render(request, 'myapp/store_pay.html', {'order': order})


@login_required(login_url='login')
def store_order_success(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk, user=request.user)
    return render(request, 'myapp/store_order_success.html', {'order': order})


def career_apply(request, job_pk):
    if request.method != 'POST':
        raise Http404

    job = get_object_or_404(JobPosting, pk=job_pk, is_active=True)
    form = CareerApplicationForm(request.POST, request.FILES)
    if form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required(login_url='login')
def bundle_checkout(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk, is_active=True)
    already_owned = not bundle.courses.exclude(enrollments__user=request.user, enrollments__is_paid=True).exists() and bundle.courses.exists()
    return render(request, 'myapp/bundle_checkout.html', {'bundle': bundle, 'already_owned': already_owned})


@login_required(login_url='login')
def bundle_success(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)
    return render(request, 'myapp/bundle_success.html', {'bundle': bundle})


def _education_rank(value):
    order = [EligibilityCriteria.EDU_10TH, EligibilityCriteria.EDU_12TH, EligibilityCriteria.EDU_GRADUATE, EligibilityCriteria.EDU_POST_GRADUATE]
    return order.index(value) if value in order else 0


def _matches_criteria(criteria, data):
    if _education_rank(data['education']) < _education_rank(criteria.min_education):
        return False
    if criteria.min_age and data['age'] < criteria.min_age:
        return False
    if criteria.max_age and data['age'] > criteria.max_age:
        return False
    if criteria.min_height_cm and data['height_cm'] < criteria.min_height_cm:
        return False
    if criteria.allowed_gender != 'any' and data['gender'] != criteria.allowed_gender:
        return False
    if criteria.marital_status == 'unmarried_only' and data['marital_status'] != 'unmarried':
        return False
    if criteria.allowed_states:
        allowed = [s.strip().lower() for s in criteria.allowed_states.split(',') if s.strip()]
        if allowed and data['state'].strip().lower() not in allowed:
            return False
    return True


@login_required(login_url='login')
def eligibility_check(request):
    result = None
    if request.method == 'POST':
        form = EligibilityCheckForm(request.POST)
        if form.is_valid():
            from datetime import date

            dob = form.cleaned_data['dob']
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            data = {
                'education': form.cleaned_data['education'],
                'gender': form.cleaned_data['gender'],
                'age': age,
                'height_cm': form.cleaned_data['height_cm'],
                'state': form.cleaned_data['state'],
                'marital_status': form.cleaned_data['marital_status'],
            }
            matched = [c for c in EligibilityCriteria.objects.filter(is_active=True) if _matches_criteria(c, data)]

            submission = EligibilitySubmission.objects.create(
                user=request.user,
                education=data['education'],
                gender=data['gender'],
                dob=dob,
                height_cm=data['height_cm'],
                state=data['state'],
                district=form.cleaned_data['district'],
                marital_status=data['marital_status'],
                matched_jobs=', '.join(c.job_name for c in matched),
            )
            result = {'matched': matched, 'age': age, 'submission': submission}
    else:
        form = EligibilityCheckForm()

    return render(request, 'myapp/eligibility_check.html', {'form': form, 'result': result})


@login_required(login_url='login')
def quiz_reset(request):
    if request.method != 'POST':
        raise Http404
    request.session['quiz_level'] = 1
    request.session['quiz_used_fifty'] = False
    request.session['quiz_used_audience'] = False
    request.session['quiz_used_skip'] = False
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def quiz_get_question(request):
    level = request.session.get('quiz_level', 1)
    question = QuizQuestion.objects.filter(is_active=True, level__gte=level).order_by('level', 'id').first()
    if not question:
        return JsonResponse({'ok': True, 'finished': True})
    return JsonResponse({
        'ok': True,
        'finished': False,
        'question': {
            'id': question.pk,
            'level': question.level,
            'text': question.text,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'prize_label': question.prize_label,
        },
        'lifelines_used': {
            'fifty': request.session.get('quiz_used_fifty', False),
            'audience': request.session.get('quiz_used_audience', False),
            'skip': request.session.get('quiz_used_skip', False),
        },
    })


@login_required(login_url='login')
def quiz_submit_answer(request):
    if request.method != 'POST':
        raise Http404
    question = get_object_or_404(QuizQuestion, pk=request.POST.get('question_id'))
    selected = (request.POST.get('selected_option') or '').strip().upper()
    is_correct = selected == question.correct_option

    if is_correct:
        request.session['quiz_level'] = question.level + 1
    return JsonResponse({
        'ok': True,
        'is_correct': is_correct,
        'correct_option': question.correct_option,
        'prize_label': question.prize_label,
    })


@login_required(login_url='login')
def quiz_lifeline_fifty(request):
    question = get_object_or_404(QuizQuestion, pk=request.GET.get('question_id'))
    if request.session.get('quiz_used_fifty'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    import random

    wrong_options = [o for o in ['A', 'B', 'C', 'D'] if o != question.correct_option]
    keep_wrong = random.choice(wrong_options)
    eliminate = [o for o in ['A', 'B', 'C', 'D'] if o not in (question.correct_option, keep_wrong)]
    request.session['quiz_used_fifty'] = True
    return JsonResponse({'ok': True, 'eliminate': eliminate})


@login_required(login_url='login')
def quiz_lifeline_audience(request):
    question = get_object_or_404(QuizQuestion, pk=request.GET.get('question_id'))
    if request.session.get('quiz_used_audience'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    import random

    correct_share = random.randint(55, 80)
    remaining = 100 - correct_share
    others = ['A', 'B', 'C', 'D']
    others.remove(question.correct_option)
    random.shuffle(others)
    splits = [0, 0, 0]
    for i in range(remaining):
        splits[i % 3] += 1
    percentages = {question.correct_option: correct_share}
    for option, share in zip(others, splits):
        percentages[option] = share
    request.session['quiz_used_audience'] = True
    return JsonResponse({'ok': True, 'percentages': percentages})


@login_required(login_url='login')
def quiz_lifeline_skip(request):
    if request.method != 'POST':
        raise Http404
    if request.session.get('quiz_used_skip'):
        return JsonResponse({'ok': False, 'error': 'Lifeline already used.'}, status=400)
    question = get_object_or_404(QuizQuestion, pk=request.POST.get('question_id'))
    request.session['quiz_used_skip'] = True
    request.session['quiz_level'] = question.level + 1
    return JsonResponse({'ok': True})


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


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_razorpay_settings(request):
    settings_obj = RazorpaySettings.load()
    if request.method == 'POST':
        form = RazorpaySettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Razorpay settings saved.')
            return redirect('panel_razorpay_settings')
    else:
        form = RazorpaySettingsForm(instance=settings_obj)

    return render(request, 'myapp/panel/razorpay_settings.html', {'form': form, 'settings_obj': settings_obj})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/panel/store_product_list.html', {'products': products})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added.')
            return redirect('panel_store_product_list')
    else:
        form = ProductForm(initial={'order': Product.objects.count()})

    return render(request, 'myapp/panel/store_product_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
            return redirect('panel_store_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'myapp/panel/store_product_form.html', {'form': form, 'is_new': False, 'product': product})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
    return redirect('panel_store_product_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_orders(request):
    orders = StoreOrder.objects.select_related('product', 'user').exclude(status=StoreOrder.STATUS_PENDING)
    return render(request, 'myapp/panel/store_orders.html', {'orders': orders})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_store_order_update(request, pk):
    order = get_object_or_404(StoreOrder, pk=pk)
    if request.method == 'POST':
        form = StoreOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated.')
    return redirect('panel_store_orders')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_list(request):
    jobs = JobPosting.objects.all()
    return render(request, 'myapp/panel/career_job_list.html', {'jobs': jobs})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_add(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting added.')
            return redirect('panel_career_job_list')
    else:
        form = JobPostingForm(initial={'order': JobPosting.objects.count()})

    return render(request, 'myapp/panel/career_job_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_edit(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated.')
            return redirect('panel_career_job_list')
    else:
        form = JobPostingForm(instance=job)

    return render(request, 'myapp/panel/career_job_form.html', {'form': form, 'is_new': False, 'job': job})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_job_delete(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job posting deleted.')
    return redirect('panel_career_job_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_applications(request):
    applications = JobApplication.objects.select_related('job')
    return render(request, 'myapp/panel/career_applications.html', {'applications': applications})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_career_application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted.')
    return redirect('panel_career_applications')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_footer_settings(request):
    site_settings_obj = SiteSettings.load()
    if request.method == 'POST':
        form = FooterSettingsForm(request.POST, instance=site_settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Footer settings saved.')
            return redirect('panel_footer_settings')
    else:
        form = FooterSettingsForm(instance=site_settings_obj)

    return render(request, 'myapp/panel/footer_settings.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_homepage_content(request):
    content = HomepageContent.load()
    if request.method == 'POST':
        form = HomepageContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homepage content saved.')
            return redirect('panel_homepage_content')
    else:
        form = HomepageContentForm(instance=content)

    return render(request, 'myapp/panel/homepage_content.html', {'form': form, 'content': content})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_list(request):
    results = ResultHighlight.objects.all()
    return render(request, 'myapp/panel/result_list.html', {'results': results})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_add(request):
    if request.method == 'POST':
        form = ResultHighlightForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Result photo added.')
            return redirect('panel_result_list')
    else:
        form = ResultHighlightForm(initial={'order': ResultHighlight.objects.count()})

    return render(request, 'myapp/panel/result_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_edit(request, pk):
    result = get_object_or_404(ResultHighlight, pk=pk)

    if request.method == 'POST':
        form = ResultHighlightForm(request.POST, request.FILES, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, 'Result photo updated.')
            return redirect('panel_result_list')
    else:
        form = ResultHighlightForm(instance=result)

    return render(request, 'myapp/panel/result_form.html', {'form': form, 'is_new': False, 'result': result})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_result_delete(request, pk):
    result = get_object_or_404(ResultHighlight, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Result photo deleted.')
    return redirect('panel_result_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_list(request):
    bundles = Bundle.objects.all().prefetch_related('courses')
    return render(request, 'myapp/panel/bundle_list.html', {'bundles': bundles})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_add(request):
    if request.method == 'POST':
        form = BundleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bundle added.')
            return redirect('panel_bundle_list')
    else:
        form = BundleForm(initial={'order': Bundle.objects.count()})

    return render(request, 'myapp/panel/bundle_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_edit(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)

    if request.method == 'POST':
        form = BundleForm(request.POST, instance=bundle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bundle updated.')
            return redirect('panel_bundle_list')
    else:
        form = BundleForm(instance=bundle)

    return render(request, 'myapp/panel/bundle_form.html', {'form': form, 'is_new': False, 'bundle': bundle})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_bundle_delete(request, pk):
    bundle = get_object_or_404(Bundle, pk=pk)
    if request.method == 'POST':
        bundle.delete()
        messages.success(request, 'Bundle deleted.')
    return redirect('panel_bundle_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_list(request):
    questions = QuizQuestion.objects.all()
    return render(request, 'myapp/panel/quiz_question_list.html', {'questions': questions})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_add(request):
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question added.')
            return redirect('panel_quiz_question_list')
    else:
        form = QuizQuestionForm(initial={'level': QuizQuestion.objects.count() + 1})

    return render(request, 'myapp/panel/quiz_question_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_edit(request, pk):
    question = get_object_or_404(QuizQuestion, pk=pk)

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated.')
            return redirect('panel_quiz_question_list')
    else:
        form = QuizQuestionForm(instance=question)

    return render(request, 'myapp/panel/quiz_question_form.html', {'form': form, 'is_new': False, 'question': question})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_quiz_question_delete(request, pk):
    question = get_object_or_404(QuizQuestion, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('panel_quiz_question_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_list(request):
    criteria = EligibilityCriteria.objects.all()
    return render(request, 'myapp/panel/eligibility_criteria_list.html', {'criteria': criteria})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_add(request):
    if request.method == 'POST':
        form = EligibilityCriteriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eligibility criteria added.')
            return redirect('panel_eligibility_criteria_list')
    else:
        form = EligibilityCriteriaForm(initial={'order': EligibilityCriteria.objects.count()})

    return render(request, 'myapp/panel/eligibility_criteria_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_edit(request, pk):
    criteria = get_object_or_404(EligibilityCriteria, pk=pk)

    if request.method == 'POST':
        form = EligibilityCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eligibility criteria updated.')
            return redirect('panel_eligibility_criteria_list')
    else:
        form = EligibilityCriteriaForm(instance=criteria)

    return render(request, 'myapp/panel/eligibility_criteria_form.html', {'form': form, 'is_new': False, 'criteria': criteria})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_criteria_delete(request, pk):
    criteria = get_object_or_404(EligibilityCriteria, pk=pk)
    if request.method == 'POST':
        criteria.delete()
        messages.success(request, 'Eligibility criteria deleted.')
    return redirect('panel_eligibility_criteria_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_eligibility_submissions(request):
    submissions = EligibilitySubmission.objects.select_related('user')
    stats = {
        'total': submissions.count(),
        'this_week': submissions.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
    }
    return render(request, 'myapp/panel/eligibility_submissions.html', {'submissions': submissions, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_erp_dashboard(request):
    from datetime import date

    from django.db.models import Sum

    today = date.today()
    month_start = today.replace(day=1)

    total_staff = StaffMember.objects.filter(is_active=True).count()
    present_today = StaffAttendance.objects.filter(date=today, status=StaffAttendance.PRESENT).count()

    pending_fees = FeeInvoice.objects.filter(status=FeeInvoice.STATUS_PENDING)
    pending_fees_total = pending_fees.aggregate(total=Sum('amount'))['total'] or 0

    month_income = Transaction.objects.filter(type=Transaction.INCOME, date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
    month_expense = Transaction.objects.filter(type=Transaction.EXPENSE, date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'myapp/panel/erp_dashboard.html', {
        'total_staff': total_staff,
        'present_today': present_today,
        'pending_fees_count': pending_fees.count(),
        'pending_fees_total': pending_fees_total,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_net': month_income - month_expense,
        'recent_transactions': Transaction.objects.all()[:8],
        'overdue_invoices': [inv for inv in pending_fees.select_related('student') if inv.is_overdue][:8],
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_list(request):
    staff = StaffMember.objects.all()
    return render(request, 'myapp/panel/staff_list.html', {'staff': staff})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_add(request):
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added.')
            return redirect('panel_staff_list')
    else:
        form = StaffMemberForm()

    return render(request, 'myapp/panel/staff_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_edit(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)

    if request.method == 'POST':
        form = StaffMemberForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated.')
            return redirect('panel_staff_list')
    else:
        form = StaffMemberForm(instance=staff_member)

    return render(request, 'myapp/panel/staff_form.html', {'form': form, 'is_new': False, 'staff_member': staff_member})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_staff_delete(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    if request.method == 'POST':
        staff_member.delete()
        messages.success(request, 'Staff member deleted.')
    return redirect('panel_staff_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_attendance(request):
    from datetime import date

    date_str = request.POST.get('date') or request.GET.get('date')
    try:
        selected_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        selected_date = date.today()

    staff_list = StaffMember.objects.filter(is_active=True)

    if request.method == 'POST':
        for staff_member in staff_list:
            status = request.POST.get(f'status_{staff_member.pk}')
            if status:
                StaffAttendance.objects.update_or_create(
                    staff=staff_member, date=selected_date, defaults={'status': status},
                )
        messages.success(request, f'Attendance saved for {selected_date:%d %b %Y}.')
        return redirect(f"{reverse('panel_attendance')}?date={selected_date.isoformat()}")

    existing = {a.staff_id: a.status for a in StaffAttendance.objects.filter(date=selected_date)}
    rows = [{'staff': s, 'status': existing.get(s.pk, StaffAttendance.PRESENT)} for s in staff_list]

    return render(request, 'myapp/panel/attendance.html', {
        'rows': rows,
        'selected_date': selected_date,
        'status_choices': StaffAttendance.STATUS_CHOICES,
    })


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_list(request):
    from django.db.models import Sum

    invoices = FeeInvoice.objects.select_related('student')
    stats = {
        'pending_count': invoices.filter(status=FeeInvoice.STATUS_PENDING).count(),
        'pending_total': invoices.filter(status=FeeInvoice.STATUS_PENDING).aggregate(total=Sum('amount'))['total'] or 0,
        'paid_total': invoices.filter(status=FeeInvoice.STATUS_PAID).aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'myapp/panel/fee_list.html', {'invoices': invoices, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_add(request):
    if request.method == 'POST':
        form = FeeInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee invoice created.')
            return redirect('panel_fee_list')
    else:
        form = FeeInvoiceForm()

    return render(request, 'myapp/panel/fee_form.html', {'form': form, 'is_new': True})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_edit(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)

    if request.method == 'POST':
        form = FeeInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee invoice updated.')
            return redirect('panel_fee_list')
    else:
        form = FeeInvoiceForm(instance=invoice)

    return render(request, 'myapp/panel/fee_form.html', {'form': form, 'is_new': False, 'invoice': invoice})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_delete(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Fee invoice deleted.')
    return redirect('panel_fee_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_fee_mark_paid(request, pk):
    invoice = get_object_or_404(FeeInvoice, pk=pk)
    if request.method == 'POST':
        invoice.status = FeeInvoice.STATUS_PAID
        invoice.paid_on = timezone.now().date()
        invoice.payment_mode = request.POST.get('payment_mode') or invoice.payment_mode or 'cash'
        invoice.save()
        messages.success(request, 'Invoice marked as paid.')
    return redirect('panel_fee_list')


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_list(request):
    from django.db.models import Sum

    transactions = Transaction.objects.all()
    stats = {
        'total_income': transactions.filter(type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0,
        'total_expense': transactions.filter(type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0,
    }
    stats['net'] = stats['total_income'] - stats['total_expense']
    return render(request, 'myapp/panel/account_list.html', {'transactions': transactions, 'stats': stats})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction recorded.')
            return redirect('panel_account_list')
    else:
        form = TransactionForm()

    return render(request, 'myapp/panel/account_form.html', {'form': form})


@login_required(login_url='login')
@user_passes_test(_is_staff, login_url='login')
def panel_account_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted.')
    return redirect('panel_account_list')





