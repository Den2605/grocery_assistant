# Generated by Django 4.2.4 on 2023-09-13 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientsinrecipes',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]
