# Generated to seed dummy Store products, Career jobs, Test Series questions,
# and placeholder banner images for demo/launch purposes.
import textwrap
from io import BytesIO

from django.db import migrations
from django.db.models import Q

PALETTE = ['#F97316', '#0EA5E9', '#14B8A6', '#8B5CF6', '#EF4444', '#22C55E', '#EAB308', '#EC4899', '#6366F1', '#0D9488']

PRODUCTS = [
    {'name': 'SSC CGL Complete Notes Set', 'category': 'SSC', 'original_price': 599, 'current_price': 499, 'stock': 120, 'description': 'Printed, spiral-bound notes covering the full SSC CGL syllabus.'},
    {'name': 'Banking Reasoning Guidebook', 'category': 'Banking & Insurance', 'original_price': 399, 'current_price': 349, 'stock': 90, 'description': '320 pages, 1,000+ practice questions with solutions.'},
    {'name': 'Academy T-Shirt', 'category': '', 'original_price': 499, 'current_price': 399, 'stock': 200, 'description': 'Cotton, unisex sizes S–XXL. Wear it to the offline centre.'},
    {'name': 'NEET Biology Flashcard Set', 'category': 'NEET', 'original_price': 349, 'current_price': 299, 'stock': 75, 'description': '200 laminated flashcards covering NCERT Biology, chapter-wise.'},
    {'name': 'Railway GK Pocket Book', 'category': 'Railway', 'original_price': 199, 'current_price': 149, 'stock': 150, 'description': 'Compact static GK reference for last-minute Railway exam revision.'},
]

JOBS = [
    {'title': 'Faculty — Reasoning & General Studies', 'location': 'Lucknow centre', 'job_type': 'full_time', 'experience_required': '3+ years teaching experience', 'description': 'Teach Reasoning and General Studies to competitive exam aspirants across batches.'},
    {'title': 'Content Writer — Current Affairs', 'location': 'Remote', 'job_type': 'remote', 'experience_required': 'Strong writing in English & Hindi', 'description': 'Research and write daily current affairs content for the academy platform.'},
    {'title': 'Video Editor', 'location': 'Lucknow centre', 'job_type': 'full_time', 'experience_required': 'Experience editing lecture videos', 'description': 'Edit recorded lectures into polished, chapter-wise video course content.'},
    {'title': 'Telecaller — Admissions', 'location': 'Lucknow centre', 'job_type': 'full_time', 'experience_required': 'Fluent Hindi & English', 'description': 'Handle inbound admission enquiries and follow up with prospective students.'},
    {'title': 'Social Media Intern', 'location': 'Remote', 'job_type': 'internship', 'experience_required': 'Fresher — good with Instagram & YouTube', 'description': 'Assist in planning and posting daily social media content for the academy.'},
]

QUESTIONS = [
    {'question_type': 'single', 'text': 'Which of the following is a prime number?', 'option_a': '15', 'option_b': '21', 'option_c': '17', 'option_d': '27', 'correct_answer': 'C'},
    {'question_type': 'multiple', 'text': 'Which of the following are even numbers?', 'option_a': '4', 'option_b': '7', 'option_c': '10', 'option_d': '13', 'correct_answer': 'A,C'},
    {'question_type': 'numeric', 'text': 'What is 15% of 200?', 'correct_answer': '30'},
    {'question_type': 'true_false', 'text': 'The sum of angles in a triangle is 180 degrees.', 'correct_answer': 'True'},
    {'question_type': 'fill_blank', 'text': 'The capital of India is ______.', 'correct_answer': 'New Delhi'},
    {'question_type': 'single', 'text': 'Choose the correctly spelled word.', 'option_a': 'Recieve', 'option_b': 'Receive', 'option_c': 'Receeve', 'option_d': 'Receve', 'correct_answer': 'B'},
    {'question_type': 'multiple', 'text': 'Which of these letters are vowels?', 'option_a': 'A', 'option_b': 'B', 'option_c': 'E', 'option_d': 'F', 'correct_answer': 'A,C'},
    {'question_type': 'numeric', 'text': 'If a train travels 60 km in 1.5 hours, what is its speed in km/h?', 'correct_answer': '40'},
    {'question_type': 'true_false', 'text': 'Water boils at 100 degrees Celsius at sea level.', 'correct_answer': 'True'},
    {'question_type': 'fill_blank', 'text': 'The national bird of India is the ______.', 'correct_answer': 'Peacock'},
]


def _placeholder_image(text, width, height, color):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=20)[:3]
    line_height = 28
    total_h = line_height * len(lines)
    y = (height - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) / 2, y), line, font=font, fill='#FFFFFF')
        y += line_height

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def seed(apps, schema_editor):
    from django.core.files.base import ContentFile

    Course = apps.get_model('myapp', 'Course')
    Category = apps.get_model('myapp', 'Category')
    Product = apps.get_model('myapp', 'Product')
    JobPosting = apps.get_model('myapp', 'JobPosting')
    Question = apps.get_model('myapp', 'Question')

    if not Product.objects.exists():
        for i, data in enumerate(PRODUCTS):
            category = Category.objects.filter(name=data['category']).first() if data['category'] else None
            product = Product.objects.create(
                category=category,
                name=data['name'],
                description=data['description'],
                original_price=data['original_price'],
                current_price=data['current_price'],
                stock=data['stock'],
                order=i,
            )
            image_bytes = _placeholder_image(data['name'], 400, 400, PALETTE[i % len(PALETTE)])
            product.image.save(f'product_{product.pk}.png', ContentFile(image_bytes), save=True)

    if not JobPosting.objects.exists():
        for i, data in enumerate(JOBS):
            JobPosting.objects.create(
                title=data['title'],
                location=data['location'],
                job_type=data['job_type'],
                experience_required=data['experience_required'],
                description=data['description'],
                order=i,
            )

    for course in Course.objects.filter(course_type='test_series'):
        if course.questions.exists():
            continue
        for i, q in enumerate(QUESTIONS):
            Question.objects.create(
                course=course,
                question_type=q['question_type'],
                text=q['text'],
                option_a=q.get('option_a', ''),
                option_b=q.get('option_b', ''),
                option_c=q.get('option_c', ''),
                option_d=q.get('option_d', ''),
                correct_answer=q['correct_answer'],
                marks=1,
                order=i,
            )

    needs_thumb = Course.objects.filter(Q(thumbnail='') | Q(thumbnail__isnull=True)).order_by('course_type', 'id')
    for i, course in enumerate(needs_thumb):
        image_bytes = _placeholder_image(course.name, 400, 240, PALETTE[i % len(PALETTE)])
        course.thumbnail.save(f'course_{course.pk}.png', ContentFile(image_bytes), save=True)


def unseed(apps, schema_editor):
    Product = apps.get_model('myapp', 'Product')
    JobPosting = apps.get_model('myapp', 'JobPosting')
    Product.objects.filter(name__in=[p['name'] for p in PRODUCTS]).delete()
    JobPosting.objects.filter(title__in=[j['title'] for j in JOBS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_jobposting_razorpaysettings_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
