from rest_framework import serializers

from .models import User


class SingUpSerializer(serializers.ModelSerializer):
    """
    Тут тесты требуют проверку на.
    максимальную длинну username и email.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя "me"')
        return value

    def validate(self, data):
        user_if = User.objects.filter(username=data['username']).exists()
        email_if = User.objects.filter(email=data['email']).exists()
        if user_if and not email_if:
            raise serializers.ValidationError('Имя уже использовалась')
        if email_if and not user_if:
            raise serializers.ValidationError('Почта уже использовалось')
        if User.objects.filter(username=data['username'],
                               email=data['email']).exists():
            return data
        return data
