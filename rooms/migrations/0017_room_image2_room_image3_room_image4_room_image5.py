# Generated by Django 4.2.11 on 2024-06-26 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0016_alter_country_name_alter_location_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='image2',
            field=models.ImageField(default='https://example.com/default_image.jpg', upload_to='room_images/'),
        ),
        migrations.AddField(
            model_name='room',
            name='image3',
            field=models.ImageField(default='https://example.com/default_image.jpg', upload_to='room_images/'),
        ),
        migrations.AddField(
            model_name='room',
            name='image4',
            field=models.ImageField(blank=True, default='https://example.com/default_image.jpg', null=True, upload_to='room_images/'),
        ),
        migrations.AddField(
            model_name='room',
            name='image5',
            field=models.ImageField(blank=True, default='https://example.com/default_image.jpg', null=True, upload_to='room_images/'),
        ),
    ]
