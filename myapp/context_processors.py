from .models import Notification, SiteSettings


def site_settings(request):
    return {
        'site_settings': SiteSettings.load(),
        'top_notifications': Notification.objects.filter(is_active=True),
    }
