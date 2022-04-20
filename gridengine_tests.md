The module `gridengine` seems to have a bug that is fixed in a pull request.

```python
import gridengine

def monkeypatch():
    # patch as in https://github.com/hbristow/gridengine/pull/2
    import inspect, gridengine
    old = 'resources = dict(self.resources.items() + resources.items())'
    new = 'resources = resources.update(self.resources) if resources else self.resources'
    old_code = inspect.getsource(gridengine.GridEngineScheduler.schedule)
    new_code = old_code.replace(old, new)
    exec('from gridengine import job, settings\nclass Dummy(gridengine.GridEngineScheduler):\n'+new_code, globals())
    gridengine.GridEngineScheduler = Dummy
    gridengine.schedulers.GridEngineScheduler = Dummy
    
monkeypatch()
```
```python
# https://www.medsci.ox.ac.uk/divisional-services/support-services-1/bmrc/cluster-usage
scheduler = gridengine.GridEngineScheduler(**{' ': '-q test.qc -M matteo@well.ox.ac.uk -pe shmem 1'})
#short.qc

def foo():
    print('Foo')
    return 'bar'

job = gridengine.Job(target=foo)

dispatcher = gridengine.JobDispatcher(scheduler)
dispatcher.dispatch([job])
dispatcher.join()
```

    JobDispatcher: starting job dispatcher on transport tcp://10.136.6.18:40307

    DeniedByDrmException: code 17: Unknown option script
