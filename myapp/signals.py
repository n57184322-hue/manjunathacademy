from django.db.models import ImageField
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .image_utils import optimize_image_field


@receiver(pre_save, dispatch_uid='myapp_optimize_uploaded_images')
def optimize_uploaded_images(sender, instance, **kwargs):
    if sender._meta.app_label != 'myapp':
        return
    for field in sender._meta.get_fields():
        if isinstance(field, ImageField):
            optimize_image_field(getattr(instance, field.name))
