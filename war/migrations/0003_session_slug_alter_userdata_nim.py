# Generated by Django 5.0.1 on 2024-01-13 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('war', '0002_userdata_nim'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='slug',
            field=models.SlugField(default='sesi1mekbat', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userdata',
            name='nim',
            field=models.IntegerField(),
        ),
    ]
