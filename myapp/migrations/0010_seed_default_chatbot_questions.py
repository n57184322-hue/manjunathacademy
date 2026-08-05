# Generated for seeding the original hardcoded chatbot quick-questions.

from django.db import migrations

DEFAULT_QUESTIONS = [
    {
        'order': 0,
        'question': 'What courses do you offer?',
        'answer': 'We offer SSC & Railways, Banking & Insurance, NEET & JEE foundation, plus CDS and AFCAT preparation — most content is free.',
    },
    {
        'order': 1,
        'question': 'How do I join for free?',
        'answer': 'Click "Join for Free" in the menu and create your account in under a minute — no fee required.',
    },
    {
        'order': 2,
        'question': 'Do you have test series?',
        'answer': 'Yes — check the Test Series section for Defence, SSC, Railway, CUET and Civil Services, with real exam timing and All-India rank.',
    },
    {
        'order': 3,
        'question': 'Where is the offline centre?',
        'answer': 'Our offline centre is in Hazratganj, Lucknow, Uttar Pradesh. Classes run Mon–Sat, 8 am – 8 pm.',
    },
    {
        'order': 4,
        'question': 'How can I contact support?',
        'answer': 'Call +91 522 000 0000 or email hello@manjunathacademy.in — our team typically replies the same day.',
    },
]


def seed_questions(apps, schema_editor):
    ChatbotQuestion = apps.get_model('myapp', 'ChatbotQuestion')
    if ChatbotQuestion.objects.exists():
        return
    for data in DEFAULT_QUESTIONS:
        ChatbotQuestion.objects.create(**data)


def remove_seeded_questions(apps, schema_editor):
    ChatbotQuestion = apps.get_model('myapp', 'ChatbotQuestion')
    ChatbotQuestion.objects.filter(question__in=[q['question'] for q in DEFAULT_QUESTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_chatbotquestion_chatbotsettings'),
    ]

    operations = [
        migrations.RunPython(seed_questions, remove_seeded_questions),
    ]
