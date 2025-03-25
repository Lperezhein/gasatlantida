from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, LoginView
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', LoginView.as_view(success_url='/'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
