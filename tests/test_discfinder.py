import asyncio
import json
import sys
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import discfinder
from app import app
from fastapi.testclient import TestClient

def reply(data,error=False):
    return SimpleNamespace(isError=error,structuredContent=None,content=[SimpleNamespace(type='text',text=json.dumps(data))])

class DiscFinderTests(unittest.TestCase):
    def test_decode_preserves_source_and_rejects_unsafe_links(self):
        data={'is_found':True,'disc':{'name':'Leopard3'},'run_id':'../../escape',
            'offers':[{'retailer':'Safe','purchase_url':'https://shop.example/disc'},
            {'retailer':'Unsafe','purchase_url':'javascript:alert(1)'},
            {'retailer':'Credentials','purchase_url':'https://user:pass@shop.example/disc'}]}
        result=discfinder.decode(reply(data))
        self.assertEqual([o['retailer'] for o in result['offers']],['Safe'])
        self.assertNotIn('run_id',result)
        with self.assertRaises(discfinder.DiscFinderError): discfinder.decode(reply(data,True))
        with self.assertRaises(discfinder.DiscFinderError): discfinder.decode(reply({'unexpected':True}))

    def test_real_client_dispatch_uses_discovered_tool(self):
        fake=SimpleNamespace()
        fake.initialize=AsyncMock(return_value=SimpleNamespace(serverInfo=SimpleNamespace(name='golfwithdiscs-finder')))
        fake.list_tools=AsyncMock(return_value=SimpleNamespace(tools=[SimpleNamespace(name='find_retailer_stock',inputSchema={'required':['disc_slug']})]))
        fake.call_tool=AsyncMock(return_value=reply({'is_found':True,'offers':[]}))
        @asynccontextmanager
        async def transport(url,**kwargs):
            self.assertEqual(url,discfinder.ENDPOINT)
            self.assertNotIn('authorization',kwargs['http_client'].headers)
            yield (None,None,None)
        @asynccontextmanager
        async def session(*args,**kwargs): yield fake
        with patch('discfinder.streamable_http_client',transport),patch('discfinder.ClientSession',session):
            trace=[];result=asyncio.run(discfinder.remote_stock('innova-leopard3','US',trace))
        self.assertTrue(result['is_found'])
        fake.call_tool.assert_awaited_once_with('find_retailer_stock',{'disc_slug':'innova-leopard3','country_code':'US','limit':10,'in_stock_only':True})
        self.assertEqual([t['tool'] for t in trace],['tools/list','find_retailer_stock'])

    def test_outage_has_no_substitute(self):
        with patch('discfinder.remote_stock',new=AsyncMock(side_effect=TimeoutError)):
            result=asyncio.run(discfinder.lookup_stock('innova-leopard3','US'))
        self.assertEqual(result['status'],'unavailable')
        self.assertEqual(result['offers'],[])
        self.assertIn('No alternate stock source',result['message'])

    def test_not_found_is_distinct_from_outage(self):
        with patch('discfinder.remote_stock',new=AsyncMock(return_value={'is_found':False,'offers':[]})):
            result=asyncio.run(discfinder.lookup_stock('innova-leopard3','GB'))
        self.assertEqual(result['status'],'not_found')
        self.assertIn('did not find',result['message'])

    def test_stock_api_validation_and_country(self):
        mocked=AsyncMock(return_value={'status':'ok','offers':[]})
        with TestClient(app) as client,patch('discfinder.lookup_stock',mocked):
            self.assertEqual(client.post('/api/discs/innova-leopard3/stock',json={'country_code':'GB'}).status_code,200)
            mocked.assert_awaited_once_with('innova-leopard3','GB')
            self.assertEqual(client.post('/api/discs/innova-leopard3/stock',json={'country_code':'not-a-country'}).status_code,422)
            self.assertEqual(client.post('/api/discs/nope/stock',json={}).status_code,404)
        with TestClient(app) as client,patch('discfinder.lookup_stock',new=AsyncMock(return_value={'status':'unavailable','offers':[]})):
            self.assertEqual(client.post('/api/discs/innova-leopard3/stock',json={}).status_code,503)
