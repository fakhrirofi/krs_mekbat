# Generated by Django 5.0.1 on 2024-01-30 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('war', '0009_rename_open_date_session_open_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='group_number',
            field=models.IntegerField(default=0, verbose_name='Kelompok'),
            preserve_default=False,
        ),
    ]
