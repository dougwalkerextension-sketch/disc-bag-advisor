"""Prove local imports and actual MCP work with the old project inaccessible."""
import asyncio
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN=ROOT.parent/'DGRag'
def inside(path, parent):
    return Path(path).resolve().is_relative_to(parent.resolve())
assert inside(sys.executable,ROOT),sys.executable
for path in sys.path:
    assert not inside(path or os.getcwd(),FORBIDDEN),path

def guard(event,args):
    if event in ('open','os.chdir','os.listdir','os.scandir') and args and isinstance(args[0],(str,bytes,os.PathLike)):
        value=os.fsdecode(args[0])
        if inside(value,FORBIDDEN): raise AssertionError('Access to the old project is blocked: '+value)
    if event=='subprocess.Popen':
        import shlex
        command=args[1]
        executable=args[0] or (command[0] if isinstance(command,(list,tuple)) else shlex.split(command,posix=False)[0].strip(chr(34)))
        assert inside(executable,ROOT),executable
sys.addaudithook(guard)
# Exercise the guard before testing application imports.
try:
    open(FORBIDDEN/'app.py')
except AssertionError:
    pass
else:
    raise AssertionError('Filesystem guard did not run')
sys.path.insert(0,str(ROOT))
os.environ['DISC_AGENT_MODEL']=''
os.environ.pop('PYTHONPATH',None)
os.environ.pop('PYTHONHOME',None)
from agent import run_agent
result=asyncio.run(run_agent(query='understable fairway driver',brands=['MVP']))
assert not result.get('failed'),result
assert len(result['discs'])==2,result
assert [t['tool'] for t in result['trace']]==['search_discs','rank_discs'],result
for module in tuple(sys.modules.values()):
    file=getattr(module,'__file__',None)
    if file: assert not inside(file,FORBIDDEN),file
print('PASS: local Python, local imports, and real MCP search/ranking with old-project access blocked.')
print('Interpreter:',sys.executable)
