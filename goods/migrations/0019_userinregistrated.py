# Generated by Django 3.0.5 on 2020-06-19 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0018_auto_20200530_2157'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInRegistrated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('password', models.IntegerField(max_length=100, verbose_name='Пароль')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ['name'],
            },
        ),
    ]
