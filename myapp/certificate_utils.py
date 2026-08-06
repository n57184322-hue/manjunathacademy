import io
import math

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

ORANGE = '#F97316'
ORANGE_DEEP = '#EA580C'
GOLD = '#FBBF24'
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


def _draw_frame(draw):
    draw.rectangle([26, 26, WIDTH - 26, HEIGHT - 26], outline=INK, width=4)
    draw.rectangle([42, 42, WIDTH - 42, HEIGHT - 42], outline=GOLD, width=2)
    draw.rectangle([54, 54, WIDTH - 54, HEIGHT - 54], outline=ORANGE, width=3)

    corner = 42
    for cx, cy, dx, dy in [(54, 54, 1, 1), (WIDTH - 54, 54, -1, 1), (54, HEIGHT - 54, 1, -1), (WIDTH - 54, HEIGHT - 54, -1, -1)]:
        draw.line([(cx, cy + dy * corner), (cx, cy), (cx + dx * corner, cy)], fill=ORANGE_DEEP, width=5)
        d = 12
        draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], fill=GOLD)


def _draw_watermark(img):
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    cx, cy = WIDTH / 2, HEIGHT / 2 + 20
    odraw.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], outline=(249, 115, 22, 35), width=10)
    odraw.ellipse([cx - 270, cy - 270, cx + 270, cy + 270], outline=(249, 115, 22, 22), width=4)
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')


def _paste_logo(img, site, top_y, target_h=104):
    if site.logo_type != site.LOGO_IMAGE or not site.logo_image:
        return top_y
    try:
        logo = Image.open(site.logo_image.path).convert('RGBA')
    except Exception:
        return top_y

    ratio = target_h / logo.height
    target_w = max(1, int(logo.width * ratio))
    logo = logo.resize((target_w, target_h), Image.LANCZOS)
    x = int((WIDTH - target_w) / 2)
    img.paste(logo, (x, top_y), logo)
    return top_y + target_h + 26


def _draw_seal(draw):
    seal_cx, seal_cy, seal_r = WIDTH - 220, HEIGHT - 232, 88

    draw.polygon(
        [(seal_cx - 38, seal_cy + 34), (seal_cx - 12, seal_cy + 132), (seal_cx - 52, seal_cy + 112)],
        fill=ORANGE_DEEP,
    )
    draw.polygon(
        [(seal_cx + 38, seal_cy + 34), (seal_cx + 12, seal_cy + 132), (seal_cx + 52, seal_cy + 112)],
        fill=ORANGE_DEEP,
    )

    draw.ellipse([seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r], fill=ORANGE_DEEP)
    draw.ellipse(
        [seal_cx - seal_r + 10, seal_cy - seal_r + 10, seal_cx + seal_r - 10, seal_cy + seal_r - 10],
        outline=CREAM, width=4,
    )
    draw.ellipse(
        [seal_cx - seal_r + 20, seal_cy - seal_r + 20, seal_cx + seal_r - 20, seal_cy + seal_r - 20],
        fill=ORANGE,
    )
    draw.polygon(_star_points(seal_cx, seal_cy, seal_r - 46, seal_r - 78), fill='white')


def generate_certificate_image(certificate):
    """Renders a fixed certificate layout onto a PNG and returns it as a ContentFile."""
    from .models import SiteSettings

    site = SiteSettings.load()
    academy_name = (site.copyright_text or 'Manjunath Academy').strip() or 'Manjunath Academy'

    img = Image.new('RGB', (WIDTH, HEIGHT), CREAM)
    img = _draw_watermark(img)

    y = 90
    has_logo = site.logo_type == SiteSettings.LOGO_IMAGE and bool(site.logo_image)
    if has_logo:
        y = _paste_logo(img, site, y)
    else:
        y = 160

    draw = ImageDraw.Draw(img)
    _draw_frame(draw)

    _centered_text(draw, y, academy_name.upper(), _font(50), INK, stroke_width=1)
    y += 96

    draw.line([(WIDTH / 2 - 130, y), (WIDTH / 2 + 130, y)], fill=ORANGE, width=3)
    y += 50

    type_label = ' '.join(certificate.get_certificate_type_display().upper())
    _centered_text(draw, y, type_label, _font(40), ORANGE_DEEP, stroke_width=1)
    y += 100

    _centered_text(draw, y, 'This certificate is proudly presented to', _font(25), MUTED)
    y += 82

    name_width = _centered_text(draw, y, certificate.recipient_name.upper(), _font(68), INK, stroke_width=2)
    y += 122

    draw.line([(WIDTH / 2 - name_width / 2 - 30, y), (WIDTH / 2 + name_width / 2 + 30, y)], fill=ORANGE, width=2)
    y += 66

    body_text = f'for successfully completing {certificate.course_name}'
    if certificate.description:
        body_text += f'. {certificate.description}'
    body_font = _font(27)
    for line in _wrap_text(draw, body_text, body_font, WIDTH - 420):
        _centered_text(draw, y, line, body_font, INK)
        y += 44

    footer_y = HEIGHT - 190
    footer_font = _font(22)
    draw.text((140, footer_y), f'Date: {certificate.issue_date.strftime("%d %B %Y")}', font=footer_font, fill=INK)
    draw.text((140, footer_y + 34), f'Certificate No: {certificate.certificate_number}', font=footer_font, fill=INK)

    sig_label = f'Director, {academy_name}'
    sig_font = _font(24)
    sig_width = draw.textlength(sig_label, font=sig_font)
    draw.line([(WIDTH / 2 - 140, footer_y - 10), (WIDTH / 2 + 140, footer_y - 10)], fill=INK, width=2)
    draw.text((WIDTH / 2 - sig_width / 2, footer_y), sig_label, font=sig_font, fill=INK)

    _draw_seal(draw)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())
