import collections
from enum import Enum
import logging
import config



# Create a namedtuple type as the entries in a job registry
JobEntry = collections.namedtuple('JobEntry',
                                  'name config preprocess postprocess func')

class JobStatus(Enum):
    INVALID = -1
    PENDING=0
    EXECUTING=1
    SUCCESS=2
    FAILED=3


class InferencePipeline:
    '''Registers and executes inference jobs.

    A typical use case with the gaussian_blur3d function:

    >>> pipeline = InferencePipeline([])
    >>> job = JobEntry(name='3dblur', config={'sigma': 1.0},
    ....               preprocess=pre_gaussian_blur3d,
    ....               postprocess=post_gaussian_blur3d,
    ....               func=gaussian_blur3d)
    >>> pipeline.register(job)
    >>> pipeline.execute('3dblur', '/path/to/input/dicom/folder',
    ....                '/path/to/output/dicom/folder')
    '''

    def __init__(self, registry: list):
        '''Instantiate an InferencePipeline object with a list of jobs.

        Duplicated jobs (by name) will collide and only the last one will be
        kept. Others will be discarded without warning.

        :param registry: a list of JobEntry objects as the init job registry

        :return: a InferencePipeline object
        '''
        self.logger = logging.getLogger(config.APP_NAME)
        self.job_register = {}

        for job in registry:
            self.register(job)


    def register(self, job: JobEntry):
        '''Add a job into the registry.

        See __init__ for information of job name collision.

        :param job: A JobEntry object containing the job to be registered
        '''
        self.job_register[job.name] = {'job':job, 'status': JobStatus.PENDING}


    def unregister(self, job_name: str):
        '''Remove a job by name from the registry.

        An unfound job_name will raise a KeyError.

        :param job_name: the name of the job to be removed
        '''
        self.job_register.pop(job_name)

    def is_job_registered(self, job_name: str) -> bool:
        '''Check if a job_name is registered with the pipeline

        :param job_name: str, the unique name of the job
        :return: bool, if the job is registered
        '''
        return job_name in self.job_register

    def execute(self, job_name: str, in_dicom_dir: str, out_dicom_dir: str):
        '''Execute a job specified by job_name, with the in_dicom_dir
        (directory containing DICOM files) as input and out_dicom_dir as the
        output DICOM directory.

        :param job_name: a string, the job's unique name
        :param in_dicom_dir: a string, the path to the input DICOM folder
        :param out_dicom_dir: a string, the path to the output DICOM folder
        '''

        job_info = self.job_register[job_name]
        cur_job = job_info['job']
        job_info['status'] = JobStatus.EXECUTING
        job_info['output'] = out_dicom_dir
        try:
            preproc_out = cur_job.preprocess(in_dicom_dir, cur_job.config)
            proc_out = cur_job.func(*preproc_out)
            cur_job.postprocess(in_dicom_dir, out_dicom_dir, proc_out)
            job_info['status'] = JobStatus.SUCCESS
        except Exception as e:
            job_info['status'] = JobStatus.FAILED
            self.logger.exception('Job Execution Failed with error : %s', e)


    def find_job_by_output(self, out_dicom_dir):
        '''
        Find job with the associated output directory
        :param out_dicom_dir:
        :return:
        '''
        for job_name, job_info in self.job_register.items():
            if 'output' in job_info and job_info['output'] == out_dicom_dir:
                return job_info['status'], job_info['output']
        return JobStatus.INVALID, None