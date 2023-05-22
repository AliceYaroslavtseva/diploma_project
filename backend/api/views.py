from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import LimitPagination
from api.permissions import AuthorReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipeInfaSerializer, RecipeSerializer,
                             SubscribeSerializer, TagSerializer,
                             UsersSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class UsersViewSet(UserViewSet):
    """Вьюсет для создания/удаления подписки."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(author,
                                             context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_serializer_context(self):
        if (self.request.path == '/api/users/' and 
            self.request.method == 'POST'):
            return
        context = super().get_serializer_context()
        subscriptions = Subscribe.objects.filter(
            user=self.request.user
        ).values_list('author_id', flat=True)
        context['subscriptions'] = set(subscriptions)
        return context

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = SubscribeSerializer(pages,
                                             many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(queryset,
                                         many=True,
                                         context={'request': request})
        print(serializer.data)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиетов."""

    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания/удаления рецептов, избранных и корзины."""

    queryset = Recipe.objects.all()
    permission_classes = [AuthorReadOnly]
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def valid_create(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeInfaSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.valid_create(FavoriteRecipe, request.user, pk)

        return self.delete_from(FavoriteRecipe, request.user, pk)

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.valid_create(ShoppingCart, request.user, pk)

        return self.delete_from(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
