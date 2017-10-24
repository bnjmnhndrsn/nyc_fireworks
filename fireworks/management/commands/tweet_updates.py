import datetime
import time
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q

from fireworks.models import Firework
from fireworks.twitter import tweet

eastern = pytz.timezone('US/Eastern')

class Command(BaseCommand):
    help = 'Tweet out upcoming fireworks'
    
    REMINDER_INTERVALS = (14, 7, 3, 1, 0)
    
    def tweet(self, message):
        if self.options['dry_run']:
            print message
        else:
            tweet(message)
            time.sleep(60)
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Print out tweets instead of actually tweeting',
        )
    
    def get_reminder_fireworks(self):
        today = timezone.now().date()
        time_query = Q()
        for interval in self.REMINDER_INTERVALS:
            time_query = time_query | Q(event_at__date=today + datetime.timedelta(days=interval))
        
        return Firework.objects.filter(cancelled=False).filter(time_query)            

    def get_new_fireworks(self):
        today = timezone.now().date()
        return Firework.objects.filter(cancelled=False, created_at__date=today)
    
    def get_cancelled_fireworks(self):
        today = timezone.now().date()
        return Firework.objects.filter(cancelled=True, updated_at__date=today)
                
    def get_message(self, prefix, firework):
        return '%s: %s on %s. Sponsored by %s' % (
            prefix, firework.location, firework.event_at.strftime('%b %d at %I:%M %p'), firework.sponsor
        )
    
    def handle(self, *args, **options):
        self.options = options
        
        timezone.activate(eastern)
        
        new_fireworks = self.get_new_fireworks()
        cancelled_fireworks = self.get_cancelled_fireworks()
        reminder_fireworks = self.get_reminder_fireworks()
        
        if self.options['verbosity'] > 1:
            print 'New Fireworks: %s' % len(new_fireworks)
            print 'Cancelled Fireworks: %s' % len(cancelled_fireworks)
            print 'Reminder Fireworks: %s' % len(reminder_fireworks)   
            
        for firework in new_fireworks:
            message = self.get_message('NEW', firework)
            self.tweet(message)
        
        for firework in cancelled_fireworks:
            message = self.get_message('CANCELLED', firework)
            self.tweet(message)
        
        for firework in reminder_fireworks:
            message = self.get_message('REMINDER', firework)
            self.tweet(message)

        
        
