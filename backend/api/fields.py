# import base64
# import os
import webcolors
# from django.core.files.base import ContentFile
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
