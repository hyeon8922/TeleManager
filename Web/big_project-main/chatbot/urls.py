from django.urls import path, reverse, reverse_lazy
from . import views
from .models import *
from django.shortcuts import render


app_name = 'chatbot'

def index(request):
    # app_name: URL 패턴을 정의할 때 설정한 app_name
    # 'client:index': app_name과 패턴 이름을 조합한 것
    url = reverse('chatbot:index') # 
    return render(request, 'index.html', {'index_url': url})

urlpatterns = [
    path('', views.chat, name='chat'),
    path('index.html', index, name='index'),
    path('test/', views.test, name='test'),

]

