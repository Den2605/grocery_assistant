import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    help = "import data from ingredients.csv"

    def handle(self, *args, **kwargs):
        with open("data/ingredients.csv", encoding="utf8") as f:
            reader_object = csv.reader(f, delimiter=",")
            # dr = csv.DictReader(f, delimiter=",")
            for row in reader_object:
                obj = Ingredients(
                    name=row[0],
                    measurement_unit=row[1],
                )
                obj.save()
