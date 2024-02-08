# Notes on running CPP in the conformance framework.

GHA:
1. Get a CPP binary, e.g.,
     https://github.com/unicode-org/icu/releases/download/release-73-2/icu4c-73_2-Ubuntu22.04-x64.tgz
    Note: Parameterize this with release, e.g.,
    MAJOR_RELEASE=73 MINOR_RELEASE=2

    wget https://github.com/unicode-org/icu/releases/download/release-$MAJOR_RELEASE-$MINOR_RELEASE/icu4c--$MAJOR_RELEASE_$MINOR_RELEASE-Ubuntu22.04-x64.tgz

2. gunzip the .tgz file
3. tar -xvz the .tar file        

    4. Set up PATH, LD_LIBRARY_PATH, include path

5. In the executors cpp directory, make with this ICU

6. Run the executor with command line parameters for ICU data versions.    
