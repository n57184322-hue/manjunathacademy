import re

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, number, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')
        if not number:
            raise ValueError('Users must have a phone number')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, number=number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=15)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'number']

    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    LOGO_TEXT = 'text'
    LOGO_IMAGE = 'image'
    LOGO_TYPE_CHOICES = [
        (LOGO_TEXT, 'Text logo'),
        (LOGO_IMAGE, 'Image logo'),
    ]

    logo_type = models.CharField(max_length=10, choices=LOGO_TYPE_CHOICES, default=LOGO_TEXT)
    logo_image = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    youtube_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, help_text='Digits only, with country code, e.g. 915220000000')

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_link(self):
        return f'https://wa.me/{self.whatsapp_number}' if self.whatsapp_number else ''

    def __str__(self):
        return 'Site settings'


class BannerSlide(models.Model):
    order = models.PositiveIntegerField(default=0)
    kicker = models.CharField(max_length=100, blank=True, help_text='Small label above the title, e.g. "Admissions open"')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=300, blank=True, help_text='e.g. #popular-courses or a full https:// URL')
    image = models.ImageField(upload_to='banner/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text='Used only if no image is uploaded above')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.title


class Notification(models.Model):
    order = models.PositiveIntegerField(default=0)
    text = models.CharField(max_length=200, help_text='Short scrolling line, e.g. "SSC CGL 2026 notification released — 4,500+ vacancies"')
    detail = models.TextField(blank=True, help_text='Longer text shown in the popup when a student taps this notification')
    link = models.URLField(blank=True, help_text='Official link (apply page, PDF, etc). Shown as a button in the popup.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.text


class ChatbotSettings(models.Model):
    is_enabled = models.BooleanField(default=True, help_text='Show or hide the chat widget on the site')

    class Meta:
        verbose_name = 'Chatbot settings'
        verbose_name_plural = 'Chatbot settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Chatbot settings'


class ChatbotQuestion(models.Model):
    order = models.PositiveIntegerField(default=0)
    question = models.CharField(max_length=200)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class HeroSection(models.Model):
    VISUAL_ILLUSTRATION = 'illustration'
    VISUAL_IMAGE = 'image'
    VISUAL_VIDEO = 'video'
    VISUAL_TYPE_CHOICES = [
        (VISUAL_ILLUSTRATION, 'Default illustration'),
        (VISUAL_IMAGE, 'Image'),
        (VISUAL_VIDEO, 'Video'),
    ]

    ILLUSTRATION_CHOICES = [
        ('study', 'Studying with a laptop'),
        ('reading', 'Reading a book'),
        ('graduate', 'Graduation success'),
        ('online_class', 'Live online class'),
        ('exam', 'Writing an exam'),
    ]

    badge_text = models.CharField(max_length=80, blank=True, default='New batches starting')
    badge_highlight = models.CharField(max_length=80, blank=True, default='Enroll free', help_text='Shown after the small dot in the badge pill')

    heading_prefix = models.CharField(max_length=100, blank=True, default='Crack Any', help_text='First line of the heading')
    heading_highlight = models.CharField(max_length=100, blank=True, default='Govt Exam', help_text='Highlighted (orange) part of the heading')
    heading_suffix = models.CharField(max_length=100, blank=True, default='with confidence', help_text='Rest of the heading, after the highlight')

    subtitle = models.TextField(blank=True, default='Live classes, free PYQs, mock tests, expert guidance, doubt solving, and a focused roadmap for serious exam aspirants.')

    primary_btn_text = models.CharField(max_length=50, blank=True, default='Start learning free')
    primary_btn_link = models.CharField(max_length=300, blank=True, default='#admission')
    secondary_btn_text = models.CharField(max_length=50, blank=True, default='Browse courses')
    secondary_btn_link = models.CharField(max_length=300, blank=True, default='#popular-courses')

    stat1_number = models.CharField(max_length=20, blank=True, default='12,400+')
    stat1_label = models.CharField(max_length=60, blank=True, default='Students taught')
    stat2_number = models.CharField(max_length=20, blank=True, default='820')
    stat2_label = models.CharField(max_length=60, blank=True, default='Final selections')
    stat3_number = models.CharField(max_length=20, blank=True, default='1,100+')
    stat3_label = models.CharField(max_length=60, blank=True, default='Free video lessons')

    badge1_value = models.CharField(max_length=10, blank=True, default='98%', help_text='e.g. 98%')
    badge1_title = models.CharField(max_length=60, blank=True, default='Success Rate')
    badge1_subtitle = models.CharField(max_length=100, blank=True, default='Govt exam selections')
    badge2_value = models.CharField(max_length=10, blank=True, default='AI', help_text='e.g. AI')
    badge2_title = models.CharField(max_length=60, blank=True, default='Free Access')
    badge2_subtitle = models.CharField(max_length=100, blank=True, default='Mock tests & guidance')

    visual_type = models.CharField(max_length=15, choices=VISUAL_TYPE_CHOICES, default=VISUAL_ILLUSTRATION)
    illustration_style = models.CharField(max_length=20, choices=ILLUSTRATION_CHOICES, default='study', help_text='Used when visual type is "Default illustration".')
    visual_image = models.ImageField(upload_to='hero/', blank=True, null=True, help_text='Used when visual type is "Image". Recommended size: 520×420px.')
    visual_video_url = models.URLField(blank=True, help_text='Used when visual type is "Video". Paste a normal YouTube/Vimeo link, or a direct .mp4 link.')

    class Meta:
        verbose_name = 'Hero section'
        verbose_name_plural = 'Hero section'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def visual_video_is_direct_file(self):
        return bool(self.visual_video_url) and self.visual_video_url.lower().split('?')[0].endswith(('.mp4', '.webm', '.ogg'))

    @property
    def visual_video_embed_url(self):
        url = self.visual_video_url
        if not url:
            return ''
        youtube_match = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{6,})', url)
        if youtube_match:
            return f'https://www.youtube.com/embed/{youtube_match.group(1)}'
        vimeo_match = re.search(r'vimeo\.com/(\d+)', url)
        if vimeo_match:
            return f'https://player.vimeo.com/video/{vimeo_match.group(1)}'
        return url

    def __str__(self):
        return 'Hero section'


class DailyUpdateCard(models.Model):
    CURRENT_AFFAIRS = 'current_affairs'
    DAILY_NEWS = 'daily_news'
    KEY_CHOICES = [
        (CURRENT_AFFAIRS, 'Current Affairs'),
        (DAILY_NEWS, 'Daily News'),
    ]

    VISUAL_ILLUSTRATION = 'illustration'
    VISUAL_IMAGE = 'image'
    VISUAL_TYPE_CHOICES = [
        (VISUAL_ILLUSTRATION, 'Default illustration'),
        (VISUAL_IMAGE, 'Image'),
    ]

    ILLUSTRATION_CHOICES = [
        ('reading', 'Reading on a couch'),
        ('quiz', 'On a video call'),
        ('news', 'Reading the newspaper'),
    ]

    key = models.CharField(max_length=20, choices=KEY_CHOICES, unique=True)
    title = models.CharField(max_length=100)
    caption = models.CharField(max_length=200, blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    visual_type = models.CharField(max_length=15, choices=VISUAL_TYPE_CHOICES, default=VISUAL_ILLUSTRATION)
    illustration_style = models.CharField(max_length=15, choices=ILLUSTRATION_CHOICES, default='reading')
    image = models.ImageField(upload_to='daily_updates/', blank=True, null=True, help_text='Used when visual type is "Image". Recommended size: 340×190px.')

    DEFAULTS = {
        CURRENT_AFFAIRS: {
            'title': 'Current Affairs',
            'caption': 'Brief updates on all the recent happening',
            'button_text': 'Continue Reading',
            'illustration_style': 'reading',
        },
        DAILY_NEWS: {
            'title': 'Daily News',
            'caption': 'Daily nuggets of news for you to ponder on',
            'button_text': 'Read Now',
            'illustration_style': 'quiz',
        },
    }

    class Meta:
        ordering = ['key']
        verbose_name = 'Daily update card'

    @classmethod
    def load(cls, key):
        obj, _ = cls.objects.get_or_create(key=key, defaults={'key': key, **cls.DEFAULTS[key]})
        return obj

    def __str__(self):
        return self.title


class DailyUpdatePost(models.Model):
    CURRENT_AFFAIRS = DailyUpdateCard.CURRENT_AFFAIRS
    DAILY_NEWS = DailyUpdateCard.DAILY_NEWS
    CATEGORY_CHOICES = DailyUpdateCard.KEY_CHOICES

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='daily_updates/posts/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AdmissionRegistration(models.Model):
    COURSE_CHOICES = [
        ('SSC & Railways', 'SSC & Railways'),
        ('Banking & Insurance', 'Banking & Insurance'),
        ('NEET & JEE foundation', 'NEET & JEE foundation'),
    ]
    BATCH_CHOICES = [
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
    ]

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    preferred_batch = models.CharField(max_length=20, choices=BATCH_CHOICES, default='Morning')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.course}'


class PWASettings(models.Model):
    is_enabled = models.BooleanField(default=True, help_text='Show the "Install App" button on the site')
    app_name = models.CharField(max_length=100, blank=True, default='Manjunath Academy', help_text='Full app name shown during install')
    short_name = models.CharField(max_length=30, blank=True, default='Manjunath', help_text='Short name shown under the home screen icon (12 characters or less looks best)')
    description = models.CharField(max_length=200, blank=True, default='Coaching for SSC, Railway, Banking, NEET & JEE exams.')
    theme_color = models.CharField(max_length=7, blank=True, default='#F97316', help_text='Hex color, e.g. #F97316. Used for the browser/app toolbar color.')
    background_color = models.CharField(max_length=7, blank=True, default='#FFFCFA', help_text='Hex color, e.g. #FFFCFA. Used for the splash screen background.')
    android_icon = models.ImageField(upload_to='pwa/', blank=True, null=True, help_text='Square icon for Android/Chrome. Recommended: 512×512px PNG.')
    ios_icon = models.ImageField(upload_to='pwa/', blank=True, null=True, help_text='Square icon for iOS/Safari home screen. Recommended: 180×180px PNG. Falls back to the Android icon if left empty.')

    class Meta:
        verbose_name = 'App (PWA) settings'
        verbose_name_plural = 'App (PWA) settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def effective_ios_icon(self):
        return self.ios_icon or self.android_icon

    def __str__(self):
        return 'App (PWA) settings'


class GalleryImage(models.Model):
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=150, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='gallery/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'Gallery image {self.pk}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, blank=True, help_text='Optional emoji icon, e.g. 📘')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Course(models.Model):
    TEST_SERIES = 'test_series'
    VIDEO_COURSE = 'video_course'
    ELIBRARY = 'elibrary'
    TYPE_CHOICES = [
        (TEST_SERIES, 'Test Series'),
        (VIDEO_COURSE, 'Video Course'),
        (ELIBRARY, 'E-Library'),
    ]

    TEST_TYPE_CHOICES = [
        ('mock_test', 'Mock Test'),
        ('practice_test', 'Practice Test'),
        ('sectional_test', 'Sectional Test'),
        ('sample_papers', 'Sample Papers'),
        ('previous_year_paper', 'Previous Year Paper'),
    ]

    VALIDITY_DAYS = 'days'
    VALIDITY_MONTHS = 'months'
    VALIDITY_UNIT_CHOICES = [
        (VALIDITY_DAYS, 'Days'),
        (VALIDITY_MONTHS, 'Months'),
    ]

    course_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    name = models.CharField(max_length=200, verbose_name='Course name')
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES, blank=True, help_text='Used for Test Series only — e.g. Mock Test, Practice Test.')
    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    current_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    enable_validity = models.BooleanField(default=False, help_text='Turn on if access to this course expires after a validity period')
    validity_value = models.PositiveIntegerField(null=True, blank=True, help_text='Length of access, e.g. 6')
    validity_unit = models.CharField(max_length=10, choices=VALIDITY_UNIT_CHOICES, default=VALIDITY_MONTHS, blank=True)
    about = models.TextField(blank=True, verbose_name='About course')
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True, help_text='Recommended size: 400×240px (16:10).')
    pdf_file = models.FileField(upload_to='elibrary_pdfs/', blank=True, null=True, help_text='Used for E-Library only. Upload the book/notes as a PDF.')
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True, help_text='Used for Video Courses only. Upload the course video (MP4 recommended).')
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text='Video length in minutes (Video Course) or time limit in minutes (Test Series).')
    author = models.CharField(max_length=150, blank=True, help_text='Used for E-Library only.')
    pages = models.PositiveIntegerField(null=True, blank=True, help_text='Used for E-Library only — number of pages.')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    @property
    def is_free(self):
        return not self.current_price or self.current_price <= 0

    def __str__(self):
        return self.name


class CourseEnrollment(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False, help_text='True once payment is confirmed (or the course is free).')
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def save(self, *args, **kwargs):
        if self.pk is None and self.expires_at is None and self.course.enable_validity and self.course.validity_value:
            from datetime import timedelta

            from django.utils import timezone as dj_timezone

            if self.course.validity_unit == self.course.VALIDITY_DAYS:
                days = self.course.validity_value
            else:
                days = self.course.validity_value * 30
            self.expires_at = dj_timezone.now() + timedelta(days=days)
        super().save(*args, **kwargs)

    def grant_paid_access(self, amount_paid=0, razorpay_order_id='', razorpay_payment_id=''):
        from datetime import timedelta

        from django.utils import timezone as dj_timezone

        self.is_paid = True
        self.amount_paid = amount_paid
        self.razorpay_order_id = razorpay_order_id
        self.razorpay_payment_id = razorpay_payment_id
        if self.course.enable_validity and self.course.validity_value:
            if self.course.validity_unit == self.course.VALIDITY_DAYS:
                days = self.course.validity_value
            else:
                days = self.course.validity_value * 30
            self.expires_at = dj_timezone.now() + timedelta(days=days)
        self.save()

    @property
    def is_expired(self):
        from django.utils import timezone as dj_timezone

        return self.expires_at is not None and self.expires_at < dj_timezone.now()

    @property
    def has_access(self):
        return self.is_paid and not self.is_expired

    def __str__(self):
        return f'{self.user} — {self.course}'


class Question(models.Model):
    SINGLE = 'single'
    MULTIPLE = 'multiple'
    NUMERIC = 'numeric'
    TRUE_FALSE = 'true_false'
    FILL_BLANK = 'fill_blank'
    TYPE_CHOICES = [
        (SINGLE, 'Single Correct Answer'),
        (MULTIPLE, 'Multiple Correct Answers'),
        (NUMERIC, 'Numeric Answer'),
        (TRUE_FALSE, 'True / False'),
        (FILL_BLANK, 'Fill in the Blank'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions', limit_choices_to={'course_type': 'test_series'})
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=SINGLE)
    text = models.TextField(verbose_name='Question')
    option_a = models.CharField(max_length=300, blank=True)
    option_b = models.CharField(max_length=300, blank=True)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)
    correct_answer = models.CharField(
        max_length=300, blank=True,
        help_text='Single/True-False: e.g. A or True. Multiple: comma-separated, e.g. A,C. Numeric/Fill-in-the-blank: the exact value.',
    )
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:60]


class TestAttempt(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='test_attempts')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attempts', limit_choices_to={'course_type': 'test_series'})
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ['-started_at']

    @property
    def is_submitted(self):
        return self.submitted_at is not None

    def __str__(self):
        return f'{self.user} — {self.course} ({self.score}/{self.total_marks})'


class TestAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='+')
    submitted_answer = models.CharField(max_length=300, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'{self.attempt} — {self.question_id}'


class RazorpaySettings(models.Model):
    key_id = models.CharField(max_length=100, blank=True, verbose_name='Razorpay Key ID')
    key_secret = models.CharField(max_length=100, blank=True, verbose_name='Razorpay Key Secret')

    class Meta:
        verbose_name = 'Razorpay settings'
        verbose_name_plural = 'Razorpay settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def is_configured(self):
        return bool(self.key_id and self.key_secret)

    def __str__(self):
        return 'Razorpay settings'


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    current_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to='store/', blank=True, null=True, help_text='Recommended size: 400×400px.')
    stock = models.PositiveIntegerField(default=0, help_text='Units available. Buying is disabled at 0.')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class StoreOrder(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='store_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.product} × {self.quantity}'


class JobPosting(models.Model):
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    REMOTE = 'remote'
    INTERNSHIP = 'internship'
    JOB_TYPE_CHOICES = [
        (FULL_TIME, 'Full-time'),
        (PART_TIME, 'Part-time'),
        (REMOTE, 'Remote'),
        (INTERNSHIP, 'Internship'),
    ]

    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150, blank=True, help_text='e.g. Lucknow centre')
    job_type = models.CharField(max_length=15, choices=JOB_TYPE_CHOICES, default=FULL_TIME)
    experience_required = models.CharField(max_length=100, blank=True, help_text='e.g. 3+ years teaching experience')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='career_resumes/', blank=True, null=True)
    cover_note = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.name} — {self.job}'
