# Generated by Django 5.0 on 2023-12-11 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='delivery_crew',
            new_name='delivery_user',
        ),
    ]