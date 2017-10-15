from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
import pytz
from dateutil import parser
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from fireworks.models import Firework


TARGET_URL = 'http://www1.nyc.gov/nyc-resources/service/206/fireworks-displays'

eastern = pytz.timezone('US/Eastern')

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def get_text(self):
        r = requests.get(TARGET_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find(class_="richtext").get_text()

    def parse_text(self, text):
        rows = text.split('\n')[1:]
        rows = [row.strip() for row in rows if row.strip()]
        if len(rows) % 3 != 0:
            raise Error('Incorrect number of lines')

        result = []
        for i in range(0, len(rows) - 2, 3):
            result.append(self.parse_firework(*rows[i:i+3]))

        return result

    def parse_firework(self, date, location, sponsor):
        try:
            sponsor_name = re.search('Sponsor: (.+)', sponsor).group(1)
        except AttributeError:
            sponsor_name = ''

        return {
            'event_at': eastern.localize(parser.parse(date)),
            'location': location,
            'sponsor': sponsor_name
        }

    def create_or_update_fireworks(self, data, options):
        now = timezone.now()
        upcoming_fireworks = Firework.objects.filter(event_at__gte=now, cancelled=False)
        found_firework_ids = []
        for item in data:
            if item['event_at'] < now:
                continue
                
            try:
                found = upcoming_fireworks.get(**item)
                found_firework_ids.append(found)
                print 'found new firework with data %s' % item
            except Firework.DoesNotExist:
                print 'creating new firework with data %s' % item
                if options['dry_run']:
                    Firework.objects.create(**item)

        not_found_fireworks = upcoming_fireworks.exclude(id__in=found_firework_ids)
        if len(not_found_fireworks):
            not_found_string = '\n'.join([str(firework) for firework in not_found_fireworks])
            print 'could not find fireworks:\n%s' % not_found_string
            if not options['dry_run']:
                not_found_fireworks.update(cancelled=True)


    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Print scraped data instead of saving',
        )

    def handle(self, *args, **options):
        text = self.get_text()
        parsed = self.parse_text(text)
        self.create_or_update_fireworks(parsed, options)
