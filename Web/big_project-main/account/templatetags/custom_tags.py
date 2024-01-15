from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import mammoth  # 설치되어 있지 않은 경우: pip install python-mammoth

register = template.Library()

@register.filter(name='file_content')
@stringfilter
def file_content(value):
    try:
        with open(value, 'rb') as file:
            result = mammoth.extract_raw_text(file)
            return mark_safe(result.value)
    except Exception as e:
        return f"파일을 읽는 중 오류가 발생했습니다: {e}"
