"""Optional local LLM tool loop. MCP remains the only domain execution boundary."""
import asyncio
import json
import httpx

async def recommend_with_model(session, call, tools, model, query, brands, sort, bag):
    messages=[{'role':'system','content':
        'You are a disc golf recommendation agent. Always call the available tool. '
        'First search_discs to find matches; then rank_discs using the search results. '
        'Do not answer in prose.'},
        {'role':'user','content':query+'. Call search_discs now.'}]
    schemas=[{'type':'function','function':{'name':t.name,'description':t.description,'parameters':t.inputSchema}}
        for t in tools if t.name in ['search_discs','rank_discs']]
    for schema in schemas:
        if schema['function']['name']=='rank_discs':
            # The host already owns candidates and preferences. Avoid asking the model
            # to copy a potentially large candidate list into a tool call.
            schema['function']['parameters']={'type':'object','properties':{'sort':{'type':'string','enum':['match','popularity','speed','name']}},'required':['sort']}
            schema['function']['description']='Rank the discs from the preceding search. The host supplies candidates. Supply the requested sort.'
    found=None
    async with asyncio.timeout(25):
        async with httpx.AsyncClient(timeout=20,trust_env=False) as client:
            for _ in range(4):
                response=await client.post('http://127.0.0.1:11434/api/chat',json={
                    'model':model,'stream':False,'messages':messages,
                    'tools':[s for s in schemas if s['function']['name']==('rank_discs' if found and found['candidates'] else 'search_discs')],
                    'options':{'temperature':0,'num_predict':500}})
                response.raise_for_status()
                message=response.json()['message'];messages.append(message)
                calls=message.get('tool_calls',[])
                if not calls:
                    messages.append({'role':'user','content':'Call the available tool now. Do not answer in prose.'})
                    continue
                for request in calls[:2]:
                    name=request['function']['name']; args=request['function']['arguments']
                    if name=='search_discs':
                        normalized=args.get('query',query)
                        if not isinstance(normalized,str) or len(normalized)>300: raise ValueError('Invalid query')
                        found=await call(session,name,{'query':normalized,'brands':brands})
                        observed=found
                    elif name=='rank_discs' and found and found['candidates']:
                        # Candidate identity, preferences, ordering, and bag are host-owned.
                        ranked=await call(session,name,{'candidates':found['candidates'],'sort':sort,'bag':bag})
                        return dict(ranked,reference=found['reference'],mode='local-model')
                    else: raise ValueError('Invalid tool sequence')
                    messages.append({'role':'tool','tool_name':name,'content':json.dumps(observed)})
                    if found and found['candidates']:
                        messages.append({'role':'user','content':f'Now call rank_discs with sort {sort}.'})
    raise ValueError('Agent step budget exhausted')
