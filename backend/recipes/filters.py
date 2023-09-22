from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name="author__id")
    tags = filters.CharFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="is_favorite")
    is_in_shopping_cart = filters.BooleanFilter(method="shopping_cart")

    class Meta:
        model = Recipe
        fields = [
            "author",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        ]

    def is_favorite(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe_favorite__user=user)
        return queryset

    def shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe__user=user)
        return queryset
