from .models import ChatbotQuestion, ChatbotSettings, HeroSection, Notification, SiteSettings


def site_settings(request):
    return {
        'site_settings': SiteSettings.load(),
        'top_notifications': Notification.objects.filter(is_active=True),
        'chatbot_settings': ChatbotSettings.load(),
        'chatbot_questions': ChatbotQuestion.objects.filter(is_active=True),
        'hero': HeroSection.load(),
    }
