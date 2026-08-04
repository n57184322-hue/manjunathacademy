from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'number', 'age', 'gender', 'state', 'city')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['number'].required = True
        self.fields['age'].required = False
        self.fields['gender'].required = False
        self.fields['state'].required = False
        self.fields['city'].required = False
