# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0003_auto_20151218_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetestimate',
            name='occurring_month',
            field=multiselectfield.db.fields.MultiSelectField(default='1', max_length=26, verbose_name='Occuring month', choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]),
        ),
    ]
