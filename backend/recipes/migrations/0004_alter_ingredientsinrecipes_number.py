# Generated by Django 4.2.4 on 2023-09-13 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredientsinrecipes_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipes',
            name='number',
            field=models.IntegerField(verbose_name='Количество'),
        ),
    ]
