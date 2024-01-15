# utils.py

from docx import Document
from django.conf import settings
import os

def read_word_file(file_path):
    full_path = os.path.join(settings.BASE_DIR, 'static', file_path)
    document = Document(full_path)

    # 파일 내용을 읽어와서 반환하는 코드 추가

    return file_content
