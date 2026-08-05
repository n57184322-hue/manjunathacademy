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
