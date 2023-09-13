from django.db import models
from users.models import CustomUser as User


class Tags(models.Model):
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


class Ingredients(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=256,
    )
    number = models.CharField(
        verbose_name="Количество",
        max_length=16,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=16,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipes(models.Model):
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
        related_name="recipes_user",
        verbose_name="Пользователь",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="data/images/",
        blank=False,
    )
    text = models.CharField(max_length=255, verbose_name="Описание блюда")
    # ingredients = models.ManyToManyField(
    #    Ingredients,
    #    related_name="recipes_ingredients",
    #    # through=
    #    blank=False,
    #    verbose_name="Тег",
    # )
    tags = models.ManyToManyField(
        Tags,
        # on_delete=models.CASCADE,
        # related_name="recipes_tags",
        through="TagsInRecipes",
        blank=False,
        # verbose_name="Тег",
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления блюда"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ("pub_date",)
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
    is_subscribed = models.BooleanField(default=False)

    # class Meta:
    #    constraints = [
    #        models.UniqueConstraint(
    #            fields=["user", "following"], name="unique_name_following"
    #        )
    #    ]


class TagsInRecipes(models.Model):
    """Промежуточная модель Tags"""

    tag = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
    )
