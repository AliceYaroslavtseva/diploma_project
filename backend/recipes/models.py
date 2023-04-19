from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150
    )
    quantity = models.FloatField(
        verbose_name='Количество ингридиента',
    )
    units = models.CharField(
        verbose_name='Единица измерения',
        max_length=15
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.quantity}, {self.units}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=150
    )
    color = models.CharField(
        max_length=20,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=20,
        verbose_name='Короткий URL адрес для вашего тега',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=1000
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата публикации'
    )
