
from functools import wraps
from django.db import transaction
import django_rq
from rq import Retry

DEFAULT_RETRY = Retry(max=3, interval=[10, 30, 60])

def enqueue_after_commit(task, *args, queue='default', **kwargs):
    """ put task into rq after instance is store in DB"""
    transaction.on_commit(lambda: django_rq.get_queue(queue).enqueue(task, *args, retry=DEFAULT_RETRY, **kwargs))
       