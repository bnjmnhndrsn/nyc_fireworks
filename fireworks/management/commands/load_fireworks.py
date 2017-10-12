from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re

from django.core.management.base import BaseCommand, CommandError
from fireworks.models import Firework


TARGET_URL = 'http://www1.nyc.gov/nyc-resources/service/206/fireworks-displays'

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
            'event_at': datetime.strptime(date, '%A, %B %d, %Y, %I:%M %p'),
            'location': location,
            'sponsor': sponsor_name
        }

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
        print parsed
