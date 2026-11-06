import asyncio
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent import run_agent

class OpenAIIntegration(unittest.TestCase):
    def config(self,key='test-secret'):
        return {'api_key':key,'model':'gpt-5-mini','enabled':True}

    def test_responses_loop_and_host_constraints(self):
        requests=[]
        async def post(client,url,**kwargs):
            requests.append(copy.deepcopy(kwargs))
            name='search_discs' if len(requests)==1 else 'rank_discs'
            args={'query':'Leopard3'} if len(requests)==1 else {'sort':'name'}
            output=[{'type':'reasoning','id':'r1','summary':[],'encrypted_content':'opaque-state'}] if len(requests)==1 else []
            output.append({'type':'function_call','name':name,'call_id':'call-'+str(len(requests)),'arguments':json.dumps(args)})
            return httpx.Response(200,json={'status':'completed','output':output})
        with patch('model_agent.settings',return_value=self.config()),patch('httpx.AsyncClient.post',new=post):
            result=asyncio.run(run_agent(query='like Leopard3',brands=['MVP'],sort='match',bag=['mvp-signal']))
        self.assertEqual(result['mode'],'openai-model',result)
        self.assertEqual(result['discs'][0]['name'],'Relay')
        self.assertTrue(all(d['brand']=='MVP' and d['id']!='mvp-signal' for d in result['discs']))
        self.assertEqual(len(requests),2)
        self.assertTrue(all(r['json']['store'] is False for r in requests))
        self.assertEqual(requests[1]['json']['input'][1]['encrypted_content'],'opaque-state')
        self.assertTrue(any(i.get('type')=='function_call_output' for i in requests[1]['json']['input']))
        self.assertNotIn('test-secret',json.dumps(result))

    def test_missing_key_does_not_call_provider(self):
        with patch('model_agent.settings',return_value=self.config('')),patch('httpx.AsyncClient.post') as post:
            result=asyncio.run(run_agent(query='understable fairway driver',brands=['MVP']))
        post.assert_not_called()
        self.assertEqual(result['mode'],'bounded-fallback')
        self.assertEqual(len(result['discs']),2)
        self.assertIn('not connected',result['message'])

    def test_provider_failures_are_safe_fallbacks(self):
        for status,reason in [(401,'authentication'),(429,'rate_limit_or_quota'),(500,'service_error')]:
            async def post(client,url,**kwargs):
                return httpx.Response(status,json={'error':{'message':'test-secret must not reach the user'}})
            with patch('model_agent.settings',return_value=self.config()),patch('httpx.AsyncClient.post',new=post):
                result=asyncio.run(run_agent(query='understable fairway driver',brands=['MVP']))
            self.assertEqual(result['mode'],'bounded-fallback')
            self.assertIn(reason,result['message'])
            self.assertNotIn('test-secret',json.dumps(result))
            self.assertEqual(len(result['discs']),2)

    def test_malformed_tool_arguments_fall_back(self):
        async def post(client,url,**kwargs):
            return httpx.Response(200,json={'status':'completed','output':[{'type':'function_call','name':'search_discs','call_id':'bad','arguments':'invalid json'}]})
        with patch('model_agent.settings',return_value=self.config()),patch('httpx.AsyncClient.post',new=post):
            result=asyncio.run(run_agent(query='understable fairway driver',brands=['MVP']))
        self.assertEqual(result['mode'],'bounded-fallback')
        self.assertEqual(len(result['discs']),2)
