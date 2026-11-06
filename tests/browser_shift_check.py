import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.tools/disc-browser'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'DGRag/.tools/disc-browser'))
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1100,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8010')
    expect(page.locator('.card').first).to_be_visible()
    expect(page.locator('.shift-panel')).to_be_hidden()
    catalog=page.request.get('http://127.0.0.1:8010/api/catalog').json()['discs']
    ref=next(d for d in catalog if d['id']=='innova-leopard3')
    def fixture(route):
        route.fulfill(json={'discs':[ref],'run_id':'boundary-test','trace':[],'mode':'fixture'})
    page.route('**/api/recommend',fixture)
    page.locator('#query').fill('Leopard3');page.locator('#find').click()
    expect(page.locator('.shift-panel')).to_be_visible()
    with page.expect_response('**/api/shift') as response:
        page.get_by_role('button',name='Faster',exact=True).click()
    data=response.value.json()
    assert data['discs'] and all(d['speed']>7 for d in data['discs'])
    expect(page.locator('#find')).to_be_enabled()
    for speed,hidden,visible in [(1,'Slower','Faster'),(14,'Faster','Slower')]:
        ref=dict(ref,speed=speed)
        page.locator('#find').click()
        expect(page.get_by_role('button',name=hidden,exact=True)).to_be_hidden()
        expect(page.get_by_role('button',name=visible,exact=True)).to_be_visible()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    assert not errors,errors
    print('PASS: post-search controls, real MCP speed shift, speed 1/14 visibility, mobile layout, no JS errors.')
    browser.close()
