# Generated by Django 3.2.3 on 2023-03-31 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_contactus_design'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='design',
            field=models.ImageField(default='', upload_to='media\\sample_design'),
        ),
    ]
