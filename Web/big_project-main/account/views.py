from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from .forms import SignupForm, ProfileUpdateForm, CompanyFileForm, CompanyFileForm2
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CompanyFile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, FormView
from django.urls import reverse_lazy, reverse
import os
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
from account.forms import PasswordChangeForm
from django.urls import reverse_lazy
import csv
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from client.models import Client
from django.contrib.auth.views import LoginView
from .models import Profile
import shutil
from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
import chardet
from captcha.fields import CaptchaField
from django_recaptcha.fields import ReCaptchaField
from .utils import read_word_file

from docx import Document  # python-docx 라이브러리 import


ALLOW_URL_LIST = settings.ALLOW_URL_LIST
FILE_COUNT_LIMIT = settings.FILE_COUNT_LIMIT         
FILE_SIZE_LIMIT_CLIENT = settings.FILE_SIZE_LIMIT_CLIENT 
WHITE_LIST_CLIENT = settings.WHITE_LIST_CLIENT
FILE_SIZE_LIMIT_COMPANY = settings.FILE_SIZE_LIMIT_COMPANY 
WHITE_LIST_COMPANY = settings.WHITE_LIST_COMPANY



class IPRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR')
        if client_ip not in ALLOW_URL_LIST:
            return redirect('account:urlerror')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(IPRequiredMixin, TemplateView):
    template_name = 'registration/profile.html'
    
def index(request):
    
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    return render(request, 'registration/login.html')

# 개인정보 동의
# @method_decorator(logout_message_required, name='dispatch')
class AgreementView(IPRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        request.session['agreement'] = False
        return render(request, 'registration/agreement.html')

    def post(self, request, *args, **kwargs):
        if request.POST.get('agreement1', False) and request.POST.get('agreement2', False):
            request.session['agreement'] = True
            return redirect('account:signup')
        else:
            messages.info(request, "약관에 모두 동의해주세요.")
            return render(request, 'registration/agreement.html')
        
        
# 회원가입
def signup(request):
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # CAPTCHA 검증
            if not form.cleaned_data.get('captcha'):
                form.add_error(None, 'CAPTCHA 검증에 실패했습니다.')
                return render(request, 'registration/signup.html', {'form': form})

            user = form.save(commit=False)
            user.save()

            Profile.objects.create(user=user, is_approved=False)

            return redirect(settings.LOGIN_URL)
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile_update(request):

    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account:profile')  # 프로필 페이지로 리다이렉트
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'registration/profile_update.html', {'form': form})

# 비밀번호 변경
class PasswordChangeView(IPRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('account:login')
    template_name = 'account/password_change_form.html'
    form_class = PasswordChangeForm
    

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "비밀번호가 성공적으로 변경되었습니다!")
        return super().form_valid(form)


# 비밀번호 찾기
class UserPasswordResetView(IPRequiredMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = self.request.POST.get("email")
        if User.objects.filter(email=email).exists():
            return super().form_valid(form)
        # 존재하지 않는 이메일인 경우에 대한 처리
        return redirect(reverse('account:password_reset'))

    def form_invalid(self, form):
        response = super().form_invalid(form)
        # 오류가 발생한 경우에만 JsonResponse 반환
        if self.request.is_ajax():
            return JsonResponse({'email_not_exists': True})
        return response


def error_page(request):
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    return render(request, 'upload/error.html', {'error_message': '잘못된 요청입니다.'})

def urlerror_page(request):
   
    return render(request, 'urlcheck/error2.html', {'error_message': '유효하지 않은 URL 입니다.'})


@login_required
def file_upload(request):
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    if request.method == 'POST':
        form = CompanyFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            user_id = request.user.id
            combined_name = f"{user_id}_{uploaded_file.name}"

            # 파일 확장자 검사
            file_extension = uploaded_file.name.split('.')[-1].lower()
            print(file_extension)
            if file_extension not in WHITE_LIST_COMPANY:
                return render(request, 'upload/error.html', {'error_message': '잘못된 파일 형식입니다. csv 형식의 파일을 제출해주십시오.'})
            
            # 파일 크기 체크
            if uploaded_file.size > FILE_SIZE_LIMIT_COMPANY:
                return render(request, 'upload/error.html', {'error_message': f'파일 크기는 최대 {FILE_SIZE_LIMIT_COMPANY / (1024 * 1024)} MB까지만 허용됩니다.'})
            

            fs = FileSystemStorage(location='media/company_data_files/')

            # 파일의 이름이 이미 존재하는지 확인합니다.
            if not fs.exists(combined_name):
                fs.save(combined_name, uploaded_file)
                user_file = form.save(commit=False)
                user_file.user = request.user
                user_file.file = combined_name
                user_file.save()

                # 파일의 인코딩 검출
                file_path = f'./media/company_data_files/{combined_name}'
                detected_encoding = detect_encoding(file_path)
                
                # CSVLoader로 파일 로드
                loader = CSVLoader(file_path=file_path, encoding=detected_encoding)
                data = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                texts = text_splitter.split_documents(data)

                # hugging face 임베딩 저장
                model_name = "jhgan/ko-sroberta-multitask"
                model_kwargs = {'device': 'cpu'}
                encode_kwargs = {'normalize_embeddings': False}

                hf = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs=model_kwargs,
                    encode_kwargs=encode_kwargs
                )
                # 폴더 만들기
                fold_name = combined_name.split(".")[0]
                try:
                    os.makedirs(f'./media/embedding_files/{fold_name}')
                    print("폴더 생성 완료")
                except:
                    print("폴더 존재 or 에러")
                    pass

                # embedding vector 저장
                vectordb_hf = Chroma.from_documents(
                    documents=texts,
                    embedding=hf, persist_directory=f"./media/embedding_files/{fold_name}")
                vectordb_hf.persist()
                ##################################################

                return redirect('client:list')
            else:
                messages.warning(request, '동일한 파일 이름이 이미 존재합니다.')
                return redirect('client:list')
    else:
        form = CompanyFileForm()

    files = CompanyFile.objects.filter(user=request.user)
    return render(request, 'upload/information.html', {'form': form, 'files': files})

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']
    
# 파일 목록을 출력하는 view입니다.
@login_required
def file_list(request):
    
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    files = CompanyFile.objects.filter(user=request.user)
    return render(request, 'upload/list.html', {'files': files})


@login_required
def edit_file(request, file_id):
    
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    file = get_object_or_404(CompanyFile, id=file_id, user=request.user)

    if request.method == 'POST':
        form = CompanyFileForm2(request.POST, instance=file)
        if form.is_valid():
            form.save()
            return redirect('client:list')  # 클라이언트 목록 뷰로 리디렉션
    else:
        form = CompanyFileForm2(instance=file)

    return render(request, 'upload/edit_file.html', {'form': form, 'file': file})


@login_required
def delete_file(request, file_id):

    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    file = get_object_or_404(CompanyFile, id=file_id, user=request.user)

    if request.method == 'POST':
        file.delete()
        return redirect('client:list')  # 클라이언트 목록 뷰로 리디렉션

    return render(request, 'upload/delete_file.html', {'file': file})



class DeleteSelectedFilesView(LoginRequiredMixin, View):
    
    def post(self, request):
        selected_ids = request.POST.getlist('file_ids')  
        #CompanyFile.objects.filter(id__in=selected_ids).delete()  
        
        for s_id in selected_ids:
            CompanyFile.objects.filter()
            file = CompanyFile.objects.get(id=s_id, user=request.user)
            
            
            file_path = os.path.join('media/company_data_files/', file.file.name)
            
            # 파일 삭제
            if os.path.exists(file_path):
                os.remove(file_path)
            
            
            #### 임베딩 폴더 삭제 ####
            
            folder_name = file.file.name.split(".")[0]  # 파일 이름에서 확장자 제거
            folder_path = os.path.join(settings.MEDIA_ROOT, 'embedding_files', folder_name)
        
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"폴더 {folder_path} 삭제 완료")
            else:
                print(f"폴더 {folder_path}가 이미 없습니다.")
                
            
            ## 모델에서 삭제
            file.delete()    
                
                
        return redirect(reverse('client:list'))  
    

def before(request, message=None):
    
    client_ip = request.META.get('REMOTE_ADDR')

    # 허용 목록에 IP 주소가 있는지 확인
    if client_ip not in ALLOW_URL_LIST:
        return redirect('account:urlerror')
    
    message = request.GET.get('message')
    
    context = {'message': message}
    return render(request, 'registration/before.html', context)

# class CustomLoginView(IPRequiredMixin, LoginView):
    
#     def form_valid(self, form):
#         # 로그인 시도 횟수를 증가시킵니다.
#         user = form.get_user()
#         print(user)
#         profile = Profile.objects.get(user=user)
#         if profile:
#             profile.increase_login_attempts()
        
#         # 기존 로그인 로직을 수행합니다.
#         super().form_valid(form)
        
#         # 로그인한 사용자를 가져옵니다.
#         user = self.request.user

#         # is_approved 값에 따라 리디렉션합니다.
#         if profile and not profile.is_approved:
#             logout(self.request)   # logout 시켜줌
#             return redirect('account:before')  # before.html로 리디렉션
#         else:
#             profile.reset_login_attempts()  # 로그인 시도 횟수 초기화
#             return redirect('index')  # views.index 함수로 리디렉션


class CustomLoginView(IPRequiredMixin, LoginView):

    def form_valid(self, form):
        # 기존 로그인 로직을 수행합니다.
        super().form_valid(form)
        
        # 로그인한 사용자를 가져옵니다.
        user = self.request.user
        
        # is_approved 값에 따라 리디렉션합니다.
        profile = Profile.objects.get(user=user)
        if profile and not profile.is_approved:
            logout(self.request)   # logout 시켜줌
            return redirect('account:before')  # before.html로 리디렉션
        else:
            profile.reset_login_attempts()
            return redirect('index')  # views.index 함수로 리디렉션
        
    def form_invalid(self, form):
        username = form.cleaned_data.get('username')
    
        try:
            profile = Profile.objects.get(user__username=username)
            
            profile.increase_login_attempts()

            if profile.login_attempts >= 5:
                profile.is_approved = False
                profile.save()
                logout(self.request)
                message = "비밀번호 5번 오류로 계정이 이용 불가능합니다. 운영자에게 문의 바랍니다."
                return redirect(reverse('account:before') + f'?message={message}')

        except Profile.DoesNotExist:
        # 입력받은 아이디에 해당하는 프로필이 없는 경우 처리
            print(f"아이디 {username}에 해당하는 프로필이 없습니다.")

        # 기본적으로는 다시 로그인 페이지로 리디렉션합니다.
        return super().form_invalid(form)
    


def read_docx_to_html(file_path):
    # .docx 파일 읽기
    doc = Document(file_path)

    # .docx 내용을 텍스트로 추출
    text_content = ""
    for paragraph in doc.paragraphs:
        text_content += paragraph.text + "<br>"

    return text_content


