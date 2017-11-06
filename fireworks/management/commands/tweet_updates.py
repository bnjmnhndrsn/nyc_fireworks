import datetime
import time
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q

from fireworks.models import Firework
from fireworks.tasks import schedule_tweet

eastern = pytz.timezone('US/Eastern')

def get_est_tz_bounds_in_utc():
    today = timezone.now().astimezone(eastern)
    beginning = today.replace(hour=0,minute=0,second=0,microsecond=0)
    end = today.replace(hour=23,minute=59,second=59,microsecond=999)
    return [beginning.astimezone(pytz.UTC), end.astimezone(pytz.UTC)]
    

class Command(BaseCommand):
    help = 'Tweet out upcoming fireworks'
    
    REMINDER_INTERVALS = (7, 3, 1, 0)
    
    def tweet(self, message, **kwargs):
        self.total_tweets += 1
        if not 'eta' in kwargs:
            kwargs['countdown'] = self.total_tweets * 10

        schedule_tweet.apply_async((message,), **kwargs)
    
    def get_reminder_fireworks(self):
        today = timezone.now()
        time_query = Q()
        bounds = get_est_tz_bounds_in_utc()
        for interval in self.REMINDER_INTERVALS:
            start = bounds[0] + datetime.timedelta(days=interval)
            end = bounds[1] + datetime.timedelta(days=interval + 1)
            time_query = time_query | Q(event_at__gte=start, event_at__lte=end)
        
        return list(Firework.objects.filter(cancelled=False).filter(time_query).order_by('event_at'))            

    def get_new_fireworks(self):
        today = timezone.now()
        fireworks = Firework.objects.filter(cancelled=False, created_at__gte=today - datetime.timedelta(days=1)).order_by('event_at')
        return list(fireworks)
    
    def get_cancelled_fireworks(self):
        today = timezone.now()
        fireworks = Firework.objects.filter(cancelled=True, updated_at__gte=today - datetime.timedelta(days=1)).order_by('event_at')
        return list(fireworks)
    
    def handle(self, *args, **options):        
        new_fireworks = self.get_new_fireworks()
        cancelled_fireworks = self.get_cancelled_fireworks()
        reminder_fireworks = self.get_reminder_fireworks()
        self.total_tweets = 0
        
        if options['verbosity'] > 1:
            print 'New Fireworks: %s' % len(new_fireworks)
            print 'Cancelled Fireworks: %s' % len(cancelled_fireworks)
            print 'Reminder Fireworks: %s' % len(reminder_fireworks)
        
        for firework in new_fireworks: 
            message = firework.get_new_tweet_text()
            self.tweet(message)
        
        for firework in cancelled_fireworks:
            message = firework.get_cancelled_tweet_text()
            self.tweet(message)
        
        for firework in reminder_fireworks:
            days = (firework.event_at - timezone.now()).days
            messages = []
            messages.append(
                (firework.get_morning_reminder_tweet_text(days), {})
            )
            if days == 0:
                messages.append((
                    firework.get_one_hour_reminder_text(),
                    {'eta': firework.event_at - datetime.timedelta(hours=1)}
                ))
                messages.append((
                    firework.get_now_reminder_text(),
                    {'eta': firework.event_at}
                ))
            for message in messages:
                self.tweet(message[0], **message[1])
        
        timezone.deactivate() 

        
        
