import os
import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Tag


DATA_DIR = 'data'


class Command(BaseCommand):
    help = 'Load ingredients data into database'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='?', default='tags.json',
                            type=str, help='JSON file with tags data')

    def handle(self, *args, **options):
        filename = options['filename']
        file_path = os.path.join(os.getcwd(), DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for tag in data:
                    name = tag.get('name')
                    color = tag.get('color')
                    slug = tag.get('slug')
                    if name and slug:
                        try:
                            Tag.objects.create(
                                name=name,
                                color=color,
                                slug=slug
                            )
                            self.stdout.write(self.style.SUCCESS(
                                f'Successfully added {name}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(
                                f'Error adding {name}: {e}'))
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'Skipping invalid ingredient: {tag}'))
        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')
