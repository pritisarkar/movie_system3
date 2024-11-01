# Generated by Django 5.1.2 on 2024-10-29 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_genre'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('release_year', models.IntegerField()),
                ('genres', models.ManyToManyField(related_name='movies', to='app.genre')),
            ],
        ),
    ]
