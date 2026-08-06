# Generated to seed 5 dummy ERP staff records for demo purposes.
from django.db import migrations

STAFF = [
    {
        'name': 'Anil Kumar Sharma', 'designation': 'Faculty — Reasoning & General Studies',
        'department': 'teaching', 'email': 'anil.sharma.demo@example.com', 'phone': '9800000001',
        'salary': 45000, 'date_of_joining': '2023-06-01', 'address': 'Hazratganj, Lucknow, Uttar Pradesh',
    },
    {
        'name': 'Priya Mishra', 'designation': 'Content Writer — Current Affairs',
        'department': 'admin', 'email': 'priya.mishra.demo@example.com', 'phone': '9800000002',
        'salary': 28000, 'date_of_joining': '2024-02-15', 'address': 'Gomti Nagar, Lucknow, Uttar Pradesh',
    },
    {
        'name': 'Rohit Verma', 'designation': 'Video Editor',
        'department': 'support', 'email': 'rohit.verma.demo@example.com', 'phone': '9800000003',
        'salary': 26000, 'date_of_joining': '2024-05-10', 'address': 'Indira Nagar, Lucknow, Uttar Pradesh',
    },
    {
        'name': 'Sneha Tiwari', 'designation': 'Telecaller — Admissions',
        'department': 'support', 'email': 'sneha.tiwari.demo@example.com', 'phone': '9800000004',
        'salary': 22000, 'date_of_joining': '2024-08-20', 'address': 'Aliganj, Lucknow, Uttar Pradesh',
    },
    {
        'name': 'Vikram Singh', 'designation': 'Academy Manager',
        'department': 'management', 'email': 'vikram.singh.demo@example.com', 'phone': '9800000005',
        'salary': 60000, 'date_of_joining': '2022-11-01', 'address': 'Hazratganj, Lucknow, Uttar Pradesh',
    },
]


def seed(apps, schema_editor):
    StaffMember = apps.get_model('myapp', 'StaffMember')

    if StaffMember.objects.filter(email__in=[s['email'] for s in STAFF]).exists():
        return

    for data in STAFF:
        StaffMember.objects.create(is_active=True, **data)


def unseed(apps, schema_editor):
    StaffMember = apps.get_model('myapp', 'StaffMember')
    StaffMember.objects.filter(email__in=[s['email'] for s in STAFF]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_seed_dummy_signups'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
