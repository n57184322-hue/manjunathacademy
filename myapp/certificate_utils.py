import io
import math

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

ORANGE = '#F97316'
ORANGE_DEEP = '#EA580C'
CREAM = '#FFF7F1'
INK = '#101012'
MUTED = '#6B7280'

WIDTH, HEIGHT = 1600, 1131


def _font(size):
    return ImageFont.load_default(size=size)


def _centered_text(draw, y, text, font, fill, stroke_width=0):
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bbox[2] - bbox[0]
    x = (WIDTH - width) / 2 - bbox[0]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width)
    return width


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        trial = f'{current} {word}'.strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _star_points(cx, cy, outer_r, inner_r, points=5):
    coords = []
    angle = -math.pi / 2
    step = math.pi / points
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        angle += step
    return coords


def generate_certificate_image(certificate):
    """Renders a fixed certificate layout onto a PNG and returns it as a ContentFile."""
    from .models import SiteSettings

    site = SiteSettings.load()
    academy_name = (site.copyright_text or 'Manjunath Academy').strip() or 'Manjunath Academy'

    img = Image.new('RGB', (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(img)

    draw.rectangle([28, 28, WIDTH - 28, HEIGHT - 28], outline=INK, width=4)
    draw.rectangle([50, 50, WIDTH - 50, HEIGHT - 50], outline=ORANGE, width=3)

    corner = 46
    for cx, cy, dx, dy in [(50, 50, 1, 1), (WIDTH - 50, 50, -1, 1), (50, HEIGHT - 50, 1, -1), (WIDTH - 50, HEIGHT - 50, -1, -1)]:
        draw.line([(cx, cy + dy * corner), (cx, cy), (cx + dx * corner, cy)], fill=ORANGE_DEEP, width=6)

    y = 160
    _centered_text(draw, y, academy_name.upper(), _font(52), INK, stroke_width=1)
    y += 100

    draw.line([(WIDTH / 2 - 130, y), (WIDTH / 2 + 130, y)], fill=ORANGE, width=3)
    y += 54

    type_label = ' '.join(certificate.get_certificate_type_display().upper())
    _centered_text(draw, y, type_label, _font(42), ORANGE_DEEP, stroke_width=1)
    y += 110

    _centered_text(draw, y, 'This certificate is proudly presented to', _font(26), MUTED)
    y += 90

    name_width = _centered_text(draw, y, certificate.recipient_name.upper(), _font(72), INK, stroke_width=2)
    y += 130

    draw.line([(WIDTH / 2 - name_width / 2 - 30, y), (WIDTH / 2 + name_width / 2 + 30, y)], fill=ORANGE, width=2)
    y += 70

    body_text = f'for successfully completing {certificate.course_name}'
    if certificate.description:
        body_text += f'. {certificate.description}'
    body_font = _font(28)
    for line in _wrap_text(draw, body_text, body_font, WIDTH - 420):
        _centered_text(draw, y, line, body_font, INK)
        y += 46

    footer_y = HEIGHT - 190
    footer_font = _font(22)
    draw.text((140, footer_y), f'Date: {certificate.issue_date.strftime("%d %B %Y")}', font=footer_font, fill=INK)
    draw.text((140, footer_y + 34), f'Certificate No: {certificate.certificate_number}', font=footer_font, fill=INK)

    sig_label = f'Director, {academy_name}'
    sig_font = _font(24)
    sig_width = draw.textlength(sig_label, font=sig_font)
    draw.line([(WIDTH / 2 - 140, footer_y - 10), (WIDTH / 2 + 140, footer_y - 10)], fill=INK, width=2)
    draw.text((WIDTH / 2 - sig_width / 2, footer_y), sig_label, font=sig_font, fill=INK)

    seal_cx, seal_cy, seal_r = WIDTH - 220, HEIGHT - 190, 85
    draw.ellipse([seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r], outline=ORANGE_DEEP, width=6)
    draw.ellipse(
        [seal_cx - seal_r + 14, seal_cy - seal_r + 14, seal_cx + seal_r - 14, seal_cy + seal_r - 14],
        fill=ORANGE,
    )
    draw.polygon(_star_points(seal_cx, seal_cy, seal_r - 42, seal_r - 72), fill='white')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())
