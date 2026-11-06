"""Bounded plan/act/observe workflow; all domain operations cross MCP."""
import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).parent

async def run_agent(query=None, brands=None, sort='match', bag=None, disc_id=None):
    run_id=str(uuid.uuid4()); trace=[]
    async def call(session,name,args):
        started=time.monotonic()
        for attempt in range(2):
            try:
                response=await asyncio.wait_for(session.call_tool(name,args),timeout=40)
                if response.isError: raise RuntimeError('Tool reported an error')
                value=response.structuredContent
                if value is None:
                    value=json.loads(next(c.text for c in response.content if c.type=='text'))
                trace.append(dict(tool=name,status='ok',attempt=attempt+1,elapsed_ms=round((time.monotonic()-started)*1000)))
                return value
            except (TimeoutError,RuntimeError):
                # Selection increments are non-idempotent: never retry them.
                if attempt or name=='record_selection': raise
        raise RuntimeError('Tool unavailable')
    result={'run_id':run_id,'trace':trace,'discs':[],'message':'','mode':'bounded-workflow'}
    try:
        async with asyncio.timeout(65):
            params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools_server.py')],cwd=str(ROOT))
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    discovered=(await session.list_tools()).tools
                    available={t.name for t in discovered}
                    required={'manufacturer_image','record_selection'} if disc_id else {'search_discs','rank_discs'}
                    if not required<=available: raise RuntimeError('Required tools missing')
                    if disc_id:
                        image=await call(session,'manufacturer_image',{'disc_id':disc_id})
                        result.update(image)
                        try: await call(session,'record_selection',{'disc_id':disc_id})
                        except Exception: result['message']+=' Selection count could not be saved.'
                    else:
                        model=os.environ.get('DISC_AGENT_MODEL','mistral:7b').strip()
                        modeled=None
                        if model:
                            from model_agent import recommend_with_model
                            try:
                                modeled=await recommend_with_model(session,call,discovered,model,query,brands or [],sort,bag or [])
                            except Exception as error:
                                trace.append(dict(tool='local_model',status='fallback',error_type=type(error).__name__))
                                result['mode']='bounded-fallback'
                        if modeled:
                            result.update(modeled)
                        else:
                            found=await call(session,'search_discs',{'query':query,'brands':brands or []})
                            # Observe search results before deciding whether ranking is useful.
                            if not found['candidates']: result['message']=found['message']
                            else:
                                ranked=await call(session,'rank_discs',{'candidates':found['candidates'],'sort':sort,'bag':bag or []})
                                result.update(ranked)
                            result['reference']=found['reference']
    except Exception:
        trace.append(dict(tool='workflow',status='failed'))
        result['message']='The recommendation tools are temporarily unavailable. Please retry. Your bag is saved in this browser.'
        result['failed']=True
    try:
        from tools_server import DATA
        DATA.mkdir(parents=True,exist_ok=True)
        record=dict(result,query=query,brands=brands,sort=sort,timestamp=time.time())
        # One file per run avoids concurrent writers corrupting a shared JSONL stream.
        (DATA/f'{run_id}.json').write_text(json.dumps(record,ensure_ascii=False),encoding='utf-8')
    except OSError:
        result['message']+=' Run history could not be saved.'
    return result
