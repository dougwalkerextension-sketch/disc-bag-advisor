"""MCP tool server; only catalog-owned HTTPS URLs are fetched."""
import json
import os
import re
import sqlite3
import time
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
sys.path.insert(0,str(Path(__file__).parent))
import httpx
from mcp.server.fastmcp import FastMCP
from catalog import CATALOG, get_disc

mcp = FastMCP('Disc Bag Tools')
DATA = Path(os.environ.get('DISC_DATA_DIR', Path(__file__).parent/'runtime'))

def db():
    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DATA/'activity.sqlite', timeout=5)
    con.execute('CREATE TABLE IF NOT EXISTS selections (disc_id TEXT PRIMARY KEY, count INTEGER NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS images (disc_id TEXT PRIMARY KEY, payload TEXT, saved REAL)')
    return con

@mcp.tool()
def search_discs(query: str, brands: list[str] = []) -> dict:
    """Resolve named discs or flight categories, preserving strict brand filters."""
    q = query.lower().strip()
    named = [d for d in CATALOG if re.search(r'(?<!\w)'+re.escape(d['name'].lower())+r'(?!\w)',q)]
    named.sort(key=lambda d: -len(d['name']))
    category = next((c for c, words in [('fairway',['fairway']),('distance',['distance']),
        ('midrange',['midrange','mid-range','mid range']),('putter',['putter','putt','approach'])]
        if any(w in q for w in words)), None)
    stability = next((s for s in ['understable','overstable','stable'] if s in q), None)
    if not named and not category and not stability and q not in ['all','browse','discs']:
        return dict(candidates=[],reference=None,message='Disc or category not recognized. Try Leopard3 or understable fairway driver.')
    refs = named[:3]
    candidates=[]
    for original in CATALOG:
        d=dict(original)
        if brands and d['brand'] not in brands: continue
        if refs:
            if d['id'] in {r['id'] for r in refs}: continue
            distance = sum(abs(d['speed']-r['speed'])*2+abs(d['glide']-r['glide'])*.5+
                abs(d['turn']-r['turn'])+abs(d['fade']-r['fade']) for r in refs)/len(refs)
            if d['category'] not in {r['category'] for r in refs}: continue
        else:
            if category and d['category']!=category: continue
            balance=d['turn']+d['fade']
            if stability=='understable' and not balance<0: continue
            if stability=='overstable' and not balance>=2: continue
            if stability=='stable' and not 0<=balance<2: continue
            distance=0
        d['score']=round(max(0,100-distance*8),1)
        d['reason']=('Similar flight numbers to '+', '.join(r['name'] for r in refs)) if refs else 'Matches your category and stability filters'
        candidates.append(d)
    return dict(candidates=candidates,reference=refs,message='' if candidates else 'No matches in the starter catalog. Try fewer brand filters or a broader category.')

@mcp.tool()
def shift_discs(reference_id: str, direction: str, brands: list[str] = []) -> dict:
    """Find discs faster/slower or more/less stable than the leading previous result."""
    ref=get_disc(reference_id)
    if not ref: raise ValueError('Unknown reference disc')
    if direction not in ['faster','slower','overstable','understable']:
        raise ValueError('Unknown shift direction')
    speed=ref['speed']; stability=ref['turn']+ref['fade']
    if (direction=='slower' and speed<=1) or (direction=='faster' and speed>=14):
        return dict(candidates=[],reference=[ref],message='Already at the speed limit.')
    target_speed=max(1,min(14,speed+({'faster':1,'slower':-1}.get(direction,0))))
    target_stability=stability+({'overstable':1,'understable':-1}.get(direction,0))
    candidates=[]
    for original in CATALOG:
        d=dict(original); balance=d['turn']+d['fade']
        if brands and d['brand'] not in brands: continue
        if direction=='faster' and d['speed']<=speed: continue
        if direction=='slower' and d['speed']>=speed: continue
        if direction=='overstable' and balance<=stability: continue
        if direction=='understable' and balance>=stability: continue
        distance=2*abs(d['speed']-target_speed)+abs(balance-target_stability)+.5*abs(d['glide']-ref['glide'])
        d.update(score=round(max(0,100-8*distance),1),reason=f'{direction.capitalize()} than {ref["name"]}')
        candidates.append(d)
    return dict(candidates=candidates,reference=[ref],message='' if candidates else 'No discs match this shift in the starter catalog. Try another direction or fewer brand filters.')

@mcp.tool()
def rank_discs(candidates: list[dict], sort: str = 'match', bag: list[str] = []) -> dict:
    """Rank retrieved catalog discs; popularity means selections in this installation."""
    with db() as con: counts=dict(con.execute('SELECT disc_id,count FROM selections'))
    result=[]
    for item in candidates:
        d=get_disc(item.get('id'))
        if not d or d['id'] in bag: continue
        d.update(score=item.get('score',0),reason=item.get('reason',''),popularity=counts.get(d['id'],0))
        result.append(d)
    keys={'match':lambda d:(-d['score'],d['name']), 'popularity':lambda d:(-d['popularity'],-d['score'],d['name']),
        'speed':lambda d:(d['speed'],d['name']),'name':lambda d:d['name']}
    if sort not in keys: raise ValueError('Unsupported sort')
    result.sort(key=keys[sort])
    return dict(discs=result,popularity_label='Selections on this installation; not market sales',message='' if result else 'No new discs match. Broaden your search or remove bag exclusions.')

class ImageParser(HTMLParser):
    def __init__(self): super().__init__(); self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('property',a.get('name')) in ['og:image','twitter:image'] and a.get('content'):
            self.images.append(a['content'])
        if tag=='img' and a.get('src') and any(w in a.get('alt','').lower() for w in ['disc','star','opto','neutron']):
            self.images.append(a['src'])

def allowed(url):
    p=urlparse(url)
    return p.scheme=='https' and not p.username and p.port in (None,443) and any(
        p.hostname==h or (p.hostname or '').endswith('.'+h) for h in
        ['innovadiscs.com','latitude64.com','mvpdiscsports.com','axiomdiscs.com','shopify.com',
         'discraft.com','discmania.net','streamlinediscs.com'])

@mcp.tool()
async def manufacturer_image(disc_id: str) -> dict:
    """Get product imagery from a fixed manufacturer page with bounded redirects and cached fallback."""
    disc=get_disc(disc_id)
    if not disc: return dict(image_url=None,message='Unknown disc.')
    with db() as con: cached=con.execute('SELECT payload,saved FROM images WHERE disc_id=?',(disc_id,)).fetchone()
    if cached and time.time()-cached[1]<86400: return json.loads(cached[0])
    try:
        async with httpx.AsyncClient(timeout=8,follow_redirects=False) as client:
            url=disc['source']
            for _ in range(4):
                if not allowed(url): raise ValueError('Unapproved redirect')
                async with client.stream('GET',url,headers={'User-Agent':'DiscBagAdvisor/1.0'}) as response:
                    if response.is_redirect:
                        url=urljoin(url,response.headers['location']); continue
                    response.raise_for_status()
                    body=b''
                    async for chunk in response.aiter_bytes():
                        body+=chunk
                        if len(body)>2_000_000: raise ValueError('Page too large')
                break
            else: raise ValueError('Too many redirects')
        parser=ImageParser(); parser.feed(body.decode('utf-8',errors='replace'))
        image=next((urljoin(url,s) for s in parser.images if allowed(urljoin(url,s))),None)
        result=dict(image_url=image,source=url,message='' if image else 'Manufacturer image unavailable. Open the official page below.',cached=False)
        if image:
            with db() as con: con.execute('INSERT OR REPLACE INTO images VALUES (?,?,?)',(disc_id,json.dumps(result),time.time()))
        return result
    except (httpx.HTTPError,ValueError,KeyError):
        if cached:
            result=json.loads(cached[0]); result.update(cached=True,message='Showing a cached manufacturer image; the site is unavailable.'); return result
        return dict(image_url=None,source=disc['source'],message='Manufacturer site unavailable. Your recommendations are still available.')

@mcp.tool()
def record_selection(disc_id: str) -> dict:
    """Record an explicit detail selection as one local popularity event."""
    if not get_disc(disc_id): raise ValueError('Unknown disc')
    with db() as con:
        con.execute('INSERT INTO selections VALUES (?,1) ON CONFLICT(disc_id) DO UPDATE SET count=count+1',(disc_id,))
    return {'recorded':True}

if __name__=='__main__': mcp.run(transport='stdio')
