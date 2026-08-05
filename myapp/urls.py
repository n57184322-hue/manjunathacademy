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
]
