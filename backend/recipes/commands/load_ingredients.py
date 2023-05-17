import os
import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


DATA_DIR = 'data'


class Command(BaseCommand):
    help = 'Load ingredients data into database'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='?', default='ingredients.json',
                            type=str, help='JSON file with ingredients data')

    def handle(self, *args, **options):
        filename = options['filename']
        file_path = os.path.join(os.getcwd(), DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ingredient in data:
                    name = ingredient.get('name')
                    unit = ingredient.get('measurement_unit')
                    if name and unit:
                        try:
                            Ingredient.objects.create(
                                name=name,
                                measurement_unit=unit
                            )
                            self.stdout.write(self.style.SUCCESS(
                                f'Successfully added {name}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f'Error adding {name}: {e}'))
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'Skipping invalid ingredient: {ingredient}'))
        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')
