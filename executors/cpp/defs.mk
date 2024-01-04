# Copyright (C) 2016 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# Copyright (c) 2002-2012 IBM, Inc. and others
# Sample code makefile definitions 

CLEANFILES=*~ $(TARGET).out
####################################################################
# Load ICU information. You can copy this to other makefiles #######
####################################################################
CC=$(shell icu-config --detect-prefix --cc)
CXX=$(shell icu-config --detect-prefix --cxx)
CPPFLAGS=$(shell icu-config --detect-prefix --cppflags)
CFLAGS=$(shell icu-config --detect-prefix --cflags)
CXXFLAGS=$(shell icu-config --detect-prefix --cxxflags)
LDFLAGS =$^ $(shell icu-config --detect-prefix --ldflags)
LDFLAGS_USTDIO =$(shell icu-config --detect-prefix --ldflags-icuio)
INVOKE=$(shell icu-config --detect-prefix --invoke)
GENRB=$(shell icu-config --detect-prefix --invoke=genrb)
GENRBOPT=
PKGDATA=$(shell icu-config --detect-prefix --invoke=pkgdata)
SO=$(shell icu-config --detect-prefix --so)
PKGDATAOPTS=-r $(shell icu-config --detect-prefix --version --detect_version) -w -v -d .
# default - resources in same mode as ICU
RESMODE=$(shell icu-config --detect-prefix --icudata-mode)

CFLAGS += $(shell pkg-config --cflags json-c)
LDFLAGS += $(shell pkg-config --libs json-c)

####################################################################
### Project independent things (common) 
### We depend on gmake for the bulk of the work 

RMV=rm -rf
