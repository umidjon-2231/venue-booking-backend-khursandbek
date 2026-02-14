# Generated migration for bookings app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("venues", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
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
                    "booking_date",
                    models.DateField(verbose_name="booking date"),
                ),
                (
                    "start_time",
                    models.TimeField(verbose_name="start time"),
                ),
                (
                    "end_time",
                    models.TimeField(verbose_name="end time"),
                ),
                (
                    "total_price",
                    models.DecimalField(
                        decimal_places=2,
                        editable=False,
                        max_digits=10,
                        verbose_name="total price",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("confirmed", "Confirmed"),
                            ("cancelled", "Cancelled"),
                            ("completed", "Completed"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
                (
                    "venue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="venues.venue",
                        verbose_name="venue",
                    ),
                ),
            ],
            options={
                "verbose_name": "booking",
                "verbose_name_plural": "bookings",
                "ordering": ["-booking_date", "-start_time"],
            },
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=models.CheckConstraint(
                check=models.Q(("end_time__gt", models.F("start_time"))),
                name="end_time_after_start_time",
            ),
        ),
    ]
