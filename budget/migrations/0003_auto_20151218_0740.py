# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20150904_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetestimate',
            name='occurring_month',
            field=multiselectfield.db.fields.MultiSelectField(default=b'1', choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], max_length=26, blank=True, null=True, verbose_name='Occuring month'),
        ),
    ]
