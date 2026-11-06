"""Direct DiscFinder MCP client. Never substitutes web/model stock data."""
import asyncio
import json
import time
import uuid
from datetime import timedelta,datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from catalog import get_disc

ROOT=Path(__file__).parent
ENDPOINT='https://finder.golfwithdiscs.com/mcp'
TOOL='find_retailer_stock'

class DiscFinderError(RuntimeError): pass

def config():
    values=json.loads((ROOT/'discfinder.json').read_text(encoding='utf-8'))
    if values['endpoint']!=ENDPOINT or values['tool']!=TOOL:
        raise DiscFinderError('Unexpected DiscFinder endpoint or tool')
    limit=values.get('limit',10)
    if not isinstance(limit,int) or not 1<=limit<=25: raise DiscFinderError('Invalid offer limit')
    return values

def safe_url(value):
    if not isinstance(value,str): return None
    try:
        p=urlparse(value)
        if p.scheme=='https' and p.hostname and not p.username and not p.password:
            return value
    except ValueError: pass
    return None

def decode(result):
    if result.isError: raise DiscFinderError('Remote tool reported an error')
    data=result.structuredContent
    if data is None:
        data=json.loads(next(c.text for c in result.content if c.type=='text'))
    if not isinstance(data,dict) or not isinstance(data.get('is_found'),bool):
        raise DiscFinderError('Unexpected DiscFinder result')
    if not isinstance(data.get('offers',[]),list): raise DiscFinderError('Unexpected offers')
    offers=[]
    for item in data.get('offers',[])[:25]:
        if not isinstance(item,dict): continue
        url=safe_url(item.get('purchase_url'))
        if not url: continue
        item=dict(item,purchase_url=url)
        offers.append(item)
    return dict(is_found=data['is_found'],disc=data.get('disc') if isinstance(data.get('disc'),dict) else {},
        query_context=data.get('query_context') if isinstance(data.get('query_context'),dict) else {},
        summary=data.get('summary') if isinstance(data.get('summary'),dict) else {},
        offers=offers if data['is_found'] else [])

async def remote_stock(disc_slug,country_code,trace):
    settings=config()
    async with asyncio.timeout(25):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20,connect=6),trust_env=False) as client:
            async with streamable_http_client(settings['endpoint'],http_client=client) as (read,write,_):
                async with ClientSession(read,write,read_timeout_seconds=timedelta(seconds=20)) as session:
                    server=await session.initialize()
                    discovered=(await session.list_tools()).tools
                    names=[t.name for t in discovered]
                    trace.append(dict(tool='tools/list',status='ok',server=server.serverInfo.name))
                    if TOOL not in names: raise DiscFinderError('find_retailer_stock is not available')
                    schema=next(t.inputSchema for t in discovered if t.name==TOOL)
                    required=set(schema.get('required',[]))
                    args={'disc_slug':disc_slug,'country_code':country_code,'limit':settings['limit'],'in_stock_only':True}
                    if not required<=set(args): raise DiscFinderError('DiscFinder tool schema changed')
                    start=time.monotonic()
                    result=await session.call_tool(TOOL,args)
                    data=decode(result)
                    trace.append(dict(tool=TOOL,status='ok',elapsed_ms=round((time.monotonic()-start)*1000),arguments=args))
                    return data

async def lookup_stock(disc_id,country_code='US'):
    disc=get_disc(disc_id)
    if not disc: raise ValueError('Unknown disc')
    trace=[]
    result=dict(run_id=str(uuid.uuid4()),mode='discfinder-mcp',source=ENDPOINT,tool=TOOL,
        checked_at=datetime.now(timezone.utc).isoformat(),country_code=country_code,
        disc_id=disc_id,trace=trace,offers=[],status='unavailable',message='')
    try:
        data=await remote_stock(disc['id'],country_code,trace)
        result.update(data)
        result['status']='ok' if data['is_found'] else 'not_found'
        if not data['is_found']: result['message']='DiscFinder did not find this disc. No alternate stock source was used.'
        elif not data.get('offers'): result['message']='DiscFinder returned no qualifying in-stock offers for this selection.'
    except Exception as error:
        trace.append(dict(tool=TOOL,status='failed',error_type=type(error).__name__))
        result['message']='DiscFinder is temporarily unavailable. Retry to check stock. No alternate stock source was used.'
    try:
        from tools_server import DATA
        DATA.mkdir(parents=True,exist_ok=True)
        (DATA/(result['run_id']+'.json')).write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    except OSError:
        result['message']+=' Stock history could not be saved.'
    return result
