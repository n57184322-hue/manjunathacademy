from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import (
    AdmissionRegistration,
    BannerSlide,
    ChatbotQuestion,
    ChatbotSettings,
    CustomUser,
    DailyUpdateCard,
    DailyUpdatePost,
    HeroSection,
    Notification,
    SiteSettings,
)

STATE_CHOICES = [
    ('', 'Select state'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Bihar', 'Bihar'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('Delhi', 'Delhi'),
    ('Other', 'Other'),
]

CITY_CHOICES = [
    ('', 'Select city'),
    ('Lucknow', 'Lucknow'),
    ('Kanpur', 'Kanpur'),
    ('Varanasi', 'Varanasi'),
    ('Prayagraj', 'Prayagraj'),
    ('Ghaziabad', 'Ghaziabad'),
    ('Noida', 'Noida'),
    ('Meerut', 'Meerut'),
    ('Agra', 'Agra'),
    ('Gorakhpur', 'Gorakhpur'),
    ('Bareilly', 'Bareilly'),
    ('Other', 'Other'),
]


class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'number', 'age', 'gender', 'state', 'city')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'number': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'age': forms.NumberInput(attrs={'placeholder': 'e.g. 21', 'min': 10, 'max': 100}),
            'state': forms.Select(choices=STATE_CHOICES),
            'city': forms.Select(choices=CITY_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['number'].required = True
        self.fields['age'].required = False
        self.fields['gender'].required = False
        self.fields['state'].required = False
        self.fields['city'].required = False
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Re-enter password'


class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'you@example.com', 'autofocus': True})
        self.fields['password'].widget.attrs['placeholder'] = 'Your password'


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('profile_picture', 'name', 'number', 'age', 'gender', 'state', 'city')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'number': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'age': forms.NumberInput(attrs={'placeholder': 'e.g. 21', 'min': 10, 'max': 100}),
            'state': forms.Select(choices=STATE_CHOICES),
            'city': forms.Select(choices=CITY_CHOICES),
        }
        help_texts = {
            'profile_picture': 'Square image works best, e.g. 300×300px. Max 2MB.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['number'].required = True
        self.fields['profile_picture'].required = False
        self.fields['age'].required = False
        self.fields['gender'].required = False
        self.fields['state'].required = False
        self.fields['city'].required = False


class NavbarCustomizationForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ('logo_type', 'logo_image', 'favicon', 'youtube_url', 'whatsapp_number')
        widgets = {
            'logo_type': forms.RadioSelect(),
            'youtube_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/@yourchannel'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': 'e.g. 915220000000'}),
        }
        help_texts = {
            'logo_image': 'Recommended size: 200×60px (transparent PNG works best). Max 1MB.',
            'favicon': 'Recommended size: 512×512px, square PNG or ICO. Shown in the browser tab.',
            'whatsapp_number': 'Digits only, with country code, no + or spaces (e.g. 915220000000).',
        }


class BannerSlideForm(forms.ModelForm):
    class Meta:
        model = BannerSlide
        fields = ('kicker', 'title', 'subtitle', 'button_text', 'button_link', 'image', 'image_url', 'order', 'is_active')
        widgets = {
            'kicker': forms.TextInput(attrs={'placeholder': 'e.g. Admissions open'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. New Batch Starting Soon'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'A short supporting line'}),
            'button_text': forms.TextInput(attrs={'placeholder': 'e.g. See the batch plan'}),
            'button_link': forms.TextInput(attrs={'placeholder': 'e.g. #popular-courses'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/photo.jpg'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'image': 'Recommended size: 1400×500px (wide photo). JPG or PNG, under 2MB.',
            'image_url': 'Used only if no image is uploaded above.',
            'order': 'Lower numbers show first.',
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('text', 'detail', 'link', 'order', 'is_active')
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'e.g. 📢 SSC CGL 2026 notification released — 4,500+ vacancies'}),
            'detail': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Longer text shown when a student taps this notification'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://ssc.nic.in/...'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'text': 'Shown in the scrolling ticker at the top of the site.',
            'link': 'Optional. Opens as the "Official notification link" button in the popup.',
            'order': 'Lower numbers show first.',
        }


class ChatbotSettingsForm(forms.ModelForm):
    class Meta:
        model = ChatbotSettings
        fields = ('is_enabled',)


class ChatbotQuestionForm(forms.ModelForm):
    class Meta:
        model = ChatbotQuestion
        fields = ('question', 'answer', 'order', 'is_active')
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'e.g. What courses do you offer?'}),
            'answer': forms.Textarea(attrs={'rows': 4, 'placeholder': 'The reply shown when a visitor taps this question'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = (
            'badge_text', 'badge_highlight',
            'heading_prefix', 'heading_highlight', 'heading_suffix',
            'subtitle',
            'primary_btn_text', 'primary_btn_link',
            'secondary_btn_text', 'secondary_btn_link',
            'stat1_number', 'stat1_label',
            'stat2_number', 'stat2_label',
            'stat3_number', 'stat3_label',
            'badge1_value', 'badge1_title', 'badge1_subtitle',
            'badge2_value', 'badge2_title', 'badge2_subtitle',
            'visual_type', 'illustration_style', 'visual_image', 'visual_video_url',
        )
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 3}),
            'visual_type': forms.RadioSelect(),
            'illustration_style': forms.RadioSelect(),
            'primary_btn_link': forms.TextInput(attrs={'placeholder': 'e.g. #admission or a full https:// URL'}),
            'secondary_btn_link': forms.TextInput(attrs={'placeholder': 'e.g. #popular-courses or a full https:// URL'}),
            'visual_video_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/watch?v=...'}),
        }


class DailyUpdateCardForm(forms.ModelForm):
    class Meta:
        model = DailyUpdateCard
        fields = ('title', 'caption', 'button_text', 'visual_type', 'illustration_style', 'image')
        widgets = {
            'visual_type': forms.RadioSelect(),
            'illustration_style': forms.RadioSelect(),
        }


class DailyUpdatePostForm(forms.ModelForm):
    class Meta:
        model = DailyUpdatePost
        fields = ('category', 'title', 'body', 'image', 'is_active')
        widgets = {
            'category': forms.Select(),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Union Budget 2026: Key Highlights'}),
            'body': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Full article text'}),
        }


class AdmissionRegistrationForm(forms.ModelForm):
    class Meta:
        model = AdmissionRegistration
        fields = ('name', 'phone', 'course', 'preferred_batch')
