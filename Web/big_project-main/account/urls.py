from django.urls import path, reverse, reverse_lazy
from . import views
from .models import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import UserPasswordResetView, PasswordChangeView
from .views import CustomLoginView
from .views import ProfileView
app_name = 'account'

def generic(request):
    return render(request, '../templates/generic.html')
 
def elements(request):
    return render(request, '../templates/elements.html')


urlpatterns = [
    path('generic.html', generic, name='generic'),
    path('elements.html', elements, name='elements'),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('agreement/', views.AgreementView.as_view(), name='agreement'),
    path('before/', views.before, name='before'),
    path('profile/', ProfileView.as_view(), name='profile' ),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', views.UserPasswordResetView.as_view(), name="password_reset"),
    path('list/', views.file_list, name='file_list'),  
    path('upload/', views.file_upload, name='file_upload'),
    path('edit/<int:file_id>/', views.edit_file, name='edit_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('delete_selected/', views.DeleteSelectedFilesView.as_view(), name='delete_selected'),
    path('error/', views.error_page, name='error'),
    path('urlerror/', views.urlerror_page, name='urlerror'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)