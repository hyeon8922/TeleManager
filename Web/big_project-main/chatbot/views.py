from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import os
from django.conf import settings

ALLOW_URL_LIST = settings.ALLOW_URL_LIST
FILE_COUNT_LIMIT = settings.FILE_COUNT_LIMIT         
FILE_SIZE_LIMIT_CLIENT = settings.FILE_SIZE_LIMIT_CLIENT 
WHITE_LIST_CLIENT = settings.WHITE_LIST_CLIENT


def chat(request):
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    return render(request, 'chatbot/chat.html')

def test(request):
    
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    return render(request, 'chatbot/test.html')
