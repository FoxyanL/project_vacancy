# Generated by Django 5.1.7 on 2025-03-19 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='Ожидает рассмотрения', max_length=50)),
                ('message', models.TextField()),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'На рассмотрении'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')], default='pending', max_length=20)),
            ],
        ),
    ]
