import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            data = csv.reader(file)
            Ingredient.objects.bulk_create(
                (Ingredient(
                    name=row[0],
                    measurement_unit=row[1])
                    for row in data),
                batch_size=999
            )
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
