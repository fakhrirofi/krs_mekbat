# Generated by Django 5.0.1 on 2024-01-13 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('war', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='nim',
            field=models.IntegerField(default=112210, verbose_name='NIM'),
            preserve_default=False,
        ),
    ]
