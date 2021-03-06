# Generated by Django 4.0 on 2022-02-10 20:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.BigIntegerField()),
                ('fee', models.BigIntegerField()),
                ('date', models.DateField()),
                ('done', models.BooleanField()),
                ('finishdate', models.DateField()),
                ('workers', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
