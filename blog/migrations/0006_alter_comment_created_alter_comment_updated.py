# Generated by Django 5.1.3 on 2025-03-01 13:59

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_ticket_email_alter_ticket_massage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='updated',
            field=django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ بروز رسانی'),
        ),
    ]
