# Generated by Django 5.0.4 on 2024-04-17 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_remove_amenity_image_alter_amenity_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='amenity',
            name='image',
            field=models.ImageField(blank=True, upload_to='amenity_images/'),
        ),
    ]