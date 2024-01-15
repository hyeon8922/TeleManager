from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from account.models import Profile
from client.models import Client
from django.shortcuts import get_object_or_404


class ChatBot(models.Model):
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_chatbots')     # 운영자, 운영자가 사라지면 연관된 챗봇도 사라짐
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_chatbots')   # 고객, 고객이 사라지면 연관된 챗봇도 사라짐
    
    outbound_purpose = models.TextField(default='Default')   # 아웃바운드 목적
    outbound_message = models.TextField()   # 아웃바운드 문구
    
    outbound_end = models.TextField() # 아웃바운드 끝났는지 여부
    
    messages = models.JSONField()    # 챗봇 내역을 저장하는 필드
    
    created_at = models.DateTimeField(auto_now_add=True)   # 만들어진 날짜 저장 필드
    updated_at = models.DateTimeField(auto_now=True)   # 수정된 날짜 저장 필드



    def get_chatbot(owner, client):   # 운영자와 고객 정보를 통해, 이전에 챗봇이 있을 경우 가져오는 코드입니다. 
                                      # 추후에 return된 chatbot의 messages 필드에 접근하여 상담내용을 가져오면 됩니다.
        chatbot = get_object_or_404(ChatBot, owner=owner, client=client)
        return chatbot


     # 챗봇에 메시지 추가하는 메서드    
     # 챗봇 모델을 Create 통해 생성해서 add_message를 통해 messages 필드에 내역 추가
     # 아웃바운드 나가기 전 질문 생성 후, 호출해서 문구 넣어 주고, 고객이 답장오면 다시 호출해서 여기에 넣어줘야함
     # role 같은 경우, owner-client 로 해서 추후에 프론트에서 구분하여 출력하기 위해 넣었습니다.
     
    def add_message(self, role, content):  
        
        self.messages.append({
            "role": role,
            "content": content
        })
        self.save()


    def __str__(self):   # 챗봇을 사용하고 있는 운영자, 고객 확인용 함수입니다.
        return f"ChatBot between {self.owner.username} and {self.client.name}"
    # 예시 test11,, 민성    
    


# chatbot_instance = ChatBot.objects.get(id=1)  # 예시로 id=1인 챗봇 인스턴스를 가져옴
# chatbot_instance.add_message("operator", "아웃바운드 문구")
# chatbot_instance.add_message("customer", "유저의 답장")
