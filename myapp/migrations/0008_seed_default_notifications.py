# Generated for seeding the original hardcoded notification ticker items.

from django.db import migrations

DEFAULT_NOTIFICATIONS = [
    {
        'order': 0,
        'text': '📢 SSC CGL 2026 notification released — 4,500+ vacancies',
        'detail': 'New SSC CGL 2026 notification is out — 4,500+ vacancies. Apply on the official SSC portal before the last date. Tap for eligibility, exam dates and the official notification link.',
        'link': '',
    },
    {
        'order': 1,
        'text': "💼 We're hiring: Faculty for Reasoning & GS",
        'detail': "Manjunath Academy is hiring faculty for Reasoning and General Studies at the Lucknow centre. Tap to see the role details and how to apply.",
        'link': '',
    },
    {
        'order': 2,
        'text': '🏫 New offline batch starts 12 Aug — register now',
        'detail': 'New offline batch for Banking & Insurance starts 12 August at the Lucknow centre. Tap to register your name and details directly.',
        'link': '',
    },
    {
        'order': 3,
        'text': '📢 Railway RRB NTPC applications open',
        'detail': 'Railway RRB NTPC application window is open. Tap for the official link, eligibility and important dates.',
        'link': '',
    },
]


def seed_notifications(apps, schema_editor):
    Notification = apps.get_model('myapp', 'Notification')
    if Notification.objects.exists():
        return
    for data in DEFAULT_NOTIFICATIONS:
        Notification.objects.create(**data)


def remove_seeded_notifications(apps, schema_editor):
    Notification = apps.get_model('myapp', 'Notification')
    Notification.objects.filter(text__in=[n['text'] for n in DEFAULT_NOTIFICATIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_notification'),
    ]

    operations = [
        migrations.RunPython(seed_notifications, remove_seeded_notifications),
    ]
