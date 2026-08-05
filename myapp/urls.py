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
    path('panel/customization/banner/', views.panel_banner_list, name='panel_banner_list'),
    path('panel/customization/banner/add/', views.panel_banner_add, name='panel_banner_add'),
    path('panel/customization/banner/<int:pk>/edit/', views.panel_banner_edit, name='panel_banner_edit'),
    path('panel/customization/banner/<int:pk>/delete/', views.panel_banner_delete, name='panel_banner_delete'),
]
