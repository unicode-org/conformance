# Copyright (C) 2016 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# Copyright (c) 2000-2002 IBM, Inc. and others
# ICU conformance executor in C++

# Usage:
#  - configure, build, install ICU (make install)
#  - make sure "icu-config" (in the ICU installed bin directory) is on
#     the path
#  - do 'make' in this directory

#### definitions
# Name of your target
TARGET=executor

# All object files (C or C++)

OBJECTS=main.o coll.o datetime_fmt.o localedisplaynames.o likely_subtags.o list_fmt.o message_fmt2.o number_fmt.o plural_rules.o relativedatetime_fmt.o segmenter.o util.o

#### rules
# Load in standard makefile definitions
include defs.mk

# the actual rules (this is a simple sample)
include rules.mk
