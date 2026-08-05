# Generated to seed a starting set of course categories.

from django.db import migrations

DEFAULT_CATEGORIES = [
    {'order': 0, 'name': 'CBSE', 'icon': '📘'},
    {'order': 1, 'name': 'ICSE', 'icon': '📗'},
    {'order': 2, 'name': 'UP Board', 'icon': '📙'},
    {'order': 3, 'name': 'SSC', 'icon': '🏛'},
    {'order': 4, 'name': 'Railway', 'icon': '🚆'},
    {'order': 5, 'name': 'Banking & Insurance', 'icon': '🏦'},
    {'order': 6, 'name': 'NEET', 'icon': '🩺'},
    {'order': 7, 'name': 'JEE', 'icon': '⚙️'},
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    if Category.objects.exists():
        return
    for data in DEFAULT_CATEGORIES:
        Category.objects.create(**data)


def remove_seeded_categories(apps, schema_editor):
    Category = apps.get_model('myapp', 'Category')
    Category.objects.filter(name__in=[c['name'] for c in DEFAULT_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_category_course'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_seeded_categories),
    ]
