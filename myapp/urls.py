from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/edit/', views.account_edit, name='account_edit'),
    path('account/password/', views.AccountPasswordChangeView.as_view(), name='account_password'),
    path('account/purchases/', views.account_purchases, name='account_purchases'),
    path('panel/', views.panel_signups, name='panel_signups'),
    path('panel/signups/add/', views.panel_signup_add, name='panel_signup_add'),
    path('panel/customization/navbar/', views.panel_navbar_customization, name='panel_navbar_customization'),
    path('panel/customization/hero/', views.panel_hero_section, name='panel_hero_section'),
    path('panel/customization/banner/', views.panel_banner_list, name='panel_banner_list'),
    path('panel/customization/banner/add/', views.panel_banner_add, name='panel_banner_add'),
    path('panel/customization/banner/<int:pk>/edit/', views.panel_banner_edit, name='panel_banner_edit'),
    path('panel/customization/banner/<int:pk>/delete/', views.panel_banner_delete, name='panel_banner_delete'),
    path('panel/customization/notifications/', views.panel_notification_list, name='panel_notification_list'),
    path('panel/customization/notifications/add/', views.panel_notification_add, name='panel_notification_add'),
    path('panel/customization/notifications/<int:pk>/edit/', views.panel_notification_edit, name='panel_notification_edit'),
    path('panel/customization/notifications/<int:pk>/delete/', views.panel_notification_delete, name='panel_notification_delete'),
    path('panel/chatbot/', views.panel_chatbot_list, name='panel_chatbot_list'),
    path('panel/chatbot/questions/add/', views.panel_chatbot_question_add, name='panel_chatbot_question_add'),
    path('panel/chatbot/questions/<int:pk>/edit/', views.panel_chatbot_question_edit, name='panel_chatbot_question_edit'),
    path('panel/chatbot/questions/<int:pk>/delete/', views.panel_chatbot_question_delete, name='panel_chatbot_question_delete'),
]
