import csv

from django.core.management.base import BaseCommand
from recipes.models import Tags


class Command(BaseCommand):
    help = "import data from ingredients.csv"

    def handle(self, *args, **kwargs):
        with open("data/tags.csv", encoding="utf8") as f:
            reader_object = csv.reader(f, delimiter=",")
            # dr = csv.DictReader(f, delimiter=",")
            for row in reader_object:
                obj = Tags(name=row[0], color=row[1], slug=row[2])
                obj.save()
