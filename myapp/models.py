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
