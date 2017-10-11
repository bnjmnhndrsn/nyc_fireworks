import requests
from django.core.management.base import BaseCommand, CommandError
from fireworks.models import Firework
from bs4 import BeautifulSoup

TARGET_URL = 'http://www1.nyc.gov/nyc-resources/service/206/fireworks-displays'

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    
    def get_text(self):
        r = requests.get(TARGET_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.find(class_="richtext").get_text()
        rows = text.split('\n')[1:]
        rows = [row.strip() for row in rows if row.strip()]
        print rows

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Print scraped data instead of saving',
        )

    def handle(self, *args, **options):
        self.get_text()
