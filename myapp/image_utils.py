import io

from django.core.files.base import ContentFile
from PIL import Image

MAX_DIMENSION = 1600
JPEG_QUALITY = 82


def optimize_image_field(field_file, max_dimension=MAX_DIMENSION, quality=JPEG_QUALITY):
    """Resizes/compresses a newly-uploaded image in place before it hits storage.

    No-ops for empty fields or files that are already committed to storage
    (i.e. unchanged existing images), so editing unrelated fields never
    re-compresses an image that was already optimized.
    """
    if not field_file or getattr(field_file, '_committed', True):
        return
    try:
        field_file.seek(0)
        img = Image.open(field_file)
        img.load()
        img_format = (img.format or 'JPEG').upper()

        width, height = img.size
        if max(width, height) > max_dimension:
            ratio = max_dimension / float(max(width, height))
            new_size = (max(1, int(width * ratio)), max(1, int(height * ratio)))
            img = img.resize(new_size, Image.LANCZOS)

        buffer = io.BytesIO()
        if img_format in ('JPEG', 'JPG'):
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
            new_name = field_file.name.rsplit('.', 1)[0] + '.jpg'
        elif img_format == 'PNG':
            img.save(buffer, format='PNG', optimize=True)
            new_name = field_file.name
        elif img_format == 'WEBP':
            img.save(buffer, format='WEBP', quality=quality, method=6)
            new_name = field_file.name
        else:
            return

        buffer.seek(0)
        field_file.save(new_name, ContentFile(buffer.read()), save=False)
    except Exception:
        pass
