# Data sets for data driven testing and
# version info for executors vs. ICU/CLDR

# Started 06-Sept-2022

from collections import defaultdict
from enum import Enum

import sys

# Describes dataset and its versions.
class DataSet():
  def __init__(self, test_type, testDataFilename, verifyFilename,
               versionCLDR, versionICU):
    self.test_type = test_type
    self.testDataFilename = testDataFilename
    self.verifyFilename = verifyFilename
    self.cldr_version = versionCLDR
    self.icu_version = versionICU

    self.status = None
    self.debug = False


def dataSetsForCldr(dataSets, cldr_version):
    # get all those datasets for a given CLDR version
    dataMatches = []
    for testSet in dataSets:
      ds = dataSets[testSet]
      if ds.cldr_version == cldr_version:
        dataMatches.append(testSet)
    return dataMatches


# The ICU and CLDR versions should be largely in sync. More than one
# ICU version will use same CLDR version.
class ICUVersion(Enum):
  ICU67 = "67.1"
  ICU70 = "70.1"
  ICU71 = "71.1"
  ICU72rc = "72rc"
  ICU72 = "72.1"
  ICU73 = "73"

# TODO: Consider adding a trunk version for testing ICU / CLDR before
# a complete release.

def latestIcuVersion():
  return ICUVersion.ICU73

# TODO: consider how to handle trunk version vs "LATEST"
# e.g., use wget on file uvernum.h, looking up #define U_ICU_VERSION
def resolveIcu(text):
  if not text or text == 'LATEST':
    return latestIcuVersion()
  else:
    return text

class CLDRVersion(Enum):
  CLDR39 = "39"
  CLDR40 = "40"
  CLDR41 = "41"
  CLDR42 = "42"
  CLDR43 = "43"

def latestCldrVersion():
  return CLDRVersion.CLDR41  # TODO: Fix this

def resolveCldr(text):
  if not text or text == 'LATEST':
    return latestCldrVersion()
  else:
    return text

# Which ICU versions use each CLDR version.
# TODO: finish this map for recent CLDR
cldr_icu_map = {
    CLDRVersion.CLDR40: [ICUVersion.ICU70, ICUVersion.ICU71],
    CLDRVersion.CLDR41: [ICUVersion.ICU71],
    CLDRVersion.CLDR42: [ICUVersion.ICU72],
    CLDRVersion.CLDR43: [ICUVersion.ICU73],
}

# TODO: Can this be added to a configuration file?
class testType(Enum):
  coll_shift = 'coll_shift_short'
  decimal_fmt = 'decimal_fmt'
  datetime_fmt = 'datetime_fmt'
  display_names = 'display_names'
  lang_names = 'lang_names'
  number_fmt = 'number_fmt'

# Returns default value for a key not defined.
def def_value():
  return "Not present"

# Initialize dictionary of data organized by test type
testDatasets = defaultdict(def_value)

testName = 'coll_shift_short'
testDatasets[testName] = DataSet(testType.coll_shift.value,
                                 'coll_test_shift.json',
                                 'coll_verify_shift.json',
                                 CLDRVersion.CLDR41, ICUVersion.ICU71)

testName = 'coll_shift_67'
testDatasets[testName] = DataSet(testType.coll_shift.value,
                                 'coll_test0816_U67.json',
                                 None,
                                 CLDRVersion.CLDR39, ICUVersion.ICU67)

testName = 'decimal_fmt'
testDatasets[testName] = DataSet(testType.decimal_fmt.value,
                                 'dcml_fmt_test_file.json',
                                 'dcml_fmt_verify.json',
                                 CLDRVersion.CLDR41, ICUVersion.ICU71)

testName = 'display_names'
testDatasets[testName] = DataSet(testType.display_names.value,
                                 'display_names.json',
                                 'display_names_verify.json',
                                 CLDRVersion.CLDR41, ICUVersion.ICU71)

testName = 'lang_names'
testDatasets[testName] = DataSet(testType.lang_names.value,
                                 'lang_name_test_file.json',
                                 'lang_name_verify_file.json',
                                 CLDRVersion.CLDR41, ICUVersion.ICU71)

testName = 'number_fmt'
testDatasets[testName] = DataSet(testType.number_fmt.value,
                                 'num_fmt_test_file.json',
                                 'num_fmt_verify_file.json',
                                 CLDRVersion.CLDR41, ICUVersion.ICU71)

# Standard executor languages. Note that the ExecutorInfo
# class below can take any string as a "system".
class ExecutorLang(Enum):
  NODE = "node"
  RUST = "rust"
  CPP = "cpp"
  JAVA = "java"
  DARTWEB = "dart_web"
  DARTNATIVE = "dart_native"

# Actual commmands to run the executors.
ExecutorCommands = {
    "node" : "node ../executors/node/executor.js",
    "rust" : "executors/rust/target/release/executor",
    "cpp":   "executors/cpp/executor",
    "dart_web" : "node ../executors/dart_web/out/executor.js",
    "dart_native" : "executors/dart_native/bin/executor.exe",
    "java" : None
    };

class ParallelMode(Enum):
  Serial = 0
  ParallelInLang = 1
  ParallelByLang = 2

class NodeVersion(Enum):
  Node19 = "19.7.0"
  Node18_7 = "18.7.0"
  Node16 = "17.9.1"

class DartVersion(Enum):
  Dart3 = "3.1.0-39.0.dev"

class RustVersion(Enum):
  Rust01 = "0.1"
  Rust1 = "1.0"

class CppVersion(Enum):
  Cpp = "1.0"

class ICU4XVersion(Enum):
  ICU4XV1 = "1.0"

# Versions for known executors
# TODO: combine the version info
IcuVersionToExecutorMap = {
    'node': {
        '73': ["20.1.0"],
        '72': ['18.14.2'],
        '71': ['18.7.0', '16.19.1'],
        '70': ['14.21.3']
    },
    'icu4x': {
        '71': ['1.61.0'],
    },
    'dart': {},
    'icu4c': {},
    'icu4j': {},

}
# What versions of NodeJS use specific ICU versions
# https://nodejs.org/en/download/releases/
NodeICUVersionMap = {
    "20.1.0": "73.1",
    "18.14.2": "72.1",
    "18.7.0": "71.1",
    "16.19.1": "71.1",
    "14.21.3": "70.1",
    }

# Versions of ICU in each ICU4X release
ICU4XVersionMap = {
    # TODO: fill this in
    "1.0": '71.1',
    "1.61.0": '71.1'
}

ICUVersionMap = {
    'node': NodeICUVersionMap,
    'icu4x': ICU4XVersionMap,
    'rust': ICU4XVersionMap,
    'dart_web': NodeICUVersionMap,
    }

# Executor programs organized by langs and version
class ExecutorInfo():
  def __init__(self):
    self.systems = {}
    self.debug = False

  # Add or modify an entry.
  def addSystem(self, lang, systemVersion, systemPath,
                versionCLDR, versionICU, argList=None, env=None):
    if lang not in self.systems:
      # Add new item
      entry = self.systems[lang] = defaultdict(def_value)
    else:
      entry = self.systems[lang]

    entry[systemVersion] = {'path': systemPath,
                            'argList': argList,
                            'cldr': versionCLDR,
                            'icu': versionICU,
                            'env': env
                            }

  def pathForVersion(self, lang, sys_version):
    try:
      return self.systems[lang][sys_version]['path']
    except:
      return None

  def versionForCldr(self, lang, cldr_needed):
    try:
      # TODO: Add option for ANY or latest available
      system = self.systems[lang]
      for version in system:
        if system[version]['cldr'] == cldr_needed:
          return system[version]
      return {'path': lang}  # Nothing found
    except KeyError as err:
      print('versionForCldr error = %s' % err)
      return {'path': lang}  # Nothing found

  def has(self, exec) :
    if self.debug:
      print('HAS %s in %s' % (exec, (self.systems.keys())))
    try:
      return exec in self.systems
    except KeyError:
      return False

# Execution environments and versions for matching with data
allExecutors = ExecutorInfo()

system = ExecutorLang.NODE.value
allExecutors.addSystem(system, NodeVersion.Node19,
                       'node ../executors/node/executor.js',
                       CLDRVersion.CLDR42, versionICU=ICUVersion.ICU71)

allExecutors.addSystem(system, NodeVersion.Node18_7,
                       'node ../executors/node/executor.js',
                       CLDRVersion.CLDR41, versionICU=ICUVersion.ICU71)

system = ExecutorLang.RUST.value
allExecutors.addSystem(system, RustVersion.Rust01,
                       '../executors/rust/target/release/executor',
                       CLDRVersion.CLDR41, versionICU=ICUVersion.ICU71)

system = ExecutorLang.RUST.value
allExecutors.addSystem(system, RustVersion.Rust1,
                       '../executors/rust/target/release/executor',
                       CLDRVersion.CLDR41, versionICU=ICUVersion.ICU71)

system = ExecutorLang.CPP.value
allExecutors.addSystem(
    system, CppVersion.Cpp,
    '../executors/cpp/executor',
    CLDRVersion.CLDR43, versionICU=ICUVersion.ICU73,
    env={'LD_LIBRARY_PATH': '/tmp/icu73/lib', 'PATH': '/tmp/icu73/bin'})

system = "newLanguage"
allExecutors.addSystem(system, '0.1.0',
                       '/bin/newExecutor',
                       CLDRVersion.CLDR41, versionICU=ICUVersion.ICU71,
                       argList=['argA', 'argB', 'argZ'])

system = ExecutorLang.JAVA

system = ExecutorLang.DARTWEB.value
allExecutors.addSystem(system,  NodeVersion.Node19,
                       'node ../executors/dart_web/out/executor.js',
                       CLDRVersion.CLDR42, versionICU=ICUVersion.ICU71)

allExecutors.addSystem(system, NodeVersion.Node18_7,
                       'node ../executors/dart_web/out/executor.js',
                       CLDRVersion.CLDR41, versionICU=ICUVersion.ICU71)
                       
system = ExecutorLang.DARTNATIVE.value
allExecutors.addSystem(system, DartVersion.Dart3,
                       '../executors/dart_native/bin/executor.exe',
                       CLDRVersion.CLDR42, versionICU=ICUVersion.ICU71)

# TESTING
def printExecutors(executors):
  print('Executor paths:')
  for lang in executors.systems:
    ex = executors.systems[lang]
    print('   %s' % (lang))
    for key in ex.keys():
      print('     %s: %s' % (key, ex[key]['path']))

def printDatasets(ds):
  print('Defined datasets:')
  for item in ds:
    print('  %s:' % (item))
    print('    type: %s' % ds[item].test_type)
    print('    test filename: %s' % ds[item].testDataFilename)
    print('    verify filename: %s' % ds[item].verifyFilename)
    print('    CLDR version: %s' % ds[item].cldr_version)
    print('    ICU version: %s' % ds[item].icu_version)

def printCldrIcuMap():
  print('CLDR version maps')
  for name, member in CLDRVersion.__members__.items():
    try:
      print('  %s in %s' % (name, cldr_icu_map[member]))
    except KeyError:
      print('  %s not in map' % (name))

def main(args):

  printCldrIcuMap()
  print()
  printDatasets(testDatasets)
  print()
  printExecutors(allExecutors)

  print()
  cldr_version = CLDRVersion.CLDR41
  ds = dataSetsForCldr(testDatasets, cldr_version)
  print('test datasets for %s:' % cldr_version)
  for label in ds:
    print('  data file = %s' % (testDatasets[label].testDataFilename))

  print()
  print('All paths for testing %s' % (cldr_version))
  lang = ExecutorLang.NODE
  for lang in [ExecutorLang.NODE, ExecutorLang.RUST, ExecutorLang.CPP,
               'newLanguage']:
    exec = allExecutors.versionsForCldr(lang, cldr_version)
    print('  executor: %s' % (lang))
    if exec:
      print('    path: %s argList=%s' % (exec['path'], exec['argList']))
    else:
      print('    ** No defined path')

if __name__ == "__main__":
    main(sys.argv)
