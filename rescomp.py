import uuid
from typing import Optional

from IPython.core.magic import (register_cell_magic)
from mako.template import Template

import re, os
from typing import Optional
from collections import namedtuple
import warnings

if os.path.exists('sge.mako'):
    with open('sge.mako', 'r') as fh:
        template = fh.read()
else:
    warnings.warn('No sge.mako found, please fill rescomp.template')
    template = ''

def uuid_jobname(jobname: Optional[str] = None) -> str:
    """
    Generate a jobname if none is provided. with a uuid (utteroverkill)
    :param jobname:
    :return:
    """
    if jobname is None:
        return str(uuid.uuid4().fields[0])
    jobname = str(jobname).strip()
    if not jobname:  # '' will crash the run...
        return '_'
    else:
        return jobname


def rescomp_submit(py_filename: str, py_args: str = '',
                   jobname: Optional[str] = None,
                   cores: int = 1,
                   queue: str = 'short.qc'):
    jobname = uuid_jobname(jobname)
    makoed = Template(template).render(jobname=jobname,
                                       cores=cores,
                                       queue=queue,
                                       py_filename=py_filename,
                                       py_args=py_args
                                       )
    with open(f'temp_{jobname}.sh', 'w') as fh:
        fh.write(makoed)
    import subprocess
    p = subprocess.Popen(["qsub", f'temp_{jobname}.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read().decode()
    err = p.stderr.read().decode()
    if err:
        raise RuntimeError(err)
    job_id = int(re.search('job (\d+)', out).group(1))
    return out


@register_cell_magic
def rescomp(line: str, cell: str) -> str:
    """
    Returns job id
    https://www.medsci.ox.ac.uk/divisional-services/support-services-1/bmrc/cluster-usage
    
    %%rescomp jobname=test queue=test.qc cores=1
    """

    def extact(rex_line, alt):
        rex = re.search(rex_line, line)
        if rex:
            return rex.group(1).strip()
        return alt

    jobname = uuid_jobname(extact(r'jobname=(\S*)', None))
    queue = extact(r'queue=(\S*)', None)
    cores = extact(r'cores=(\d+)', 1)
    py_filename = f'temp_{jobname}.py'
    with open(py_filename, 'w') as fh:
        fh.write(cell)
    return rescomp_submit(py_filename,
                          py_args='',
                          jobname=jobname,
                          cores=cores,
                          queue=queue)

    # print(', '.join(re.findall(r'\$\{(.*?)}', template)))

del rescomp

# -----------------------------------------------------------------------------

Job = namedtuple('Job', ['id', 'name'])


def get_last_job_id() -> Job:
    """Jupyter only... The global ``_oh`` won't exist otherwise"""
    for o in reversed(_oh.values()):
        if not isinstance(o, str):
            continue
        rex = re.match('Your job (\d+) \("(.*)"\) has been submitted', o)
        if rex:
            # job_name
            return Job(id=int(rex.group(1)), name=rex.group(2))

    else:
        raise ValueError('No jobs found in cell outputs... did the kernel runtime reset?')


def get_job_log(job: Optional[Job] = None) -> str:
    """Given a job namedtuple (or guess it), return the job log"""
    if job is None:
        job = get_last_job_id()
    log_filename = f'{job.name}.o{job.id}'
    if os.path.exists(log_filename):
        with open(log_filename) as fh:
            return fh.read()

#cat /gpfs0/mgmt/modules/Modules/default/init/python.py
import os, re, subprocess

if os.environ.get('MODULE_VERSION', None) is None:
    os.environ['MODULE_VERSION_STACK'] = '3.2.10'
    os.environ['MODULE_VERSION'] = '3.2.10'
else:
    os.environ['MODULE_VERSION_STACK'] = os.environ['MODULE_VERSION']
os.environ['MODULESHOME'] = '/gpfs0/mgmt/modules/Modules/3.2.10'

if os.environ.get('MODULEPATH', None) is None:
    f = open(os.environ['MODULESHOME'] + "/init/.modulespath", "r")
    path = []
    for line in f.readlines():
        line = re.sub("#.*$", '', line)
        if line != '':
            path.append(line)
    os.environ['MODULEPATH'] = ':'.join(path)

if os.environ.get('LOADEDMODULES', None) is None:
    os.environ['LOADEDMODULES'] = ''

def module(*args):
    """
    Load a module, like ``module('load', 'CUDA')``.
    This is because doing ``os.system('module load CUDA')`` does not work.
    From /gpfs0/mgmt/modules/Modules/default/init/python.py
    made Py 3.6 compatible.


    :param args: 'load', 'modulename' generally!
    :return:
    """
    if isinstance(args[0], list):
        args = args[0]
    else:
        args = list(args)
    (output, error) = subprocess.Popen(['/gpfs0/mgmt/modules/Modules/%s/bin/modulecmd'
                                        % os.environ['MODULE_VERSION'], 'python'] +
        args, stdout=subprocess.PIPE).communicate()
    exec(output)





