# DL Pipeline Tools for Medical Imaging

Tools for Medical Imaging 
Implemented using Python 3.5, Aiohttp and Numpy.
 

## Design : Web Backend 
The web backend runs on ```aiohttp``` for serving web requests. It's integrated with 
```asyncio``` event loop and a threadpool for the inference pipeline that allows us to start a job without 
blocking the request (due to job execution). The threadpool size can be changed to manage the number of 
concurrent jobs required to execute.

To simplify implementation, an ASCII UID is generated and also used as output directory. 


## Design : Gaussian Kernel
The pre, post and processing steps for the mock Gaussian task are implemented in gaussian_blur3d.py.
For computing 3D blur, a 1d convolution is computing for each dimension using a 1d gaussian kernel.
The algorithms creates the gaussian kernels with sigma for each dimension based on pixel spacing of the dimension.

The convolution operates on padded input help maintain original shape.   

## Design: Inference Pipeline
A dictionary is used to track the job and its current execution state as 
```
{
 'job': JobEntry,
 'status': JobStatus,
 'output': str # Output Dir 
}   
```
While this allows for only one execution of a job at a time (due to time constraint), it can be  
easily extended to track a dictionary of UID to state per job.   

## Installation

1. Install Python3.5+ 

2. Install remaining dependencies using
```
pip install -r requirements.txt
```


## Running the script interface
1. Merging and Converting DICOMs to HD5 and JSON.

```
python dicom_to_hd5.py -i :DICOM DIR -h :Path to Output HDF5 -j :Path to Output JSON
```

2. Extracting Pixel data from HD5 to dicoms.

```
python hd5_to_dicom.py -h :DICOM DIR -h :Path to input HDF5 -d :Path to template DICOM -o :Path to output DICOM
```

## Running the web backend
```
python web.py
```
By default, this launches a server on localhost port 8080
Supports 2 resources: e.g.
1. ```POST http://localhost:8080/job/```
Accepts JSON input, similar to :
```
{
  "job_name": "3dblur",
  "in_dir": "dicom_data"
}
```
Successful Response:
```HTTP 201```
```
{
"uid": "sfkbn"
}
```


2. ```GET http://localhost:8080/query/<job_uid>```


Successful Response while running:
```HTTP 202```
```
{
"msg": "Job is running"
}
```

Successful Response when done:
```HTTP 200```
```
{
"msg": "Job has completed", "output_dir": "web-outlxnge"
}
```



## Code Structure
  The code is designed to be extremely modular and re-usable, while following the Python paradigm KISS. 
  e.g. The web and script interfaces call the same code for dicom to hd5, while also avoiding 
  unessary disk write for the web interface. 

  dicom_to_hd5.py -- Houses the logic for generating HDF5 and JSON from DICOM.
  Also offers a command line interface as expected.
  
  hd5_to_dicom.py -- Houses the logic for generating DICOMs from HDF5 and templates.
  Also offers a command line interface as expected.
  
  utils.py -- Common utility functions 
  
  inference_pipeline.py  -- The inference pipeline
  
  web.py -- Web backend for invoking the pipeline
  
  config.py -- Basic configuration settings and constants. 
 
  test -- Package housing test cases. 

## Debug
By default, execution logs are stored in the current directory in debug.log

## Unit Tests

Tests are located in the test directory, while not complete, do allow for building upon 
and adding new test cases
e.g. For testing the basic functionality of the interface pipeline

```
 python -m unittest test.test_inference_pipeline
```

