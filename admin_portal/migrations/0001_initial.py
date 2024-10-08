# Generated by Django 4.2.11 on 2024-07-02 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('title', models.CharField(max_length=100)),
                ('button_text', models.CharField(max_length=50)),
                ('button_url', models.URLField()),
            ],
        ),
    ]
