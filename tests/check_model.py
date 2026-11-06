import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent import run_agent
result=asyncio.run(run_agent(query='Similar to Leopard3',brands=['MVP']))
assert result['mode']=='local-model',result
assert result['discs'] and all(d['brand']=='MVP' for d in result['discs'])
assert result['discs'][0]['name']=='Relay',result
print('PASS: local model selected search and rank over real MCP; brand constraint preserved.')
