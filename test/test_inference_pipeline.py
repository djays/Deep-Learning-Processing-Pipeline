import unittest
from unittest.mock import MagicMock
import numpy as np
from inference_pipeline import InferencePipeline, JobEntry

class TestPipeline(unittest.TestCase):

    def test_register(self):
        pipe = InferencePipeline([])
        job_name = 'test_job'

        # Check if job was registered
        pipe.register(JobEntry(name=job_name, config={'sigma': 1.0}, preprocess = None, postprocess= None, func = None))
        self.assertTrue(pipe.is_job_registered(job_name))

        # Check if new job override the old one
        new_job = JobEntry(name=job_name, config={'sigma': 2.0}, preprocess = None, postprocess= None, func = None)
        pipe.register(new_job)
        self.assertEqual(pipe.job_register[job_name]['job'], new_job)

        # Check job unregister
        pipe.unregister(job_name)
        self.assertFalse(pipe.is_job_registered(job_name))

    def test_execution(self):
        pipe = InferencePipeline([])
        job_name = 'test_job'

        # Simple check that all processing methods were called.
        preproc_method = MagicMock()
        postproc_method = MagicMock()
        main_method = MagicMock()
        job = JobEntry(name=job_name, config={'sigma': 2.0}, preprocess=preproc_method, postprocess=postproc_method, func=main_method)

        pipe.register(job)
        pipe.execute(job_name, 'in-dir', 'out-dir')

        self.assertTrue(preproc_method.called)
        self.assertTrue(main_method.called)
        self.assertTrue(postproc_method.called)



if __name__ == '__main__':
    unittest.main()