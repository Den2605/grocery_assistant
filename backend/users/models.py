from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

username_validator = RegexValidator(
    regex=r"^[\w.@+-]+$",
    message=(
        "Имя пользователя должно состоять из буквенно-цифровых символов, "
        'а также знаков ".", "@", "+", "-" и не содержать других символов.'
    ),
)


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        unique=True,
        blank=False,
        max_length=254,
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        unique=True,
        blank=False,
        max_length=150,
        validators=[username_validator],
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=False,
    )
    password = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
