# Generated by Django 3.1.1 on 2020-10-15 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qmratool', '0007_auto_20201015_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exposure',
            name='reference',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='qmratool.reference'),
        ),
    ]