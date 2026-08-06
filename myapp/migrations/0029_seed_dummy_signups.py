# Generated to seed 50 dummy student signups for demo/testing purposes.
import random
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone

MALE_FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
    'Rohan', 'Kabir', 'Aryan', 'Dhruv', 'Karan', 'Yash', 'Rahul', 'Amit', 'Vikram', 'Nikhil',
    'Rajesh', 'Suresh', 'Manoj', 'Deepak', 'Anil',
]
FEMALE_FIRST_NAMES = [
    'Saanvi', 'Ananya', 'Diya', 'Myra', 'Aadhya', 'Kiara', 'Pari', 'Anika', 'Navya', 'Ira',
    'Priya', 'Neha', 'Pooja', 'Sneha', 'Kavya', 'Riya', 'Isha', 'Simran', 'Divya', 'Nisha',
    'Anjali', 'Shreya', 'Meera', 'Radha', 'Sunita',
]
LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Yadav', 'Mishra', 'Tiwari', 'Pandey', 'Chauhan', 'Kumar',
    'Agarwal', 'Jain', 'Rathore', 'Chaturvedi', 'Dubey', 'Shukla', 'Saxena', 'Bhatt', 'Nair', 'Reddy',
]
STATES = ['Uttar Pradesh', 'Bihar', 'Madhya Pradesh', 'Uttarakhand', 'Delhi']
CITIES = ['Lucknow', 'Kanpur', 'Varanasi', 'Prayagraj', 'Ghaziabad', 'Noida', 'Meerut', 'Agra', 'Gorakhpur', 'Bareilly']

EMAIL_MARKER = '.demo'


def seed(apps, schema_editor):
    CustomUser = apps.get_model('myapp', 'CustomUser')

    if CustomUser.objects.filter(email__contains=EMAIL_MARKER).exists():
        return

    rng = random.Random(42)
    people = (
        [(name, 'male') for name in MALE_FIRST_NAMES]
        + [(name, 'female') for name in FEMALE_FIRST_NAMES]
    )
    rng.shuffle(people)

    now = timezone.now()

    for i, (first_name, gender) in enumerate(people):
        last_name = rng.choice(LAST_NAMES)
        email = f'{first_name.lower()}{EMAIL_MARKER}{i}@example.com'
        phone = f'9{700000000 + i}'
        joined_days_ago = rng.choice(range(0, 90))

        user = CustomUser.objects.create(
            name=f'{first_name} {last_name}',
            email=email,
            number=phone,
            age=rng.randint(18, 30),
            gender=gender,
            state=rng.choice(STATES),
            city=rng.choice(CITIES),
            password=make_password('Student@123'),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        CustomUser.objects.filter(pk=user.pk).update(date_joined=now - timedelta(days=joined_days_ago))


def unseed(apps, schema_editor):
    CustomUser = apps.get_model('myapp', 'CustomUser')
    CustomUser.objects.filter(email__contains=EMAIL_MARKER).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0028_staffmember_transaction_feeinvoice_staffattendance'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
