from aiohttp import web
import uuid
from inference_pipeline import InferencePipeline, JobEntry, JobStatus
from gaussian_blur3d import pre_gaussian_blur3d, gaussian_blur3d, post_gaussian_blur3d
import logging
import config
import utils
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import string

routes = web.RouteTableDef()

def gen_uid(uid_len=5):
    """Generate a random UID of given length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(uid_len))

def execute_job(job_name, in_dir, uid):
    pipeline.execute(job_name, in_dir, config.WEB_OUTPUT_DIR + uid)

@routes.post('/job')
async def job(request):
    # Validate for request parameters
    # TODO: add logger info
    json = await request.json()

    if not json or not 'job_name' in json or not 'in_dir' in json:
        logger.info('BAD Request Recieved')
        return web.json_response({'msg': 'Bad Request: job_name or in_dir attributes not found'}, status=400)

    job_name = json['job_name']
    in_dir = json['in_dir']

    # Validate existence of job
    if not pipeline.is_job_registered(job_name):
        return web.json_response({'msg': 'Job Not Found: The supplied job_name isn\'t registered'}, status=422)

    # Validate Directory: on empty, non
    in_dir_path = Path(in_dir)
    if not in_dir_path.exists() or not utils.get_files(in_dir_path, config.DCM2HD5_INPUT_EXT):
        return web.json_response({'msg': 'The supplied in_dir doesn\'t contain a valid path to DICOMs'}, status=422)

    # Create UID and start job
    uid = gen_uid()
    event_loop.run_in_executor(pool, execute_job, job_name, in_dir, uid)


    return web.json_response({'uid': uid}, status=201)


@routes.get('/query/{job_uid}')
def query(request):
    uid = request.match_info.get('job_uid', None)

    if not uid:
        return web.json_response({'msg': 'Job uid required'}, status=400)

    status, output_dir = pipeline.find_job_by_output(config.WEB_OUTPUT_DIR + uid)

    if status == JobStatus.INVALID:
        return web.json_response({'msg': 'Job not found!'}, status=404)
    elif status == JobStatus.PENDING or status == JobStatus.EXECUTING:
        return web.json_response({'msg': 'Job is running'}, status=202)
    elif status == JobStatus.FAILED:
        return web.json_response({'msg': 'Job has failed! Contact admin!'}, status=500)

    return web.json_response({'msg': 'Job has completed', 'output_dir' : output_dir}, status=200)


async def init_app():
    app = web.Application(debug=True)
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    logger = logging.getLogger(config.APP_NAME)

    pipeline = InferencePipeline([])
    pipeline.register(JobEntry(name='3dblur', config={'sigma': 1.0}, preprocess=pre_gaussian_blur3d,
                               postprocess=post_gaussian_blur3d, func=gaussian_blur3d))
    pool = ThreadPoolExecutor(max_workers=2)
    event_loop = asyncio.get_event_loop()
    app = event_loop.run_until_complete(init_app())
    web.run_app(app)



