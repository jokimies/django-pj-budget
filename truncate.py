#!/usr/bin/env python

import re
import sys

filepointer = open(sys.argv[1], "rw+")
line = filepointer.readline()
while line:
    if re.search("django-budget. \[P", line):
        filepointer.truncate()
    line = filepointer.readline()
