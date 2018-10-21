Changelog
=========


v2.3.2 (2018-10-21)
-------------------
- Bump version: 2.3.1 → 2.3.2. [Petri Jokimies]
- Fix features decprecated/removed in Django 1.10. [Petri Jokimies]
- Rename settings used with tests. [Petri Jokimies]



- Remove deprecation warning on urls. [Petri Jokimies]








- Update change log. [Petri Jokimies]


v2.3.1 (2016-12-11)
-------------------
- Bump version to 2.3.1. [Petri Jokimies]
- Execute date range filtering in Python. [Petri Jokimies]








v2.3.0 (2016-11-15)
-------------------
- Bump version to 2.3.0. [Petri Jokimies]
- Update for Django 1.9. [Petri Jokimies]
- Use local settings-test with py.test. [Petri Jokimies]





v2.2.2 (2015-12-20)
-------------------
- *montly summary*: Broken monthly summary fixed. [Petri Jokimies]








v2.2.1 (2015-12-19)
-------------------

Fix
~~~
- *dashboard*: Estimate has no repeast field. [Petri Jokimies]









v2.2.0 (2015-12-19)
-------------------

New features
~~~~~~~~~~~~
- *estimate setup*: Months used in estimate. [Petri Jokimies]







Other
~~~~~
- Version increase. [Petri Jokimies]
- *yearly summary*: Colorize Actual column. [Petri Jokimies]
- *yearly summary*: Limit number of decimals to two. [Petri Jokimies]


v2.1.2 (2015-12-14)
-------------------
- *yearly summary*: Corrected counting & display. [Petri Jokimies]








v2.1.1 (2015-09-22)
-------------------

Documentation
~~~~~~~~~~~~~
- Attempt to fix rst formatting on PyPi. [Petri Jokimies]

Other
~~~~~
- Change history for new version. [Petri Jokimies]


v2.1.0 (2015-09-22)
-------------------

New features
~~~~~~~~~~~~
- Python3 changes, added possibility to run tests with.pytest. [Petri
  Jokimies]
- *docs*: gitchangelog taken into use. [Petri Jokimies]

Refactor
~~~~~~~~
- *summary*: Yearly summary with details (#2) [Petri Jokimies]
- *views*: Moving logic away from views (#1) [Petri Jokimies]




Other
~~~~~
- New version. [Petri Jokimies]


v2.0.0 (2015-09-06)
-------------------
- Django-pj-budget: Initial import of all the changes made to original
  django-budget. [Petri Jokimies]
- Merge pull request #1 from mpeterson/master. [Daniel Lindsley]
- Added division by 0 handling to the Dashboard view. [mpeterson]
- Added 'es' locale. [mpeterson]
- Modified models for i18n. [mpeterson]


v1.0.3 (2010-05-24)
-------------------
- Fixed the ``Budget`` model to exclude deleted estimates. Thanks to
  brad for the patch. v1.0.3. [Daniel Lindsley]
- Added a ``.gitignore``. [Daniel Lindsley]
- Added README & some tweaks. [Daniel Lindsley]
- Added the sample templates to the repo. [Daniel Lindsley]
- Incremented version number and documented fixes. [Daniel Lindsley]
- Fixed end_date in dashboard view as well. [Daniel Lindsley]
- Merge branch 'master' of
  ssh://daniellindsley@lindsley.dyndns.org/Users/daniellindsley/git
  /django-budget. [Moriah]
- Merge branch 'master' of /Users/daniellindsley/git/django-budget.
  [Daniel Lindsley]
- Added much needed default timestamp on 'updated'. [Daniel Lindsley]
- Incremented version number and provided description of previous bug
  fix. [polarcowz]
- Added much needed default timestamp on 'updated'. [polarcowz]
- Updated documentation. [polarcowz]
- Merge branch 'master' of /Users/daniellindsley/git/django-budget.
  [polarcowz]
- Initial directory structure. [(no author)]
- A better (and correct) fix this time. [Moriah]
- Fixed error when the month is December. [Moriah]
- Added sorting to transactions. [Daniel Lindsley]
- Customized admins. [Daniel Lindsley]
- Excluded income transacations from adding to total. [Daniel Lindsley]
- Tweaks for colorize_amount. [Daniel Lindsley]
- Added colorize_amount tag for presentation purposes. [Daniel Lindsley]
- Renamed credit/debit to income/expense. [Daniel Lindsley]
- Added documentation to the views. [Daniel Lindsley]
- Added some documentation to transaction views. [Daniel Lindsley]
- Modularized the views for customization/extension. [Daniel Lindsley]
- Split the start_date for better data entry (and Javascript date
  pickers). [Daniel Lindsley]
- Reorganization complete. [Daniel Lindsley]
- Final commit before starting prep for open sourcing. [Daniel Lindsley]
- Summary functionality working. [Daniel Lindsley]
- More development on all fronts. Initial working GUI. [Daniel Lindsley]
- Budgets and estimates CRUD views complete and tested. [Daniel
  Lindsley]
- Spacing tweak. [Daniel Lindsley]
- Fixed various category bugs. [Daniel Lindsley]
- Transactions complete and (mostly) tested. [Daniel Lindsley]
- Categories complete and tested. [Daniel Lindsley]
- Various fixes to the main app. [Daniel Lindsley]
- Initial commit. Views, forms and tests need love. [Daniel Lindsley]


