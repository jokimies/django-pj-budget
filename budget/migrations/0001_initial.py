# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Created')),
                ('updated', models.DateTimeField(default=datetime.datetime.now, verbose_name='Updated')),
                ('is_deleted', models.BooleanField(default=False, db_index=True, verbose_name='Is deleted')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('start_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Start Date', db_index=True)),
            ],
            options={
                'verbose_name': 'Budget',
                'verbose_name_plural': 'Budgets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BudgetEstimate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='Created')),
                ('updated', models.DateTimeField(default=datetime.datetime.now, verbose_name='Updated')),
                ('is_deleted', models.BooleanField(default=False, db_index=True, verbose_name='Is deleted')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=11, decimal_places=2)),
                ('repeat', models.CharField(blank=True, max_length=15, verbose_name='Repeat', choices=[(b'BIWEEKLY', 'Every 2 Weeks'), (b'MONTHLY', 'Every Month')])),
                ('occurring_month', models.IntegerField(blank=True, max_length=3, null=True, verbose_name='Occuring month', choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('budget', models.ForeignKey(related_name='estimates', verbose_name='Budget', to='budget.Budget')),
                ('category', models.ForeignKey(related_name='estimates', verbose_name='Category', to='categories.Category')),
            ],
            options={
                'verbose_name': 'Budget estimate',
                'verbose_name_plural': 'Budget estimates',
            },
            bases=(models.Model,),
        ),
    ]
