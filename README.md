# Big_Project
KT Aivle School Big Project

##### 목차
[0. 팀&역할 Team&Role](#0-팀--역할-teamroles)  
[1. 선정 배경](#1-선정-배경)  
[2. 주요 내용](#2-주요-내용)  
[3. 기대 효과](#3-기대-효과)  
[4. 서비스 플로우](#4-서비스-플로우)  
[5. 프로젝트 아키텍처](#5-프로젝트-아키텍처)  
[6. 데이터](#6-데이터)  
[7. 모델-평가](#7-모델-평가)  


# TeleManager TM 서비스
## 0. 팀 & 역할 Team&Roles
|**김경민**|**이현태**|**김예훈**|**노민성**|**김현정**|**조민지**|
|:---:|:---:|:---:|:---:|:---:|:---:|
|<img src="/readme_files/GyungMin.png" width="100" height="100"/>|<img src="/readme_files/HyungTae.jpeg" width="100" height="100"/>|<img src="/readme_files/yeahun.jpeg" width="100" height="100"/>|<img src="/readme_files/minseung.png" width="100" height="100"/>|<img src="/readme_files/hyungjung.jpeg" width="100" height="100"/>|<img src="/readme_files/minG.jpeg" width="100" height="100"/>|
|[![GitHub](/readme_files/gitimage.png)](https://github.com/Leon-real)|[![GitHub](/readme_files/gitimage.png)](https://github.com/leeht0113)|[![GitHub](/readme_files/gitimage.png)](https://github.com/yhkimox)|[![GitHub](/readme_files/gitimage.png)](https://github.com/maatanyy)|[![GitHub](/readme_files/gitimage.png)](https://github.com/hyeon8922)|[![GitHub](/readme_files/gitimage.png)](https://github.com/hahahoho0320)|
|**AI Researcher**, Web Back-End|**AI Researcher**, Web Back-End|AI Researcher, **Web Front-End**|AI Researcher, **Web Back-End**|AI Researcher, **Web Front-End**|AI Researcher, **Web Back-End**|

## 1. 선정 배경
1. 감정노동에 시달리는 텔레마케터의 고충을 덜고자 CS 업무의 자동화 시스템 제안   
2. AICC를 통한 상담원 업무 보완 및 확대되는 AICC 시장의 기술 고도화  

<img src="/readme_files/1_1.png" style="width:48%;"> <img src="/readme_files/1_2.png" style="width:48%;">


## 2. 주요 내용
1. 고객에게 맞춤화된 아웃바운드 문구 생성으로 개인화 마케팅   
2. 지속적인 발화자의 감정 분석을 통한 고객과 상호작용  
3. 자동화하여 시간 절감 및 업무 효율성 증대  

<img src="/readme_files/2_1.png" style="width:48%;"> <img src="/readme_files/2_2.png" style="width:48%;">

## 3. 기대 효과
<img src="/readme_files/3_1.png" style="width:100%;">

## 4. 서비스 플로우
1. 각 고객사의 정보를 업데이트(고객 정보, 기타 정보)  
2. 아웃바운드 나갈 고객을 선택한다.  
3. 아웃바운드 나갈 목적입력  
4. 각 고객에 맞추어 목적에 맞는 문구로 아웃바운드 실시  
<img src="/readme_files/flow.png"/>


## 5. 프로젝트 아키텍처
<img src="/readme_files/5_1.png" style="width:100%;">

## 6. 데이터
|TRAIN / TEST|RAG(LangChain)|감성분류|출처|Total|
|------------|--------------|--------|----|-----|
||카드 회사 크롤링 자체 데이터||자체 데이터||
|Train||속성 기반 감성 분석 말뭉치 2021|국립국어원|5591|
|||속성 기반 감성 분석 말뭉치 2021 데이터 증강|국립국어원|3730|
|||속성 기반 감정 데이터|AI Hub|1834|
|||OPENAI를 통한 감성 분류 자체 데이터 & 데이터 증강|자체 데이터|220|
|Total||||11775|
|Test||속성 기반 감정 데이터|AI Hub|246|
|Total||||12021|

## 7. 모델-평가
* 카드 고릴라 (https://www.card-gorilla.com/home) 사이트에 있는 카드 정보를 크롤링하여 회사 정보 데이터로 활용
* LangChain을 기반으로 RAG 기술을 통해 카드 홍보 아웃바운드 마케팅 문구 생성
* OPENAI를 활용하여 카드 상담에서 일어날 수 있는 발화문 데이터 생성

<img src="/readme_files/6_1.png" style="width:100%;">

|AI 모델|성능(accuracy)|모델 크기|사전학습 모델|
|-------|--------------|---------|-------------|
|ALBERT|0.8984|50.3MB|https://huggingface.co/kykim/albert-kor-base|
|BERT|0.8821|422.1MB|https://huggingface.co/klue/bert-base|
|CNN|0.76|||
|ELECTRA|0.7398|430.9MB|https://huggingface.co/monologg/koelectra-base-v3-discriminator|
|LSTM|0.72|||

* Pretrained Language Model을 fine-tuning하여 고객 발화문 감성 분류 모델 구축
* RAG, 모델 학습 코드는 아래 github 참고
* https://github.com/leeht0113/rag_sentiment_analysis








