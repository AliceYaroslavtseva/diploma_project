import base64
import os
import re

import webcolors
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User

"""Users."""


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'id'
        )

    def validate_username(self, value):
        if not re.fullmatch(r'^[\w.+-]+', value):
            raise serializers.ValidationError('Nickname должен'
                                              ' содержать буквы,'
                                              'цифры и символы .+-_')
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя "me"')
        return value


class UsersSerializer(UserSerializer):
    """Сериализатор информации о пользователе."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=object.id).exists()


class SubscribeSerializer(UserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        queryset = self.get_queryset(obj)
        return queryset.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = self.get_queryset(obj)
        if limit:
            queryset = queryset[:int(limit)]
        serializer = RecipeInfaSerializer(queryset, many=True, read_only=True)
        return serializer.data
        # return RecipeInfaSerializer(serializer.data, many=True).data

    def get_queryset(self, obj):
        if hasattr(obj, 'recipes'):
            return obj.recipes.all()
        else:
            return Recipe.objects.filter(author=obj)


"""Recipe."""


class Hex2NameColor(serializers.Field):
    """Сериализатор цвета в тегах."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор списка ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('name', 'id', 'measurement_unit')
      

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор списка тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug', 'id')


class IngredientAddSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта, валидация."""

    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientAddSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if not item:
                raise ValidationError({
                    'ingredients': 'Список пуст'
                })
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты должны быть уникальными'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0'
                })
            ingredients_list.append(ingredient)
        return value

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        validated_ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, validated_ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        validated_ingredients = validated_data.pop('ingredients')

        IngredientRecipe.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.create_ingredients(instance, validated_ingredients)

        return instance

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeGetSerializer(instance, context=context).data


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""

    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and FavoriteRecipe.objects.filter(user=self.context['request'].user,
                                        recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )    


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов, валидация."""

    class Meta:
        model = FavoriteRecipe
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен в список избранных'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeInfaSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок, валидация."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен в список продуктов'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeInfaSerializer(instance.recipe, context=context).data


class RecipeInfaSerializer(serializers.ModelSerializer):
    """Сериализатор информации о рецепте для списков."""

    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
