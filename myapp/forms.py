from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import (
    AdmissionRegistration,
    BannerSlide,
    Bundle,
    Category,
    Certificate,
    ChatbotQuestion,
    ChatbotSettings,
    Classroom,
    Coupon,
    Course,
    CustomUser,
    DailyUpdateCard,
    DailyUpdatePost,
    EligibilityCriteria,
    ExamCalendarEvent,
    ExtraPage,
    FAQItem,
    FeeInvoice,
    GalleryImage,
    HeroSection,
    HomepageContent,
    JobApplication,
    JobPosting,
    Notification,
    NotificationProviderSettings,
    Product,
    PWASettings,
    Question,
    QuizQuestion,
    RazorpaySettings,
    ReferralCode,
    ResultHighlight,
    SiteSettings,
    SSOSettings,
    StaffMember,
    StoreOrder,
    Transaction,
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
    referral_code = forms.CharField(
        required=False, max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Referral code (optional)'}),
    )

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

    def clean_referral_code(self):
        code = self.cleaned_data.get('referral_code', '').strip().upper()
        if code and not ReferralCode.objects.filter(code=code).exists():
            raise forms.ValidationError('This referral code is not valid.')
        return code


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
            'profile_picture': forms.FileInput(),
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
            'logo_image': forms.FileInput(),
            'favicon': forms.FileInput(),
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
            'image': forms.FileInput(),
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
            'visual_image': forms.FileInput(),
        }


class DailyUpdateCardForm(forms.ModelForm):
    class Meta:
        model = DailyUpdateCard
        fields = ('title', 'caption', 'button_text', 'visual_type', 'illustration_style', 'image')
        widgets = {
            'visual_type': forms.RadioSelect(),
            'illustration_style': forms.RadioSelect(),
            'image': forms.FileInput(),
        }


class DailyUpdatePostForm(forms.ModelForm):
    class Meta:
        model = DailyUpdatePost
        fields = ('category', 'title', 'body', 'image', 'is_active')
        widgets = {
            'category': forms.Select(),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Union Budget 2026: Key Highlights'}),
            'body': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Full article text'}),
            'image': forms.FileInput(),
        }


class AdmissionRegistrationForm(forms.ModelForm):
    class Meta:
        model = AdmissionRegistration
        fields = ('name', 'phone', 'course', 'preferred_batch')


class PWASettingsForm(forms.ModelForm):
    class Meta:
        model = PWASettings
        fields = (
            'is_enabled',
            'app_name', 'short_name', 'description',
            'theme_color', 'background_color',
            'android_icon', 'ios_icon',
        )
        widgets = {
            'theme_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'android_icon': forms.FileInput(),
            'ios_icon': forms.FileInput(),
        }


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ('title', 'caption', 'image', 'order', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Annual Prize Distribution 2026'}),
            'caption': forms.TextInput(attrs={'placeholder': 'A short line about this photo'}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'image': forms.FileInput(),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'icon', 'order')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. CBSE'}),
            'icon': forms.TextInput(attrs={'placeholder': '📘'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'category', 'name', 'test_type', 'original_price', 'current_price', 'force_free',
            'enable_validity', 'validity_value', 'validity_unit',
            'about', 'thumbnail', 'pdf_file', 'video_file',
            'duration_minutes', 'author', 'pages',
            'order', 'is_active',
        )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL Complete Test Series'}),
            'about': forms.Textarea(attrs={'rows': 5, 'placeholder': 'What this course covers'}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'validity_value': forms.NumberInput(attrs={'min': 1, 'placeholder': 'e.g. 6'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 1, 'placeholder': 'e.g. 60'}),
            'author': forms.TextInput(attrs={'placeholder': 'e.g. R.S. Aggarwal'}),
            'pages': forms.NumberInput(attrs={'min': 1, 'placeholder': 'e.g. 120'}),
            'thumbnail': forms.FileInput(),
            'pdf_file': forms.FileInput(),
            'video_file': forms.FileInput(),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            'question_type', 'text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'marks', 'order',
        )
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type the question here'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
            'marks': forms.NumberInput(attrs={'min': 1}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class NotificationProviderSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationProviderSettings
        fields = (
            'sms_provider_name', 'sms_api_url', 'sms_api_key', 'sms_sender_id',
            'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls',
            'smtp_from_email', 'smtp_from_name',
        )
        widgets = {
            'sms_provider_name': forms.TextInput(attrs={'placeholder': 'e.g. MSG91, Fast2SMS, Twilio'}),
            'sms_api_url': forms.URLInput(attrs={'placeholder': 'https://api.yourprovider.com/send'}),
            'sms_api_key': forms.PasswordInput(attrs={'placeholder': 'API key / auth token', 'autocomplete': 'off'}, render_value=True),
            'sms_sender_id': forms.TextInput(attrs={'placeholder': 'e.g. MNJACD'}),
            'smtp_host': forms.TextInput(attrs={'placeholder': 'smtp.gmail.com'}),
            'smtp_port': forms.NumberInput(attrs={'placeholder': '587'}),
            'smtp_username': forms.TextInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'off'}),
            'smtp_password': forms.PasswordInput(attrs={'placeholder': 'App password', 'autocomplete': 'off'}, render_value=True),
            'smtp_from_email': forms.EmailInput(attrs={'placeholder': 'no-reply@yourdomain.com'}),
            'smtp_from_name': forms.TextInput(attrs={'placeholder': 'Manjunath Academy'}),
        }


class SSOSettingsForm(forms.ModelForm):
    class Meta:
        model = SSOSettings
        fields = (
            'google_enabled', 'google_client_id', 'google_client_secret',
            'facebook_enabled', 'facebook_app_id', 'facebook_app_secret',
        )
        widgets = {
            'google_client_id': forms.TextInput(attrs={'placeholder': 'xxxxxxxxxx.apps.googleusercontent.com', 'autocomplete': 'off'}),
            'google_client_secret': forms.PasswordInput(attrs={'placeholder': 'Google client secret', 'autocomplete': 'off'}, render_value=True),
            'facebook_app_id': forms.TextInput(attrs={'placeholder': 'Facebook App ID', 'autocomplete': 'off'}),
            'facebook_app_secret': forms.PasswordInput(attrs={'placeholder': 'Facebook App secret', 'autocomplete': 'off'}, render_value=True),
        }


class SSOCompleteSignupForm(forms.Form):
    number = forms.CharField(
        max_length=15, label='Phone number',
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number', 'autocomplete': 'off'}),
    )


class RazorpaySettingsForm(forms.ModelForm):
    class Meta:
        model = RazorpaySettings
        fields = ('key_id', 'key_secret')
        widgets = {
            'key_id': forms.TextInput(attrs={'placeholder': 'rzp_live_xxxxxxxxxxxx', 'autocomplete': 'off'}),
            'key_secret': forms.PasswordInput(attrs={'placeholder': 'Your Razorpay key secret', 'autocomplete': 'off'}, render_value=True),
        }
        help_texts = {
            'key_id': 'Found in Razorpay Dashboard → Settings → API Keys.',
            'key_secret': 'Kept private — never shown on the public site.',
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'name', 'description', 'original_price', 'current_price', 'image', 'stock', 'order', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL Complete Notes Set'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What this product includes'}),
            'stock': forms.NumberInput(attrs={'min': 0}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'image': forms.FileInput(),
        }
        help_texts = {
            'image': 'Recommended size: 400×400px.',
            'order': 'Lower numbers show first.',
        }


class StoreCheckoutForm(forms.Form):
    shipping_name = forms.CharField(max_length=150, label='Full name', widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    shipping_phone = forms.CharField(max_length=15, label='Phone number', widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'}))
    shipping_address = forms.CharField(label='Delivery address', widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'House no, street, city, state, PIN code'}))
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'min': 1}))


class StoreOrderStatusForm(forms.ModelForm):
    class Meta:
        model = StoreOrder
        fields = ('status',)


class CouponForm(forms.ModelForm):
    valid_from = forms.DateTimeField(
        required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    valid_until = forms.DateTimeField(
        required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )

    class Meta:
        model = Coupon
        fields = (
            'code', 'description', 'discount_type', 'discount_value', 'max_discount_amount',
            'min_order_amount', 'applies_to', 'valid_from', 'valid_until',
            'usage_limit', 'per_user_limit', 'is_active',
        )
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'e.g. WELCOME50'}),
            'description': forms.TextInput(attrs={'placeholder': 'Internal note, e.g. Launch offer for new students'}),
            'discount_value': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'min_order_amount': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'usage_limit': forms.NumberInput(attrs={'min': 1}),
            'per_user_limit': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()


class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} — {obj.email}'


class CertificateForm(forms.ModelForm):
    user = StudentChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('name'),
        label='Student',
    )

    class Meta:
        model = Certificate
        fields = ('user', 'certificate_type', 'recipient_name', 'course_name', 'description', 'issue_date')
        widgets = {
            'recipient_name': forms.TextInput(attrs={'placeholder': "Leave blank to use the student's account name"}),
            'course_name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL Test Series 2026'}),
            'description': forms.TextInput(attrs={'placeholder': 'Optional, e.g. for scoring 92% in the final mock test'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ('title', 'location', 'job_type', 'experience_required', 'description', 'order', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Faculty — Reasoning & General Studies'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Lucknow centre'}),
            'experience_required': forms.TextInput(attrs={'placeholder': 'e.g. 3+ years teaching experience'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Role details, responsibilities, requirements'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ('name', 'designation', 'department', 'email', 'phone', 'salary', 'date_of_joining', 'photo', 'address', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'e.g. Maths Faculty'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'salary': forms.NumberInput(attrs={'min': 0}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'photo': forms.FileInput(),
        }


class StudentModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} — {obj.email}'


class FeeInvoiceForm(forms.ModelForm):
    student = StudentModelChoiceField(
        queryset=CustomUser.objects.filter(is_superuser=False, is_staff=False).order_by('name'),
    )

    class Meta:
        model = FeeInvoice
        fields = ('student', 'title', 'amount', 'due_date', 'status', 'payment_mode', 'paid_on', 'notes')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL Batch — Term 1 Fee'}),
            'amount': forms.NumberInput(attrs={'min': 0}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'paid_on': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('type', 'category', 'title', 'amount', 'date', 'notes')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. August rent'}),
            'amount': forms.NumberInput(attrs={'min': 0}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ('name', 'email', 'phone', 'resume', 'cover_note')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'cover_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Why should we hire you? (optional)'}),
        }


class FooterSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            'footer_about', 'footer_address', 'footer_phone', 'footer_email', 'copyright_text',
            'facebook_url', 'instagram_url', 'twitter_url', 'telegram_url', 'linkedin_url',
        )
        widgets = {
            'footer_about': forms.Textarea(attrs={'rows': 3}),
            'footer_address': forms.TextInput(attrs={'placeholder': 'e.g. Hazratganj, Lucknow, Uttar Pradesh'}),
            'footer_phone': forms.TextInput(attrs={'placeholder': '+915220000000'}),
            'footer_email': forms.EmailInput(attrs={'placeholder': 'hello@example.com'}),
            'copyright_text': forms.TextInput(attrs={'placeholder': 'Manjunath Academy'}),
            'facebook_url': forms.URLInput(attrs={'placeholder': 'https://facebook.com/yourpage'}),
            'instagram_url': forms.URLInput(attrs={'placeholder': 'https://instagram.com/yourhandle'}),
            'twitter_url': forms.URLInput(attrs={'placeholder': 'https://x.com/yourhandle'}),
            'telegram_url': forms.URLInput(attrs={'placeholder': 'https://t.me/yourchannel'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/company/yourpage'}),
        }
        help_texts = {
            'facebook_url': 'Leave blank to hide this icon in the footer.',
            'instagram_url': 'Leave blank to hide this icon in the footer.',
            'twitter_url': 'Leave blank to hide this icon in the footer.',
            'telegram_url': 'Leave blank to hide this icon in the footer.',
            'linkedin_url': 'Leave blank to hide this icon in the footer.',
        }


class HomepageContentForm(forms.ModelForm):
    class Meta:
        model = HomepageContent
        fields = (
            'results_heading', 'results_subtitle',
            'gallery_heading', 'gallery_subtitle',
            'about_heading', 'about_para1', 'about_para2', 'about_checklist',
            'about_badge_value', 'about_badge_label', 'about_image',
        )
        widgets = {
            'about_para1': forms.Textarea(attrs={'rows': 4}),
            'about_para2': forms.Textarea(attrs={'rows': 4}),
            'about_checklist': forms.Textarea(attrs={'rows': 6}),
            'about_image': forms.FileInput(),
        }
        help_texts = {
            'about_checklist': 'One bullet point per line.',
        }


class ResultHighlightForm(forms.ModelForm):
    class Meta:
        model = ResultHighlight
        fields = ('image', 'caption', 'order', 'is_active')
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'e.g. Health'}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'image': forms.FileInput(),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class CourseMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.get_course_type_display()} — {obj.name}'


class BundleForm(forms.ModelForm):
    courses = CourseMultipleChoiceField(
        queryset=Course.objects.filter(is_active=True).order_by('course_type', 'name'),
        widget=forms.CheckboxSelectMultiple(), required=False,
        help_text='Select every Test Series, Video Course and E-Library item included in this bundle.',
    )

    class Meta:
        model = Bundle
        fields = ('name', 'description', 'courses', 'icon', 'badge_label', 'original_price', 'current_price', 'rating', 'order', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Unified Syllabus Course'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What this bundle includes'}),
            'icon': forms.TextInput(attrs={'placeholder': '🏛'}),
            'badge_label': forms.TextInput(attrs={'placeholder': 'e.g. All Subjects Included'}),
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': '0.1'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class StudentMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.name} — {obj.email}'


class ClassroomForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    end_time = forms.DateTimeField(
        required=False, input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )

    class Meta:
        model = Classroom
        fields = ('name', 'description', 'test_course', 'is_free', 'price', 'start_time', 'end_time', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL Weekend Batch — Mock Test 3'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional notes for this classroom'}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ids = set(
            Course.objects.filter(course_type=Course.TEST_SERIES, questions__isnull=False)
            .values_list('pk', flat=True)
        )
        if self.instance and self.instance.pk:
            ids.add(self.instance.test_course_id)
        self.fields['test_course'].queryset = Course.objects.filter(pk__in=ids).order_by('name')


class ClassroomAddStudentsForm(forms.Form):
    students = StudentMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': 12}),
        required=True,
        label='Select students to add',
    )

    def __init__(self, *args, **kwargs):
        exclude_ids = kwargs.pop('exclude_ids', [])
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = CustomUser.objects.filter(is_active=True).exclude(pk__in=exclude_ids).order_by('name')


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ('level', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'prize_label', 'is_active')
        widgets = {
            'level': forms.NumberInput(attrs={'min': 1}),
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type the question here'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
            'prize_label': forms.TextInput(attrs={'placeholder': 'e.g. ₹10,000'}),
        }
        help_texts = {
            'level': 'Lower levels are asked first — like a difficulty ladder.',
        }


class ExtraPageForm(forms.ModelForm):
    class Meta:
        model = ExtraPage
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Leave blank to use the default title'}),
            'content': forms.Textarea(attrs={'rows': 22, 'placeholder': 'Separate paragraphs with a blank line. Start a line with "- " for a bullet point.'}),
        }


class ExamCalendarEventForm(forms.ModelForm):
    class Meta:
        model = ExamCalendarEvent
        fields = ('exam_name', 'category', 'description', 'event_date', 'official_link', 'order', 'is_active')
        widgets = {
            'exam_name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL 2026 Tier 1 Exam'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g. SSC, Banking, Railways'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Tier 1 exam date, admit card release, last date to apply'}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'official_link': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class FAQItemForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = ('question', 'answer', 'order', 'is_active')
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'e.g. How do I purchase a Test Series?'}),
            'answer': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write the answer here'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class EligibilityCriteriaForm(forms.ModelForm):
    class Meta:
        model = EligibilityCriteria
        fields = (
            'job_name', 'min_education', 'min_age', 'max_age', 'min_height_cm',
            'allowed_gender', 'marital_status', 'allowed_states', 'description', 'order', 'is_active',
        )
        widgets = {
            'job_name': forms.TextInput(attrs={'placeholder': 'e.g. SSC CGL'}),
            'min_age': forms.NumberInput(attrs={'min': 0, 'placeholder': 'e.g. 18'}),
            'max_age': forms.NumberInput(attrs={'min': 0, 'placeholder': 'e.g. 32'}),
            'min_height_cm': forms.NumberInput(attrs={'min': 0, 'placeholder': 'e.g. 157'}),
            'allowed_states': forms.TextInput(attrs={'placeholder': 'Leave blank to allow every state'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'order': 'Lower numbers show first.',
        }


class EligibilityCheckForm(forms.Form):
    education = forms.ChoiceField(choices=EligibilityCriteria.EDUCATION_CHOICES)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Date of birth')
    height_cm = forms.IntegerField(min_value=100, max_value=250, label='Height (cm)', widget=forms.NumberInput(attrs={'placeholder': 'e.g. 168'}))
    state = forms.ChoiceField(choices=[c for c in STATE_CHOICES if c[0]])
    district = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Lucknow'}))
    marital_status = forms.ChoiceField(choices=[('unmarried', 'Unmarried'), ('married', 'Married')])
