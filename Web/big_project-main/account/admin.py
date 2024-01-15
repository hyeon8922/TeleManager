from django.contrib import admin
from .models import Profile
from .models import CompanyFile
# Register your models here.



class CompanyFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'upload_date',)

admin.site.register(Profile)
admin.site.register(CompanyFile, CompanyFileAdmin) 
    
