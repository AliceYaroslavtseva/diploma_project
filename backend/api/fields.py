import base64
import os

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers


class Hex2NameColor(serializers.Field):
    """Сериализатор цвета в тегах."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')


class Base64ImageField(serializers.ImageField):
    """Сериализатор фото в рецептах."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            img_name = 'image.' + ext
            img_path = os.path.join('images', img_name)
            data = ContentFile(base64.b64decode(imgstr), name=img_path)

        return super().to_internal_value(data)
