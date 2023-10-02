from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser as User


class Tag(models.Model):
    """Теги."""

    name = models.CharField(
        verbose_name="Название тега",
        max_length=256,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=16,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Тег",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=256,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=16,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ("name", "measurement_unit")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""

    name = models.CharField(
        verbose_name="Название блюда",
        max_length=256,
        blank=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name="recipes",
        verbose_name="Пользователь",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="data/images/",
        blank=False,
    )
    text = models.CharField(max_length=255, verbose_name="Описание блюда")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="IngredientInRecipe",
        verbose_name="Ингредиент",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        through="TagInRecipe",
        blank=False,
        verbose_name="Тег",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления блюда(мин)",
        validators=[MinValueValidator(1, message="Не менее 1")],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="follower",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Автор",
        related_name="follow",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_name_following"
            )
        ]


class TagInRecipe(models.Model):
    """Промежуточная модель Tags"""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tag_in",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="tag_in",
    )

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["tag", "recipe"], name="recipe_tag_unique"
            )
        ]


class IngredientInRecipe(models.Model):
    """Промежуточная модель Ingredients"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_in",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_in",
    )

    amount = models.PositiveIntegerField(
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="recipe_ingredient_unique",
            )
        ]


class Basket(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Корзина"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_name_basket_recipe"
            )
        ]


class Favorite(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="user_favorite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_favorite",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_name_favorite_recipe"
            )
        ]
