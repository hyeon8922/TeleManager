from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
# default=True 제거: 기본값을 설정하지 않습니다.
# null=True 추가: 이 필드는 null 값을 허용합니다.
# blank=True 추가: 이 필드는 폼에서 필수가 아닙니다.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    
    login_attempts = models.IntegerField(default=0)  # 로그인 시도 횟수
    last_attempt_time = models.DateTimeField(null=True, blank=True)  # 마지막 로그인 시도 시간

    def __str__(self):
        return self.user.username  # 사용자의 이름을 반환합니다.

    def increase_login_attempts(self):
        self.login_attempts += 1
        self.last_attempt_time = timezone.now()
        
        # 로그인 시도 횟수가 5회 이상일 경우 계정을 잠금
        if self.login_attempts >= 5:
            self.is_approved = False
        self.save()

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.last_attempt_time = None
        self.save()

    def can_login(self):
        if self.is_approved:
            return True
        
        if self.last_attempt_time:
            # 마지막 로그인 시도 시간이 현재 시간보다 5분 이내인지 확인
            if timezone.now() - self.last_attempt_time < timedelta(minutes=5):
                return False

        self.reset_login_attempts()
        return True
    
class CompanyFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='company_data_files/')
    embedding_file = models.FileField(upload_to='embedding_files/', blank=True, null=True)


    def __str__(self):
        return self.file.name