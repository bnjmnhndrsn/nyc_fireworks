from celery import task
from .twitter import tweet

@task(priority=1)
def schedule_tweet(message):
    tweet(message)
