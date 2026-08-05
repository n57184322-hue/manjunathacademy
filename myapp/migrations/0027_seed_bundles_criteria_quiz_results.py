# Generated to seed dummy Bundles, Eligibility Criteria, Quiz questions and
# Academic Excellence result photos so these new sections aren't empty on first load.
import urllib.request
from io import BytesIO

from django.db import migrations

RESULT_PHOTOS = [
    ('1519345182560-3f2917c472ef', 'Health'),
    ('1519085360753-af0119f7cbe7', 'Management'),
    ('1571260899304-425eee4c7efc', 'Pre-University'),
    ('1580489944761-15a19d654956', 'Agriculture'),
    ('1544005313-94ddf0286df2', 'KLE School'),
    ('1508214751196-bcfd4ca60f91', 'Law College'),
    ('1573497019940-1c28c88b4f3e', 'Collegiate'),
    ('1531123897727-8f129e1688ce', 'Foundation'),
]

BUNDLES = [
    {
        'name': 'SSC & Railway Combo', 'icon': '🏛', 'badge_label': 'All Subjects Included',
        'description': 'Complete test series, video lessons and e-notes for SSC and Railway exams.',
        'original_price': 1499, 'current_price': 799,
        'courses': ['SSC CGL Tier 1 Mock Test Series', 'Railway RRB NTPC Practice Sets', 'Quantitative Aptitude Masterclass', 'SSC CGL 10 Years Solved Papers (E-Book)'],
    },
    {
        'name': 'Banking Complete Pack', 'icon': '💰', 'badge_label': 'Reasoning + Awareness',
        'description': 'Sectional tests, video lessons and the monthly banking awareness digest.',
        'original_price': 999, 'current_price': 599,
        'courses': ['Banking Reasoning Sectional Tests', 'Reasoning: Puzzles & Seating Arrangement', 'Banking Awareness Digest 2026'],
    },
    {
        'name': 'NEET Foundation Pack', 'icon': '🧬', 'badge_label': 'Biology Focus',
        'description': 'Previous year papers, video lessons and NCERT-based notes for NEET Biology.',
        'original_price': 1599, 'current_price': 899,
        'courses': ['NEET Previous Year Papers (2016-2025)', 'NEET Biology: Human Physiology', 'NEET Biology NCERT Line-by-Line Notes'],
    },
]

CRITERIA = [
    {'job_name': 'SSC CGL', 'min_education': 'graduate', 'min_age': 18, 'max_age': 32},
    {'job_name': 'Railway RRB NTPC', 'min_education': '12th', 'min_age': 18, 'max_age': 33},
    {'job_name': 'IBPS Bank PO', 'min_education': 'graduate', 'min_age': 20, 'max_age': 30},
    {'job_name': 'NEET', 'min_education': '12th', 'min_age': 17, 'max_age': 25},
    {'job_name': 'Indian Army Agniveer (Male)', 'min_education': '12th', 'min_age': 17, 'max_age': 21, 'min_height_cm': 170, 'allowed_gender': 'male'},
    {'job_name': 'Indian Army Agniveer (Female)', 'min_education': '12th', 'min_age': 17, 'max_age': 21, 'min_height_cm': 152, 'allowed_gender': 'female'},
]

QUIZ_QUESTIONS = [
    {'text': 'Who is known as the Father of the Nation in India?', 'option_a': 'Jawaharlal Nehru', 'option_b': 'Mahatma Gandhi', 'option_c': 'Sardar Patel', 'option_d': 'B.R. Ambedkar', 'correct_option': 'B', 'prize_label': '₹1,000'},
    {'text': 'What is the capital of India?', 'option_a': 'Mumbai', 'option_b': 'Kolkata', 'option_c': 'New Delhi', 'option_d': 'Chennai', 'correct_option': 'C', 'prize_label': '₹2,000'},
    {'text': 'Which planet is known as the Red Planet?', 'option_a': 'Venus', 'option_b': 'Mars', 'option_c': 'Jupiter', 'option_d': 'Saturn', 'correct_option': 'B', 'prize_label': '₹5,000'},
    {'text': 'What is 12 × 8?', 'option_a': '88', 'option_b': '96', 'option_c': '104', 'option_d': '92', 'correct_option': 'B', 'prize_label': '₹10,000'},
    {'text': 'Which river is known as the Ganga of the South?', 'option_a': 'Krishna', 'option_b': 'Cauvery', 'option_c': 'Godavari', 'option_d': 'Narmada', 'correct_option': 'C', 'prize_label': '₹20,000'},
    {'text': 'Who wrote the Indian national anthem?', 'option_a': 'Bankim Chandra', 'option_b': 'Rabindranath Tagore', 'option_c': 'Sarojini Naidu', 'option_d': 'Subhas Chandra Bose', 'correct_option': 'B', 'prize_label': '₹40,000'},
    {'text': 'The Battle of Plassey was fought in which year?', 'option_a': '1757', 'option_b': '1857', 'option_c': '1707', 'option_d': '1657', 'correct_option': 'A', 'prize_label': '₹80,000'},
    {'text': 'Which gas do plants absorb from the atmosphere for photosynthesis?', 'option_a': 'Oxygen', 'option_b': 'Nitrogen', 'option_c': 'Carbon dioxide', 'option_d': 'Hydrogen', 'correct_option': 'C', 'prize_label': '₹1,60,000'},
    {'text': 'Who was the first President of India?', 'option_a': 'Dr. Rajendra Prasad', 'option_b': 'Dr. S. Radhakrishnan', 'option_c': 'Zakir Husain', 'option_d': 'V.V. Giri', 'correct_option': 'A', 'prize_label': '₹3,20,000'},
    {'text': 'What is the square root of 225?', 'option_a': '13', 'option_b': '14', 'option_c': '15', 'option_d': '16', 'correct_option': 'C', 'prize_label': '₹6,40,000'},
]


def _download(photo_id):
    url = f'https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=440&h=560&q=70'
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except Exception:
        return None


def seed(apps, schema_editor):
    from django.core.files.base import ContentFile

    Course = apps.get_model('myapp', 'Course')
    Bundle = apps.get_model('myapp', 'Bundle')
    EligibilityCriteria = apps.get_model('myapp', 'EligibilityCriteria')
    QuizQuestion = apps.get_model('myapp', 'QuizQuestion')
    ResultHighlight = apps.get_model('myapp', 'ResultHighlight')

    if not ResultHighlight.objects.exists():
        for i, (photo_id, caption) in enumerate(RESULT_PHOTOS):
            content = _download(photo_id)
            if not content:
                continue
            result = ResultHighlight.objects.create(caption=caption, order=i)
            result.image.save(f'result_{result.pk}.jpg', ContentFile(content), save=True)

    if not Bundle.objects.exists():
        for i, data in enumerate(BUNDLES):
            bundle = Bundle.objects.create(
                name=data['name'], icon=data['icon'], badge_label=data['badge_label'],
                description=data['description'], original_price=data['original_price'],
                current_price=data['current_price'], order=i,
            )
            courses = Course.objects.filter(name__in=data['courses'])
            bundle.courses.set(courses)

    if not EligibilityCriteria.objects.exists():
        for i, data in enumerate(CRITERIA):
            EligibilityCriteria.objects.create(order=i, **data)

    if not QuizQuestion.objects.exists():
        for i, q in enumerate(QUIZ_QUESTIONS):
            QuizQuestion.objects.create(level=i + 1, **q)


def unseed(apps, schema_editor):
    Bundle = apps.get_model('myapp', 'Bundle')
    EligibilityCriteria = apps.get_model('myapp', 'EligibilityCriteria')
    QuizQuestion = apps.get_model('myapp', 'QuizQuestion')
    ResultHighlight = apps.get_model('myapp', 'ResultHighlight')

    Bundle.objects.filter(name__in=[b['name'] for b in BUNDLES]).delete()
    EligibilityCriteria.objects.filter(job_name__in=[c['job_name'] for c in CRITERIA]).delete()
    QuizQuestion.objects.filter(text__in=[q['text'] for q in QUIZ_QUESTIONS]).delete()
    ResultHighlight.objects.filter(caption__in=[c for _, c in RESULT_PHOTOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0026_eligibilitycriteria_homepagecontent_quizquestion_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
