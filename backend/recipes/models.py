from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Модель для ингендиентов"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=15
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=150
    )
    color = models.CharField(
        max_length=16,
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


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
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
    text = models.CharField(
        verbose_name='Описание блюда',
        max_length=1000
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipe',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}, {self.text} '


class IngredientRecipe(models.Model):
    """Модель, которая вкладывает нужное кол-во ингредиента в рецепт"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique ingredient in recipe'
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для добавления рецепта(ингредиентов) в корзину"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепты в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'


class FavoriteRecipe(models.Model):
    """Модель для добавления ингредиента в избранное"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite '
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'
