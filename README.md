# DL Pipeline Tools for Medical Imaging

Tools for Medical Imaging 
Implemented using Python 3.5
Since 

## Installation

1. Install Python3.5+ 

2. Install remaining dependencies using
```
pip install -r requirements.txt
```

## Running the code
1. Merging and Converting DICOMs to HD5 and JSON.

```
python dicom_to_hd5.py -i <DICOM DIR> -h <Path to Output HDF5> -j <Path to Output JSON>
```

## Debug
By default, execution logs are stored in the current directory in debug.log

## Unit Tests

Tests are located in the test directory, while not complete, do allow for building upon 
and adding new test cases
e.g.


## Code Structure
  script.py -- Main execution file 
 
  config.py -- Basic configuration constants such as maxmimum number of faces, minimum face size. 
 
  test -- Package housing test cases. 
