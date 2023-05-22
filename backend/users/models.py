from django.contrib.auth.models import AbstractUser
from django.db import models

# class User(AbstractUser):
#     username = models.CharField(
#         'Логин',
#         max_length=150,
#         unique=True,
#         help_text='Nickname'
#     )
#     password = models.CharField(
#         'Пароль',
#         max_length=150,
#         blank=True,
#         help_text='Пароль',
#     )
#     email = models.EmailField(
#         'email',
#         max_length=254,
#         help_text='Электронная почта',
#         unique=True,
#     )
#     first_name = models.CharField(
#         'Имя',
#         max_length=150,
#         blank=True,
#         help_text='Имя',
#     )
#     last_name = models.CharField(
#         'Фамилия',
#         max_length=150,
#         blank=True,
#         help_text='Фамилия',
#     )

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('username', 'email'),
#                 name='unique_user'
#             )
#         ]

#     def __str__(self) -> str:
#         return self.username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
