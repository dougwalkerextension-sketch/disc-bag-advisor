import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['DISC_DATA_DIR']=tempfile.mkdtemp(prefix='disc-test-')
os.environ['DISC_AGENT_MODEL']=''
from tools_server import search_discs, shift_discs, rank_discs, record_selection, manufacturer_image, allowed
from agent import run_agent
from app import app
from fastapi.testclient import TestClient

class Recommendations(unittest.TestCase):
    def test_directional_shifts(self):
        from catalog import get_disc
        ref=get_disc('innova-leopard3')
        for direction in ['faster','slower','overstable','understable']:
            result=shift_discs(ref['id'],direction,['MVP'])
            self.assertTrue(result['candidates'])
            for d in result['candidates']:
                self.assertEqual(d['brand'],'MVP')
                value=d['speed'] if direction in ['faster','slower'] else d['turn']+d['fade']
                base=ref['speed'] if direction in ['faster','slower'] else ref['turn']+ref['fade']
                self.assertTrue(value>base if direction in ['faster','overstable'] else value<base)

    def test_speed_boundaries(self):
        from catalog import get_disc
        for speed,direction in [(1,'slower'),(14,'faster')]:
            ref=get_disc('innova-leopard3');ref['speed']=speed
            with patch('tools_server.get_disc',return_value=ref):
                self.assertEqual(shift_discs(ref['id'],direction)['candidates'],[])

    def test_shift_mcp_and_validation(self):
        result=asyncio.run(run_agent(reference_id='innova-leopard3',direction='faster',brands=['MVP'],bag=['mvp-volt']))
        self.assertFalse(result.get('failed'),result)
        self.assertEqual([t['tool'] for t in result['trace']],['shift_discs','rank_discs'])
        self.assertTrue(all(d['speed']>7 and d['id']!='mvp-volt' for d in result['discs']))
        with TestClient(app) as client:
            self.assertEqual(client.post('/api/shift',json={'reference_id':'nope','direction':'faster'}).status_code,404)
            self.assertEqual(client.post('/api/shift',json={'reference_id':'innova-leopard3','direction':'invalid'}).status_code,422)

    def test_understable_and_brand(self):
        result=search_discs('understable fairway driver',['MVP'])
        self.assertEqual({d['name'] for d in result['candidates']},{'Relay','Signal'})
    def test_named_comparison(self):
        found=search_discs('similar to River and Crave')
        self.assertEqual(len(found['reference']),2)
        self.assertNotIn('River',[d['name'] for d in found['candidates']])
    def test_unknown_has_recovery(self):
        self.assertIn('not recognized',search_discs('xyz')['message'])
    def test_bag_and_popularity(self):
        candidates=search_discs('all')['candidates']
        record_selection('mvp-relay')
        ranked=rank_discs(candidates,'popularity',['innova-leopard3'])['discs']
        self.assertEqual(ranked[0]['id'],'mvp-relay')
        self.assertNotIn('innova-leopard3',[d['id'] for d in ranked])
    def test_ssrf(self):
        for url in ['http://127.0.0.1','https://innovadiscs.com.evil.test/x','https://user@innovadiscs.com/x']:
            self.assertFalse(allowed(url))
    def test_image_failure(self):
        import httpx
        with patch('httpx.AsyncClient.stream',side_effect=httpx.ConnectError('offline')):
            result=asyncio.run(manufacturer_image('innova-leopard3'))
        self.assertIsNone(result['image_url'])
        self.assertIn('unavailable',result['message'])
    def test_api_validation(self):
        with TestClient(app) as client:
            metadata=client.get('/api/catalog').json()
            self.assertEqual(len(metadata['popular_brands']),5)
            self.assertEqual(set(metadata['brands']),{d['brand'] for d in metadata['discs']})
            self.assertEqual(client.post('/api/recommend',json={'query':'all','brands':['Unknown']}).status_code,422)
            self.assertEqual(client.get('/').status_code,200)
            self.assertEqual(client.post('/api/recommend',json={'query':'all','sort':'invented'}).status_code,422)
            self.assertEqual(client.post('/api/discs/nope',json={}).status_code,404)
            self.assertEqual(client.post('/api/recommend',json={'query':'all'},headers={'Origin':'https://evil.test'}).status_code,403)
    def test_real_mcp_transport(self):
        result=asyncio.run(run_agent(query='understable fairway driver',brands=['MVP']))
        self.assertFalse(result.get('failed'),result)
        self.assertEqual(len(result['discs']),2)
        self.assertEqual([t['tool'] for t in result['trace']],['search_discs','rank_discs'])
    def test_workflow_failure(self):
        with patch('agent.stdio_client',side_effect=OSError('missing executable')):
            result=asyncio.run(run_agent(query='all'))
        self.assertTrue(result['failed'])
        self.assertIn('retry',result['message'])

if __name__=='__main__':unittest.main()
