# Generated by Django 5.1.7 on 2025-03-25 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='direccion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
