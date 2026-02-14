# Generated migration for venues app

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Venue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="active"),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="name"),
                ),
                (
                    "name_ru",
                    models.CharField(max_length=255, null=True, verbose_name="name"),
                ),
                (
                    "name_uz",
                    models.CharField(max_length=255, null=True, verbose_name="name"),
                ),
                (
                    "name_en",
                    models.CharField(max_length=255, null=True, verbose_name="name"),
                ),
                (
                    "address",
                    models.TextField(verbose_name="address"),
                ),
                (
                    "address_ru",
                    models.TextField(null=True, verbose_name="address"),
                ),
                (
                    "address_uz",
                    models.TextField(null=True, verbose_name="address"),
                ),
                (
                    "address_en",
                    models.TextField(null=True, verbose_name="address"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "description_ru",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
                (
                    "description_uz",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
                (
                    "description_en",
                    models.TextField(blank=True, null=True, verbose_name="description"),
                ),
                (
                    "price_per_hour",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Price in local currency per hour",
                        max_digits=10,
                        verbose_name="price per hour",
                    ),
                ),
                (
                    "images",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.URLField(max_length=500),
                        blank=True,
                        default=list,
                        help_text="List of image URLs",
                        size=None,
                        verbose_name="images",
                    ),
                ),
                (
                    "amenities",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        blank=True,
                        default=list,
                        help_text="List of amenities",
                        size=None,
                        verbose_name="amenities",
                    ),
                ),
            ],
            options={
                "verbose_name": "venue",
                "verbose_name_plural": "venues",
                "ordering": ["-created_at"],
            },
        ),
    ]
