# Generated by Django 4.2.4 on 2023-09-13 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_rename_ingredients_ingredientsinrecipes_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipes',
            name='number',
            field=models.IntegerField(max_length=16, verbose_name='Количество'),
        ),
    ]
