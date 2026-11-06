"""Live public DiscFinder MCP check; requires internet, no API key."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from discfinder import lookup_stock,TOOL
result=asyncio.run(lookup_stock('innova-leopard3','US'))
assert result['status']=='ok',result
assert result['is_found'],result
assert any(t['tool']==TOOL and t['status']=='ok' for t in result['trace']),result
print('PASS: DiscFinder connected; find_retailer_stock discovered and called over remote MCP.')
print('Offers returned:',len(result['offers']))
