from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text='Nickname'
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=True,
        help_text='Пароль',
    )
    email = models.EmailField(
        'email',
        max_length=254,
        help_text='Электронная почта',
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
        help_text='Имя',
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
        help_text='Фамилия',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username
