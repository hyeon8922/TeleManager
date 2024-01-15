from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.views.generic import ListView, View
import pandas as pd
from .models import Client
from .forms import ClientForm  # 고객 모델 폼
from django.urls import reverse
from datetime import datetime
import os
import zipfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import CompanyFile, Profile
from chatbot.models import ChatBot
from pytz import UTC
from django.core.paginator import Paginator
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from django.http import HttpResponse
from openai import OpenAI
# 녹음한 음성을 mp3로 변환하여 저장하기 위한 라이브러리.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators import gzip
from django.utils.decorators import method_decorator
from django.views import View
import json
# from django.shortcuts import render
# import os
# from pydub import AudioSegment
## For URL Checking
from django.conf import settings
from django.http import HttpResponseForbidden
# from pydub import AudioSegment

# from transformers import BertForSequenceClassification
from transformers import AlbertForSequenceClassification
import torch
from transformers import pipeline
from transformers import BertTokenizer
from transformers import BertTokenizerFast

open_api_key = os.environ.get('OPENAI_API_KEY')

ALLOW_URL_LIST = settings.ALLOW_URL_LIST
FILE_COUNT_LIMIT = settings.FILE_COUNT_LIMIT         
FILE_SIZE_LIMIT_CLIENT = settings.FILE_SIZE_LIMIT_CLIENT 
WHITE_LIST_CLIENT = settings.WHITE_LIST_CLIENT

class IPRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # client_ip = request.META.get('REMOTE_ADDR')
        # if client_ip not in settings.ALLOW_URL_LIST:
        #     return HttpResponseForbidden(render(request, 'index.html'))
        return super().dispatch(request, *args, **kwargs)
    
class ClientListView(IPRequiredMixin, LoginRequiredMixin, ListView):
    model = Client
    template_name = 'client/client_list.html'  
    
    def get_context_data(self, **kwargs): # 2
        context = super().get_context_data(**kwargs)  # 컨텍스트 데이터 가져옴
        
        client_list = Client.objects.filter(user = self.request.user)
        file_list = CompanyFile.objects.filter(user = self.request.user)
        
        search_key = self.request.GET.get("keyword", "")
        if search_key:
            client_list = Client.objects.filter(user = self.request.user, name__icontains=search_key)

        client_paginator = Paginator(client_list, 5)
        file_paginator = Paginator(file_list, 5)
    
        client_page_number = self.request.GET.get('client_page')
        file_page_number = self.request.GET.get('file_page')
        
            
        client_obj = client_paginator.get_page(client_page_number)
        file_obj = file_paginator.get_page(file_page_number)
        
        
        context['tmgoal'] = self.request.session.get('tmgoal', None)
        context['client_obj'] = client_obj
        context['file_obj'] = file_obj
        context['q'] = search_key

        return context

    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist('client_ids')  
        Client.objects.filter(id__in=selected_ids).delete()  
        return redirect(reverse('client:list'))  
    
    def get_queryset(self): 
        user = self.request.user
        print(f"Current User ID: {user.id}")
        queryset = Client.objects.filter(user=self.request.user).order_by('-tm_date')  # '-tm_date'는 내림차순 정렬을 의미
        print(f"Queryset length: {queryset.count()}")
        #print(f"Queryset data: {queryset.values()}")
        return queryset



class DeleteSelectedClientsView(IPRequiredMixin, View):
    
    def post(self, request):
        selected_ids = request.POST.getlist('client_ids')  
        Client.objects.filter(id__in=selected_ids).delete()  
        return redirect(reverse('client:list'))  


def normalize_gender(gender_str):
    # 성별을 Male, Female로 변환
    
    if gender_str in ['남성', '남', '남자', 'm', 'M']:
        return '남'
    elif gender_str in ['여성', '여', '여자', 'f', 'F']:
        return '여'
    else:
        return None  


def error_page(request):  
    return render(request, 'client/error.html', {'error_message': '잘못된 요청입니다.'})


def upload_excel(request): 

    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')

    
    
    if request.method == 'POST' and request.FILES['excel_file']:
        check_file = request.FILES['excel_file']
        
        # # 파일 개수 체크
        # if len(request.FILES.getlist('excel_file')) > FILE_COUNT_LIMIT:
        #     print(len(request.FILES.getlist('excel_file')))
        #     return render(request, 'client/error.html', {'error_message': f'파일은 최대 {FILE_COUNT_LIMIT}개까지만 업로드 가능합니다.'})
        

        file_extension = check_file.name.split('.')[-1].lower()

        # 파일 형식 체크
        if file_extension not in WHITE_LIST_CLIENT:
            return render(request, 'client/error.html', {'error_message': '잘못된 파일 형식입니다. xlsx, xls 형식의 파일을 제출해주십시오.'})

        # 파일 크기 체크
        if check_file.size > FILE_SIZE_LIMIT_CLIENT:
            return render(request, 'client/error.html', {'error_message': f'파일 크기는 최대 {FILE_SIZE_LIMIT_CLIENT / (1024 * 1024)} MB까지만 허용됩니다.'})
        
        
        tmgoal = request.POST.get('tmgoal')
        request.session['tmgoal'] = tmgoal
        df = pd.read_excel(check_file)
        
        print(df.columns)
        
        for index, row in df.iterrows():
            user = request.user
            name = str(row['name'])
            number = row['number']
            email = row['email']
            
            print(name, number, email)
            # 기존에 손님 데이터와 중복되는 데이터인지 확인
            existing_client = Client.objects.filter(name=name, number=number, email=email, user= user).first()
            
            if existing_client is not None:
                print(existing_client.name)
                continue
            
            # raw_birth_date 에는 마스킹 전 생년월일
            raw_birth_date = row.get('birth_date', None)
            
            # 생년월일이 엑셀로 들어올 경우, age 계산
            if raw_birth_date:
                birth_date = raw_birth_date.to_pydatetime()  # Timestamp 객체를 datetime 객체로 변환
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
                # 생년월일 마스킹        
                masked_birth_date = raw_birth_date.strftime('%Y-%m-%d')[:5] + 'XX-XX'
            else:  
                age = None
                masked_birth_date = None
            
            # 정규화 전 성별
            raw_gender = row.get('gender', None)
            
            # 성별 변환
            normalized_gender = normalize_gender(raw_gender)
            
            temp_date = UTC.localize(datetime.now())
            
            user = request.user # 문제는 원래 저장되어 있던 데이터여서 새로 안된거일 뿐이었다. 데이터베이스를 초기화하는 코드가 약간 필요할듯 하다.
            #if user.is_authenticated:
            #    print(f"User ID: {user.pk}")
            #else:
            #    print("User is not authenticated.")
            
            # info 필드에 추가 정보 저장
            info = ""

            # 제외된 키를 제외한 모든 키와 값을 추가
            for key, value in row.items():
                if key not in ['name', 'number','gender', 'email', 'birth_date','location']:  # 원하는 키를 제외한 리스트
                    info += f"{key}: {value}, "
            
        
            Client.objects.create(
                user=user,
                name=name,
                location=row['location'],
                number=number,
                birth_date=masked_birth_date,
                age=age,
                tm_date=temp_date,
                gender=normalized_gender,
                email=email,
                info = info.strip()
            )
        print(f"Client {Client.id} created successfully.")  # 디버깅 메시지 잘뜬다.
        print(tmgoal)
        
        return redirect('client:list')
    
    
    return render(request, 'client/upload.html')

def edit_client(request, client_id):
    
    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')

    
    client = get_object_or_404(Client, id=client_id, user=request.user)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client:list')  # 클라이언트 목록 뷰로 리디렉션
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'client/edit_client.html', {'form': form, 'client': client})

@login_required
def delete_client(request, client_id):
    
    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')

    
    client = get_object_or_404(Client, id=client_id, user=request.user)
    
    if request.method == 'POST':
        client.delete()
        return redirect('client:list')  # 클라이언트 목록 뷰로 리디렉션
    
    return render(request, 'client/delete_client.html', {'client': client})


def selected_items(request):

    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')

    
    selected_clients = request.GET.get('selected_clients', '').split(',')
    selected_files = request.GET.get('selected_files', '').split(',')

    # 빈 문자열을 제거합니다. ( 선택이 안된 경우 )
    selected_clients = [id for id in selected_clients if id]
    selected_files = [id for id in selected_files if id]

    # 처음엔 빈 쿼리셋할당
    clients = Client.objects.none()  
    files = CompanyFile.objects.none()  

    if selected_clients:   # 해당 되는 clients 넣어줌
        clients = Client.objects.filter(id__in=selected_clients)

    if selected_files:     # 해당 되는 files 넣어줌
        files = CompanyFile.objects.filter(id__in=selected_files)
        

    context = {
        'selectedClients': clients,
        'selectedFiles': files,
    }

    return render(request, 'client/selected_items.html', context)



def start_tm(request):
    
    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')


    # global start_tm_hf
    whisper = OpenAI()
    input_data = ''
    selected_clients = []
    selected_files = []
    question_tm=[] # hj
    
    if request.method == 'POST':
        input_data = request.POST.get('input_data', '')
        selected_clients = request.POST.get('selected_clients', '').split(',')
        selected_files = request.POST.get('selected_files', '').split(',')
 
 
        # 빈 문자열을 제거합니다. ( 선택이 안된 경우 )
        selected_clients = [id for id in selected_clients if id]
        selected_files = [id for id in selected_files if id]
 
        # 처음엔 빈 쿼리셋 할당
        clients = Client.objects.none()  
        files = CompanyFile.objects.none()  
 
        if selected_clients:   # 해당 되는 clients 넣어줌
            clients = Client.objects.filter(id__in=selected_clients)
 
        if selected_files:     # 해당 되는 files 넣어줌
            files = CompanyFile.objects.filter(id__in=selected_files)
 
        # 회사 파일 벡터 임베딩 경로 가져오기
        file_name = files[0].file.name.split('.')[0]
        embeding_file_url = './media/embedding_files/{}'.format(file_name)
        # print(embeding_file_url)
 
        # 질문지 생성해주는 hugginface 모델 불러오기
        llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0, openai_api_key=open_api_key)
       
        # start_tm 페이지 렌더링 부분(아웃바운드 목적 적고 send 누를 때 실행)
        start_tm_model_name = "jhgan/ko-sroberta-multitask"
        start_tm_model_kwargs = {'device': 'cpu'}
        start_tm_encode_kwargs = {'normalize_embeddings': False}
        start_tm_hf = HuggingFaceEmbeddings(
            model_name=start_tm_model_name,
            model_kwargs=start_tm_model_kwargs,
            encode_kwargs=start_tm_encode_kwargs,
            # cache_dir=True
            )
       
        chatbots = [] # 챗봇 리스트 생성
        chatbot_ids = [] # 챗봇 고유 아이디 번호
        
        # audio 폴더 생성하기(계정 폴더)
        # 폴더가 존재하지 않으면 폴더를 생성
        audio_path = f"./media/audio/{file_name}/"
        if not os.path.exists(audio_path): # 폴더 존재하지 않을경우 생성
            os.makedirs(audio_path)
        else: # 폴더 존재할 경우 패스
            pass
        
        # 고객 하나씩 접근해서 정보 가져오기
        
        for c in clients:
            clients_info = [] # 고객 정보가 들어간 리스트
            
            # 열 정보만 가져오기
            excluded_fields = ['user', 'tm_date']
            user_defined_fields = [field.name for field in Client._meta.get_fields() if not field.auto_created]
            client_values = [(field, getattr(c, field)) for field in user_defined_fields if field not in excluded_fields]

            # audio/계정 안에 고객당 폴더 생성하기
            # 폴더가 존재하지 않으면 폴더를 생성
            final_save_path = f"./media/audio/{file_name}/{c.id}"
            if not os.path.exists(final_save_path): # 폴더 존재하지 않을경우 생성
                os.makedirs(final_save_path)
                # print(f"{audio_path} 폴더가 생성되었습니다.")
            else: # 폴더 존재할 경우 패스
                pass
            
            # 질문지 생성부분
            ments = make_phrases(client_values, input_data, embeding_file_url, start_tm_hf, llm)
            # print(ments)
            print(f"{c}의 문구 생성 완료")
           
            # 데이터 저장하기
            chatbot = ChatBot(
                owner = request.user,
                client = c,
                outbound_message=ments['answer'],
                messages=[],
                outbound_purpose=ments['question'],
            )
            chatbot.save()
            chatbots.append(chatbot)
            chatbot_ids.append(chatbot.id)
           
            questions = ments['answer'].split("\n")
            
            # # 생성된 문구별 각각 음성 파일로 저장하는 부분
            for i, q in enumerate(questions):
                if len(q)<1:
                    continue
                print(q, len(q))
                question_tm.append(q) # hj
            #     try:
            #         q = q[q.index('"'):]
            #         response = whisper.audio.speech.create(
            #             model="tts-1",
            #             voice="nova",
            #             input=f"{q}",
            #         )
            #         response.stream_to_file(f"{final_save_path}/{str(i)}.mp3")
            #         # response.stream_to_file(f"./{str(i)}.mp3")
            #     except:
            #         pass
 
        #print('@@@')

 
    context = {
        'selectedClients': clients,
        'selectedFiles': files,
        'input_data': input_data,  # 추가
        'chatbots': chatbots,
        'chatbots_ids':chatbot_ids,
        'mentsanswer' : ments['answer'], # 20240102 yh 대답 부분이 필요해서 추가함.
        'question' : question_tm # hj
    }
    
    try:
        # text_processing 또는 다른 함수에서 전달한 데이터
        data_to_send = {
            "question": question_tm,
            # 다른 필요한 데이터들...
        }

        # 세션에 데이터 저장
        request.session['data_to_send'] = data_to_send

 
        return render(request, 'client/start_tm.html', context)
    
    except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
# 문구 생성 부분
def make_phrases(user_info, purpose, embeding_url, hf, llm):

    system_template = f"""당신은 최고의 아웃바운드 상담사입니다.
    다음과 같은 맥락을 사용하여 마지막 질문에 대답하십시오.
    만약 답을 모르면 모른다고만 말하고 답을 지어내려고 하지 마십시오.
    답변은 최대 세 문장으로 하고 가능한 한 간결하게 유지하십시오.
    비슷한 답변은 하지 마십시오.
    답변을 할 때, 고객에 대한 정보는 이와 같습니다.
    고객에 대한 정보 : {user_info}.
    고객의 정보를 활용하여 맞춤형으로 문구를 작성해 주십시오.(친근하게 이름을 부르며)
    {{summaries}}
    질문: {{question}}
    도움이 되는 답변:"""
    # print(system_template)
    # print()
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")
    ]

    # prompt 내에 변수처럼 쓸 수 있게끔 해두는 장치
    prompt = ChatPromptTemplate.from_messages(messages)
    
    chain_type_kwargs = {"prompt": prompt}

    vectordb_hf = Chroma(persist_directory=embeding_url, embedding_function=hf)
    # retriever_hf = vectordb_hf.as_retriever(search_type='mmr')
    retriever_hf = vectordb_hf.as_retriever()
    
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever = retriever_hf,
        return_source_documents=False, # source document를 return
        chain_type_kwargs=chain_type_kwargs # langchain type argument에다가 지정한 prompt를 넣어줌, 별도의 prompt를 넣음
    )
    
    query = f'''{[user_info[0], user_info[-1]]}고객의 특징을 바탕으로 맞춤형으로 목적에 맞게 답해줘. 카드 이름도 같이 명시해줘
    목적 : {purpose}'''  # Provide the input as a dictionary
    result = chain(query)
    # print(result['answer'])
    
    return result

# 문구 감정 분류 및 결과 내보내는 함수
# sentence_model = BertForSequenceClassification.from_pretrained("klue/bert-base", num_labels=3)
sentence_model = AlbertForSequenceClassification.from_pretrained("kykim/albert-kor-base", num_labels=3)
# Load model weights with map_location to 'cpu'
# sentence_model.load_state_dict(torch.load("./models/BERT_sentiment_analysis_model.pt", map_location='cpu'))
sentence_model.load_state_dict(torch.load("./models/ALBERT_sentiment_analysis_model.pt", map_location='cpu'))
# Move the model to the specified device (either 'cpu' or 'cuda')
sentence_model = sentence_model.to('cpu')
# sentence_tokenizer = BertTokenizer.from_pretrained('klue/bert-base')  # tokenizer 이름은 위에서 받은 사전학습된 모델의 이름이랑 항상 같아야 함
sentence_tokenizer = BertTokenizerFast.from_pretrained("kykim/albert-kor-base")
# 여기에서 user_message를 사용하여 필요한 작업 수행
pipe = pipeline("text-classification", model=sentence_model, tokenizer=sentence_tokenizer, function_to_apply='softmax', top_k=1)

@csrf_exempt
def text_processing(request):

    
    # client_ip = request.META.get('REMOTE_ADDR')

    # # 허용 목록에 IP 주소가 있는지 확인
    # if client_ip not in ALLOW_URL_LIST:
    #     return redirect('account:urlerror')


    global pipe
    
    if request.method == "POST":
        # try:
        # POST 요청으로 받은 데이터
        data = json.loads(request.body)
        user_message = data.get("userMessage", "")

        # 여기에서 user_message를 사용하여 필요한 작업 수행    
        # 0중립, 1긍정, 2부정  
        label_dict = {'LABEL_0' : '중립', 'LABEL_1' : '긍정', 'LABEL_2' : '부정'}
        values = pipe(user_message)
        result = label_dict[values[0][0]['label']] # [긍정, 중립, 부정] 이 셋중 하나 값 가짐
        
        # 결과를 JSON 형식으로 응답
        return JsonResponse({"result": result})
        # except Exception as e:
        #     return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "POST 요청만 지원합니다."}, status=400)


@csrf_exempt
def message_results(request): # 프론트앤드에서 채팅 내용 모두 저장하기
    if request.method == 'POST':
        data = json.loads(request.body)
        all_messages = data.get('all_messages')
        chatbots_id = data.get('chatbots_id')
        # print(f"파이썬에서 받은 데이터")
        # print(all_messages)
        # print(chatbots_id)
        # print("파이썬 끝")
        
        if chatbots_id is not None:
            try:
                # 모델에 저장
                chatbot = ChatBot.objects.get(id=chatbots_id)
                for i in range(0, len(all_messages), 2):
                    role = all_messages[i] if i < len(all_messages) else None
                    content = all_messages[i + 1] if i + 1 < len(all_messages) else None
                    chatbot.add_message(role, content)
                print(chatbot.messages)
                chatbot.outbound_end = "End"
                chatbot.save()
                return JsonResponse({"result": "All Message Save Success."})
            except ChatBot.DoesNotExist:
                return JsonResponse({"error": f"ChatBot with id {chatbots_id} does not exist."}, status=404)
        else:
            return JsonResponse({"error": "chatbots_id is required in the request."}, status=400)

    return JsonResponse({'status': 'error'})



@csrf_exempt
def sendAllMessages(request): # 프론트앤드에서 채팅 내용 모두 저장하기
    if request.method == 'POST':
        data = json.loads(request.body)
        chatbots_id = data.get('chatbots_id')
        # print("파이썬에서 받은거")
        # print(chatbots_id)
        chatbot = ChatBot.objects.get(id=chatbots_id)
        n = len([i for i in chatbot.outbound_message.split("\n") if len(i)>0])
        # print(chatbot.messages)
        # print(chatbot.outbound_message)
        # print(chatbot.outbound_message.split("\n")[0])
        # print("끝")
        return JsonResponse({"result": chatbot.messages, 
                             "outbound_message":chatbot.outbound_message.split("\n")[0],
                             "outbound_end":chatbot.outbound_end,
                             "q_len":n,
                             })

    return JsonResponse({'status': 'error'})
# # 녹음한 파일을 저장하는 function
# @csrf_exempt
# @require_POST
# def save_audio(request):
    
    # audio_data = request.FILES.get('audio_data')
    # if audio_data:
    #     ogg_save_path = os.path.join('../media/audio/', 'audio.ogg')
    #     mp3_save_path = os.path.join('../media/audio/', 'audio.mp3')
 
    #     # 원본 ogg 파일을 저장
    #     with open(ogg_save_path, 'wb') as ogg_file:
    #         for chunk in audio_data.chunks():
    #             ogg_file.write(chunk)

    #     # ogg 파일을 mp3로 변환
    #     audio_segment = AudioSegment.from_file(ogg_save_path) # 여기가 문제.

    #     # ffmpeg 경로 설정 (설치한 경로로 변경)
    #     # AudioSegment.converter = "C:/path/to/ffmpeg"
        
    #     audio_segment.export(mp3_save_path, format='mp3')

 
    #     # ogg 파일을 mp3로 변환
    #     audio_segment = AudioSegment.from_file(ogg_save_path) # 여기가 문제.
 
    #     # ffmpeg 경로 설정 (설치한 경로로 변경)
    #     # AudioSegment.converter = "C:/path/to/ffmpeg"
       
    #     audio_segment.export(mp3_save_path, format='mp3')
 
    #     return JsonResponse({'message': 'Audio file saved and converted to MP3 successfully.'})
    # else:
    #     return JsonResponse({'message': 'No audio data received.'})