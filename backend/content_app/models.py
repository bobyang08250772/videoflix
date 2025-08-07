
import os

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from uuid import uuid4


def upload_video_path(instance, filename):
    """
        slufigy video name
    """
    name, ext = os.path.splitext(filename)
    name = slugify(name) 
    return f"videos/{uuid4().hex}_{name}{ext}"

def validate_video_file_extension(value):
    """
        Vlidate video extension
    """
    ext = os.path.splitext(value.name)[1]  # get file extension
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed: ' + ', '.join(valid_extensions))


class Video(models.Model):
    """
        Video Model
    """
    class Category(models.TextChoices):
        MOVIE = 'MOVIE', 'Movie'
        TUTORIAL = 'TUTORIAL', 'Tutorial'
        VLOG = 'VLOG', 'Vlog'
        MUSIC = 'MUSIC', 'Music Video'
        NEWS = 'NEWS', 'News'
        GAMING = 'GAMING', 'Gaming'
        DOCUMENTARY = 'DOCUMENTARY', 'Documentary'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True, choices=Category, default=Category.MOVIE)
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to=upload_video_path, null=True, blank=True, validators=[validate_video_file_extension])

    def __str__(self):
        return self.title