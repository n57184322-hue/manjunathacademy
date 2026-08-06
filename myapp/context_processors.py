from .models import ChatbotQuestion, ChatbotSettings, DailyUpdateCard, HeroSection, Notification, PWASettings, SiteSettings, SSOSettings


def site_settings(request):
    return {
        'site_settings': SiteSettings.load(),
        'top_notifications': Notification.objects.filter(is_active=True),
        'chatbot_settings': ChatbotSettings.load(),
        'chatbot_questions': ChatbotQuestion.objects.filter(is_active=True),
        'hero': HeroSection.load(),
        'daily_current_card': DailyUpdateCard.load(DailyUpdateCard.CURRENT_AFFAIRS),
        'daily_news_card': DailyUpdateCard.load(DailyUpdateCard.DAILY_NEWS),
        'pwa_settings': PWASettings.load(),
        'sso_settings': SSOSettings.load(),
    }
