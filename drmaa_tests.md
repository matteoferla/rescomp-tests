## DRMAA

In Rescomp DRMAA is:
```python
import os
os.environ['DRMAA_LIBRARY_PATH'] = '/mgmt/uge/8.6.8/lib/lx-amd64/libdrmaa.so.1.0'
```

```python
# example of running drmaa.
import drmaa
drmaa_session = drmaa.Session()
drmaa_session.initialize()
print(f'Supported contact strings: {drmaa_session.contact}')
print(f'Supported DRM systems: {drmaa_session.drmsInfo}')
print(f'Supported DRMAA implementations: {drmaa_session.drmaaImplementation}')
print(f'Version {drmaa_session.version}')
drmaa_session.exit() 
```

    Supported contact strings: session=humbug.10755.813611879
    Supported DRM systems: UGE 8.6.8
    Supported DRMAA implementations: UGE 8.6.8
    Version 1.0

```python
import drmaa
drmaa_session = drmaa.Session()
drmaa_session.initialize()

def print_output(output_filename):
    print('Output:\n'+'*'*10)
    with open(output_filename, 'r') as fh:
        print(fh.read())
    print('*'*10)
    
def clean_output(output_filename):
    if os.path.exists(output_filename):
        os.remove(output_filename)


import os
output_filename = '/gpfs3/well/brc/matteo/test_output.txt'

with open('test.sh', 'w') as fh:
    fh.write('#!/bin/bash\n')
    #'-cwd'? 
    #  '-P brc.prjc', 
    for spec in ('-q short.qc', '-pe shmem 1','-j y', '-wd /gpfs3/well/brc/matteo/', '-M matteo@well.ox.ac.uk', '-N test'):
        fh.write(f'#$ {spec}\n')  
    fh.write('echo "hello Mars"\n')
    fh.write(f'echo "hello Mars" >> {output_filename}\n')
 
clean_output(output_filename)
job_template = drmaa_session.createJobTemplate()
job_template.jobName = 'Test'
# /well simlink to /well/gpfs3
#  -P brc.prjc -M matteo@well.ox.ac.uk
job_template.nativeSpecification = '-q short.qc -j y -N test -pe shmem 1 -wd /well/brc/matteo/'
job_template.remoteCommand = 'bash test.sh' # this is the script.
job_template.outputPath = ':'+os.path.join(output_filename)
job_template.joinFiles = True
#job_template.errorPath = ':'+os.path.join('/gpfs3/well/brc/matteo/test_error.log')
jobid = drmaa_session.runJob(job_template)
# ----------------------
decodestatus = {drmaa.JobState.UNDETERMINED: 'process status cannot be determined',
                drmaa.JobState.QUEUED_ACTIVE: 'job is queued and active',
                drmaa.JobState.SYSTEM_ON_HOLD: 'job is queued and in system hold',
                drmaa.JobState.USER_ON_HOLD: 'job is queued and in user hold',
                drmaa.JobState.USER_SYSTEM_ON_HOLD: 'job is queued and in user and system hold',
                drmaa.JobState.RUNNING: 'job is running',
                drmaa.JobState.SYSTEM_SUSPENDED: 'job is system suspended',
                drmaa.JobState.USER_SUSPENDED: 'job is user suspended',
                drmaa.JobState.DONE: 'job finished normally',
                drmaa.JobState.FAILED: 'job finished, but failed'}
import time
import datetime
previous = float('nan')
while True:
    status = drmaa_session.jobStatus(jobid)
    if previous != status:
        previous = status
        print(datetime.datetime.now(), decodestatus[status])
    if status in (drmaa.JobState.DONE, drmaa.JobState.FAILED):
        break
    time.sleep(1)
# ----------------------
drmaa_session.deleteJobTemplate(job_template) 
print_output(output_filename)
```

    2021-12-09 12:01:58.890574 job is queued and active
    2021-12-09 12:02:12.963337 job is running
    2021-12-09 12:02:15.975835 job finished, but failed
    Output:
    **********
    
    **********

Fails.

Running not via the grid:

```python
clean_output(output_filename)
assert not os.system('bash /well/brc/matteo/test.sh')
print_output(output_filename)
```

    0
    Output:
    **********
    hello Mars
    
    **********