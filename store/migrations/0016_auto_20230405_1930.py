# Generated by Django 3.2.3 on 2023-04-05 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_order_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name': 'User Address Detail', 'verbose_name_plural': 'User Address Detail'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('-created_at',), 'verbose_name_plural': 'Product Categories'},
        ),
        migrations.AlterModelOptions(
            name='contactus',
            options={'verbose_name': 'Contact Us Manage', 'verbose_name_plural': 'Contact Us Manage'},
        ),
        migrations.AlterModelOptions(
            name='otp_data',
            options={'verbose_name': 'OTP Manage', 'verbose_name_plural': 'OTP Manage'},
        ),
        migrations.AlterModelOptions(
            name='wishlist',
            options={'verbose_name': 'Wishlist Products', 'verbose_name_plural': 'Wishlist Products'},
        ),
        migrations.AlterField(
            model_name='contactus',
            name='design',
            field=models.ImageField(blank=True, null=True, upload_to='custom_design', verbose_name='Custom design'),
        ),
    ]