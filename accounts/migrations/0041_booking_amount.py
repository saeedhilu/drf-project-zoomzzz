# Generated by Django 5.0.4 on 2024-04-23 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0040_alter_booking_total_guest'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]