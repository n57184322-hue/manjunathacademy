# Generated to seed dummy Test Series, Video Course and E-Library entries for demo purposes.

from django.db import migrations

TEST_SERIES = [
    {'name': 'SSC CGL Tier 1 Mock Test Series', 'category': 'SSC', 'test_type': 'mock_test', 'original_price': 499, 'current_price': 249, 'about': 'Full-length mock tests matching the latest SSC CGL Tier 1 pattern.'},
    {'name': 'Railway RRB NTPC Practice Sets', 'category': 'Railway', 'test_type': 'practice_test', 'original_price': 399, 'current_price': 199, 'about': 'Topic-wise practice sets for Railway RRB NTPC preparation.'},
    {'name': 'Banking Reasoning Sectional Tests', 'category': 'Banking & Insurance', 'test_type': 'sectional_test', 'original_price': 299, 'current_price': 149, 'about': 'Sectional tests focused on Reasoning for Bank PO and Clerk exams.'},
    {'name': 'CBSE Class 10 Sample Papers', 'category': 'CBSE', 'test_type': 'sample_papers', 'original_price': 199, 'current_price': 0, 'about': 'Board-pattern sample papers for CBSE Class 10 with marking schemes.'},
    {'name': 'NEET Previous Year Papers (2016-2025)', 'category': 'NEET', 'test_type': 'previous_year_paper', 'original_price': 349, 'current_price': 199, 'about': 'Ten years of solved NEET previous year question papers.'},
]

VIDEO_COURSES = [
    {'name': 'Quantitative Aptitude Masterclass', 'category': 'SSC', 'original_price': 999, 'current_price': 499, 'about': 'Shortcut techniques and 120 solved examples for SSC & Banking exams.'},
    {'name': 'Reasoning: Puzzles & Seating Arrangement', 'category': 'Banking & Insurance', 'original_price': 899, 'current_price': 399, 'about': 'Every puzzle type asked in the last 5 years, solved step by step.'},
    {'name': 'NEET Biology: Human Physiology', 'category': 'NEET', 'original_price': 1299, 'current_price': 699, 'about': 'NCERT-mapped video lessons with diagram-based revision notes.'},
    {'name': 'JEE Physics: Mechanics Foundation', 'category': 'JEE', 'original_price': 1499, 'current_price': 799, 'about': 'Concept-first video course covering kinematics to rotational motion.'},
    {'name': 'Railway General Awareness Crash Course', 'category': 'Railway', 'original_price': 599, 'current_price': 299, 'about': 'High-yield current affairs and static GK video lessons for Railway exams.'},
]

ELIBRARY = [
    {'name': 'SSC CGL 10 Years Solved Papers (E-Book)', 'category': 'SSC', 'original_price': 249, 'current_price': 99, 'about': 'Digital compilation of the last 10 years of SSC CGL solved papers.'},
    {'name': 'CBSE Class 12 Physics Notes', 'category': 'CBSE', 'original_price': 199, 'current_price': 0, 'about': 'Chapter-wise revision notes mapped to the CBSE Class 12 syllabus.'},
    {'name': 'Banking Awareness Digest 2026', 'category': 'Banking & Insurance', 'original_price': 149, 'current_price': 79, 'about': 'Monthly banking and financial awareness digest for exam preparation.'},
    {'name': 'NEET Biology NCERT Line-by-Line Notes', 'category': 'NEET', 'original_price': 299, 'current_price': 149, 'about': 'Detailed NCERT-based notes covering every line likely to be tested.'},
    {'name': 'ICSE Class 10 Sample Question Bank', 'category': 'ICSE', 'original_price': 199, 'current_price': 99, 'about': 'A curated question bank aligned with the ICSE Class 10 board pattern.'},
]


def seed_courses(apps, schema_editor):
    Course = apps.get_model('myapp', 'Course')
    Category = apps.get_model('myapp', 'Category')

    if Course.objects.exists():
        return

    def create_all(items, course_type):
        for i, data in enumerate(items):
            category = Category.objects.filter(name=data['category']).first()
            Course.objects.create(
                course_type=course_type,
                category=category,
                name=data['name'],
                test_type=data.get('test_type', ''),
                original_price=data['original_price'],
                current_price=data['current_price'],
                about=data['about'],
                order=i,
            )

    create_all(TEST_SERIES, 'test_series')
    create_all(VIDEO_COURSES, 'video_course')
    create_all(ELIBRARY, 'elibrary')


def remove_seeded_courses(apps, schema_editor):
    Course = apps.get_model('myapp', 'Course')
    names = [c['name'] for c in TEST_SERIES + VIDEO_COURSES + ELIBRARY]
    Course.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_course_test_type'),
    ]

    operations = [
        migrations.RunPython(seed_courses, remove_seeded_courses),
    ]
