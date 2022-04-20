from IPython.core.magic import (register_cell_magic)
import re
import uuid
from mako.template import Template
from typing import Optional

with open('sge.mako', 'r') as fh:
    template = fh.read()


def uuid_jobname(jobname: Optional[str] = None) -> str:
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
def rescomp(line: str, cell: str) -> int:
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





