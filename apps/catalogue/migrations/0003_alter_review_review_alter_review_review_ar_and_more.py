# Generated by Django 4.2 on 2024-08-22 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_remove_product_source_country_product_source_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review',
            field=models.TextField(blank=True, max_length=250, null=True, verbose_name='Review'),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_ar',
            field=models.TextField(blank=True, max_length=250, null=True, verbose_name='Review'),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_en',
            field=models.TextField(blank=True, max_length=250, null=True, verbose_name='Review'),
        ),
    ]