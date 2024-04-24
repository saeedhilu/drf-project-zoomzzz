# Generated by Django 5.0.4 on 2024-04-23 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0038_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='is_available',
        ),
        migrations.AddField(
            model_name='booking',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('CANCELED', 'Canceled')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='reservation_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELED', 'Canceled')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='total_guest',
            field=models.IntegerField(null=True),
        ),
    ]
