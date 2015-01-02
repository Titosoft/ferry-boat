from __future__ import print_function
from celery import Celery, chain
from celery.task import current
from celery.utils.log import get_task_logger
from docker import Client
import json,docker,os, logging


logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.join('/var/log/ferry-btm/','tasks.log'))
formatter = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Celery('tasks', backend='amqp', broker='amqp://')
c = Client(base_url='unix://var/run/docker.sock')

@app.task
def pull(image,ignore_result=True):
    result=''
    logger.info('Pulling image %s, please wait...' %image)
    for line in c.pull(image,stream=True):
        result+=json.dumps(json.loads(line), indent=4)
    logger.info('Image %s downloaded.' %image)

@app.task(bind=True,ignore_result=True)
def start(self,container,binds,port_bindings,publish_all_ports):
    """ start(container=PARCIAL,binds={'/tmp': {'bind': '/tmp', 'ro': True}},port_bindings={'81': '81'},publish_all_ports=False) """
    logger.info('Starting container %s. Good luck!' %container)
    result=c.start(container=container,binds=binds,port_bindings=port_bindings,publish_all_ports=publish_all_ports)
    return container

@app.task(bind=True)
def create(self,image,command,name,ports,volumes,environment,hostname):
    """ create(name=testeubuntu,image=ubuntu,ports=[81],volumes=['/tmp'],environment={'TEST': 'ieie'},hostname=testeubuntu) """
    try:
        logger.info('Trying to create %s (%s)' %(name,image)) 
        container=c.create_container(image=image,name=name,command=command,environment=environment,ports=ports,volumes=volumes,hostname=hostname)
    except Exception as e:
        logger.error('Error creating %s (%s): %s' %(name,image,e.explanation))
        logger.warning('Retrying (%s) in 60 seconds for %s (%s)' %(current.request.retries,name,image))
        pull.delay(image)
        self.retry(exc=e,countdown=60)
    
    return container['Id']

@app.task(bind=True,ignore_result=True)
def create_start(self,image,command,name,ports,volumes,environment,hostname,binds,port_bindings,publish_all_ports):
    ret = chain(create.s(image,command,name,ports,volumes,environment,hostname), start.s(binds,port_bindings,publish_all_ports))(link_error=log_error.s())
    logger.info('Creating and starting: %s (%s)' %(name,image)) 
    return 'creating container'

@app.task
def log_error(task_id,ignore_result=True):
    result = app.AsyncResult(task_id)
    result.get(propagate=False)  # make sure result written.
    with open(os.path.join('/var/log/ferry-btm/', task_id+-'error.log'), 'a') as fh:
        print('--\n\n{0} {1} {2}'.format(
            task_id, result.result, result.traceback), file=fh)
