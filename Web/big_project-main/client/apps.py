from django.apps import AppConfig
# 음성을 mp3로 변환 및 저장하기 위한 라이브러리들
# from flask import Flask, request, render_template
# from pydub import AudioSegment
import os


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "client"


