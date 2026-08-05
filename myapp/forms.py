from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser

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
