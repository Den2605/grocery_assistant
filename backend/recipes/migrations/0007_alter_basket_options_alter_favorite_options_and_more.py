# Generated by Django 4.2.4 on 2023-09-21 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_follow_unique_name_following'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basket',
            options={'ordering': ('user',), 'verbose_name': 'Корзина', 'verbose_name_plural': 'Список покупок'},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('user',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('user',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписчики'},
        ),
    ]