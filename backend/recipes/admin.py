from django.contrib.admin import ModelAdmin, register

from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug', 'id')


@register(Recipe)
class RecipeAdmin(ModelAdmin):

    def tags(self, user):
        tag = []
        for tags in user.tag.all():
            tag.append(tags.name)
        return ' '.join(tag)
    tags.short_description = 'Tag'

    list_display = ('name', 'author', 'tags')
    search_fields = ('name',)


@register(IngredientRecipe)
class IngredientRecipeAdmin(ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'id')


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    list_display = ('recipe', 'user')


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('recipe', 'user')
