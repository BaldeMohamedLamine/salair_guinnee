from django.urls import path
from . import auth_views

app_name = 'salary_auth'

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('change-password/', auth_views.change_password_view, name='change_password'),
]
