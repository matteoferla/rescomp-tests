# rescomp-tests

> This is just a storage dumpyard and an internal thing.

Various tests done in Rescomp.
Rescomp runs Univa Grid Engine (UGE) as its batch-queuing system.

## Magics

In rescomp.py a cell magic is registered.
Which allows the cell to be run as queued task:

```jupyter
%%rescomp jobname=test queue=test.qc cores=1

print('Hello world')

```

It does not pack the contents of globals, so is pretty limited.

## Note on Dask

I never got Dask to work,
but Collin has but he could only submit to a single node without shared memory,
making it very limited.

## Functions

```python
import subprocess
import pandas as pd

def qstat2df() -> pd.DataFrame:
    """
    Get qstat as a pandas dataframe
    """
    headers = ['job-ID', 'prior', 'name', 'user', 'state', 'submit/start at', 'queue', 'slots ja-task-ID']
    rows = list(_call_qstat().split('\n'))[2:]
    return pd.DataFrame.from_records([dict(zip(headers, row.split())) for row in map(str.strip, rows)])


def availability() -> pd.DataFrame:
    """
    How is the cluster looking
    """
    headers = ['CLUSTER QUEUE', 'CQLOAD', 'USED', 'RES', 'AVAIL', 'TOTAL', 'aoACDS', 'cdsuE']
    p = subprocess.Popen(["qstat", '-g', 'c'], stdout=subprocess.PIPE)
    out = p.stdout.read().decode().strip()
    rows = list(out.split('\n'))[2:]
    return pd.DataFrame.from_records([dict(zip(headers, row.split())) for row in map(str.strip, rows)])

def job_ids():
    """
    Get the ids of jobs running —completed jobs will have disappeared.
    """
    return [int(line.strip().split()[0]) for line in _call_qstat().split('\n')[2:]]

def _call_qstat() -> str:
    """
    called by ``qstat2df`` and ``job_ids``.
    """
    p = subprocess.Popen(["qstat"], stdout=subprocess.PIPE)
    out = p.stdout.read().decode().strip()
    return out
```

## sge.mako template
Example usage of `sge.mako`:

```python
from mako.template import Template

with open('sge.mako', 'r') as fh:
    template = fh.read()
with open(f'{dataset_name}_{i}.sh', 'w') as fh:
    makoed = Template(template).render(jobname=f'{dataset_name}_{i}',
                                       cores=5,
                                       queue='short.qc',
                                       py_filename='analyse.py',
                                       py_args=f'{dataset_name} {subdataset_filename} {protein_filename} {settings_filename} 5'
                                       )
with open(f'{dataset_name}_{i}.sh', 'w') as fh:
    fh.write(makoed)
os.system(f'qsub {dataset_name}_{i}.sh')
```

## DRMAA

> :skull: deadend

In [drmaa_tests markdown file](drmaa_tests.md) are my notes.
The following is the best I could do.
It is rather pointless as a job that is finished becomes traceless.

```python
import os
import drmaa

os.environ['DRMAA_LIBRARY_PATH'] = '/mgmt/uge/8.6.8/lib/lx-amd64/libdrmaa.so.1.0'

class JobStatusChecker:
    session = None
    jobs = []

    def __init__(self):
        if not self.session:
            self.session = drmaa.Session()
            self.session.initialize()
            self.__class__.session = self.session

    def __del__(self):
        self.session.exit()

    def __getitem__(self, job_id):
        try:
            return self.session.jobStatus(str(job_id))
        except drmaa.InvalidJobException:
            return 'disappeared'

    def last(self):
        assert len(self.jobs), 'No known jobs'
        job_id = self.jobs[-1]
        return job_id, self[job_id]
```