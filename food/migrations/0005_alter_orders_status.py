# Generated by Django 4.1.7 on 2023-03-06 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_rename_dishes_dish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(choices=[('Aceepted', 'Accepted'), ('Rejected', 'Rejected'), ('Finished', 'Finished'), ('Delivered', 'Delivered')], default='Waiting', max_length=40),
        ),
    ]