# testgen - Test Data Generators

Test data generation is about converting test data from its original form into JSON conforming to a schema that we design for that functionality component.

The process of test data generation (for a particular component of functionality) entails:

1. Finding the original source test data
2. Creating a JSON schema that is appropriate for the particular functionality component
3. Creating code to convert the original format to the new JSON format to be used by DDT

## Usage

Generate all test data:
```sh
python testdata_gen.py
```

Generate a subset of test data:
```sh
python testdata_gen.py --icu_versions=icu75 --test_types=message_fmt2
```

Show all options:
```sh
python testdata_gen.py --help
```

## Prerequisites

For some components, obtaining the original source test data requires manual work.
The following document some of those manual steps required:

### Locale Display Names (aka lang_names)

The code to generate locale display names test data was
[merged into CLDR after CLDR v45](https://github.com/unicode-org/cldr/pull/3728).

In order to retroactively apply the test generator code to older versions of CLDR,
the following steps can be employed for a specific version of CLDR:

1. checkout snapshot of old CLDR version
    ```
    git co release-43 -b release-43-localedisplay-datagen
    ```
2. pull backwards the current desired version of the test data generator
    ```
    git checkout main -- tools/cldr-code/src/main/java/org/unicode/cldr/tool/GenerateLocaleIDTestData.java
    ```
3. compile and run the generator from the right spot
    ```
    pushd tools/cldr-code
    mvn compile exec:java -DCLDR_DIR=/usr/local/google/home/elango/oss/cldr/mine/src -Dexec.mainClass=org.unicode.cldr.tool.GenerateLocaleIDTestData
    popd
    ```
4. copy the generated test data file to the Conformance repo
    ```
    cp ./common/testData/localeIdentifiers/localeDisplayName.txt ~/oss/conformance/testgen/icu73
    ```

### DateTime (aka datetime_fmt)


In order to retroactively apply the test generator code to older versions of CLDR,
the following steps can be employed for a specific version of CLDR:

1. checkout snapshot of old CLDR version
    ```
    git co release-46 -b release-46-datetime-datagen
    ```
2. pull backwards the current desired version of the test data generator
    ```
    git checkout main -- tools/cldr-code/src/main/java/org/unicode/cldr/tool/GenerateLocaleIDTestData.java
    ```
3. compile and run the generator from the right spot
    ```
    pushd tools/cldr-code
    mvn compile exec:java -DCLDR_DIR=/usr/local/google/home/elango/oss/cldr/mine/src -Dexec.mainClass=org.unicode.cldr.tool.enerateDateTimeTestData
    popd
    ```
4. copy the generated test data file to the Conformance repo
    ```
    cp ./common/testData/datetime/datetime.json ~/oss/conformance/testgen/icu76
    ```

