from django.db import models


class Tags(models.Model):
    """Теги."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название тега",
    )
    color = models.CharField(max_length=16)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Тег",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название тега",
    )
    number = models.CharField(max_length=16)
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Рецепты."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название блюда",
    )
    # author = models.ForeignKey(
    #    User,
    #    on_delete=models.CASCADE,
    #    related_name="recepies",
    #    verbose_name="Пользователь",
    # )
    image = models.ImageField(upload_to="/images/", blank=False)
    text = models.CharField(max_length=255, verbose_name="Описание блюда")
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name="ingredients",
        blank=True,
        verbose_name="Тег",
    )
    tags = models.ManyToManyField(
        Tags,
        related_name="tags",
        blank=True,
        verbose_name="Тег",
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
