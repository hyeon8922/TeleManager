from django.urls import path, reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from . import views
from .models import *
from .views import ClientListView, text_processing, message_results, sendAllMessages
from django.shortcuts import render


app_name = 'client'

def index(request):
    return render(request, 'index.html')

def audio(request):
    return render(request, 'client/audio.html')

urlpatterns = [
    path('', ClientListView.as_view(), name = 'list'),
    path('upload/',views.upload_excel, name='upload'),
    path('edit/<int:client_id>/', views.edit_client, name='edit_client'),
    path('delete/<int:client_id>/', views.delete_client, name='delete_client'),
    path('delete_selected/', views.DeleteSelectedClientsView.as_view(), name='delete_selected'),
    path('selected_items/', views.selected_items, name='selected_items'),
    path('start_tm/',views.start_tm, name='start_tm'),
    path('error/', views.error_page, name='error'),
 
    path('delete_selected/', views.DeleteSelectedClientsView.as_view(), name='delete_selected'),
    # path('audio/', audio, name='audio'),
    # path('save_audio/', views.save_audio, name='save_audio'),
    path('start_tm/text_processing/', text_processing, name='text_processing'), # 텍스트 감정분류(아웃바운드 챗봇)
    path('start_tm/message_results/', message_results, name='message_results'), # 챗봇 채팅 내역 전달부분
    path('start_tm/sendAllMessages/', sendAllMessages, name='sendAllMessages'), # 챗봇 채팅 내역 전달부분
]


