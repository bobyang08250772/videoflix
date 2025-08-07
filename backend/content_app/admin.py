from django.contrib import admin
from django import forms
from .models import Video

class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'

        widgets = {
            'video_file': forms.ClearableFileInput(attrs={
                'accept': 'video/*'
            })
        }

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Video._meta.fields]
    form = VideoAdminForm
