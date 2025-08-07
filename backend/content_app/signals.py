from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from content_app.tasks import convert_resolutions_to_hls, delete_hls_files
from core.utils.tasks import enqueue_after_commit
import os

def save_remove(path):
    """
        Capture File not found error so it will not throw error 
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error deleting file {path}: {e}")


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
        Convert video in diffrent resolutions
    """
    if created:
        enqueue_after_commit(convert_resolutions_to_hls, instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
        Delete files from Media if video object is delete
    """
    if instance.video_file and os.path.isfile(instance.video_file.path):
        enqueue_after_commit(save_remove, instance.video_file.path)
        enqueue_after_commit(delete_hls_files, instance.video_file.path)

    if instance.thumbnail_url and os.path.isfile(instance.thumbnail_url.path):
        enqueue_after_commit(save_remove, instance.thumbnail_url.path)

        
            


