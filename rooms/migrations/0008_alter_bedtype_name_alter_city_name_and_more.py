import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0007_alter_room_amenities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bedtype',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='rooms.city'),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='room',
            name='amenities',
            field=models.ManyToManyField(blank=True, to='rooms.amenity'),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
