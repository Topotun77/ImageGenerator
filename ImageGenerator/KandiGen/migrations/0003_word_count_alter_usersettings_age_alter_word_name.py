# Generated by Django 5.1.2 on 2024-10-10 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KandiGen', '0002_rename_user_id_usersettings_user_image_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='age',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='word',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]