```python
def call_qstat() -> str:
    p = subprocess.Popen(["qstat"], stdout=subprocess.PIPE)
    out = p.stdout.read().decode().strip()
    return out
```