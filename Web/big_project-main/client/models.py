from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
# Create your models here.
 
 
class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)                               # 고객 이름 저장
    location = models.CharField(max_length=140, null=True, blank=True)   # 고객 주소 저장
    number = models.CharField(max_length=20, null=True, blank=True)      # 고객 전화번호 저장
    birth_date = models.CharField(max_length=10, null=True, blank=True)  # YYYY-MM_DD 형식
    tm_date = models.DateTimeField(null=True, blank = True)              # TM 날짜 저장
    age = models.IntegerField(null= True, blank=True)                    # 고객 나이 저장
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)  # (실제 값, 보여지는 값)
    email = models.EmailField(max_length=254, null=True, blank=True)     # 고객 이메일 저장
    info = models.CharField(max_length=1000, null=True, blank=True)      # 고객의 정보들
 
    def __str__(self):
        return self.name
 
 
 
# class Marketing(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     location = models.CharField(max_length=255)
 
 
   
 
# class AudioFile(models.Model):
#   owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'owner_audiofile')    
#   client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name = 'client_audiofile')  
#   title = models.CharField(max_length=255)
#   audio_file = models.FileField(upload_to='audio_files/')  # 파일 경로
#   created_at = models.DateTimeField(auto_now_add = True)   # 만들어진 날짜 저장 필드
#   updated_at = models.DateTimeField(auto_now = True)       # 수정된 날짜 저장 필드
 
#   messages = models.JSONField(default = list)    # 챗봇 내역을 저장하는 필드
 
#   def __str__(self):
#       return self.title
 
 
#   def generate_audio_filename(self, owner, client):
 
#       owner_username = owner.username
#       client_name = client.name
#       filename = f"{owner_username}_{client_name}.mp3"
#       return slugify(filename)
   
#   def save(self, *args, **kwargs):
#       if not self.title:
#           self.title = self.generate_audio_filename(self.owner, self.client)
 
#       super().save(*args, **kwargs)
 
 
#   def get_audiofile(owner, client):    # 가져오기
#       audiofile = get_object_or_404(AudioFile, owner=owner, client=client)
#       return audiofile
 
 
#   def add_audio_message(self, role, path):
 
#       new_message = {
#             'role': role,  # onwer 인지 client 인지
#             'path': path,  # 새로운 파일 경로
#             'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 추가 된 시간
#         }  
       
#       self.messages.append(new_message)
       
#       self.save()
   
# # save 예시
# # AudioFile 객체 생성
# audio_file_instance = AudioFile(owner=owner, client=client)
# # 객체 저장
# audio_file_instance.save()
# # 객체 저장 후의 title 확인
# print(audio_file_instance.title)  
# # 출력 예시: "owner_user_client_name.mp3" (slugified)