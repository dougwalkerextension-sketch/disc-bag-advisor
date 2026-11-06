from playwright.sync_api import sync_playwright,expect

with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1200,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8010')
    expect(page.locator('.card').first).to_be_visible()
    catalog=page.request.get('http://127.0.0.1:8010/api/catalog').json()['discs']
    mvp=page.locator('#brands input[value="MVP"]')
    innova=page.locator('#brands input[value="Innova"]')
    mvp.check()
    expect(page.locator('.card')).to_have_count(sum(d['brand']=='MVP' for d in catalog))
    mvp.uncheck()
    expect(page.locator('#brand-filter-state')).to_contain_text('Brand filter off')
    expect(page.locator('.card')).to_have_count(3)
    calls=[]
    def respond(route):
        body=route.request.post_data_json;calls.append((route.request.url,body))
        if route.request.url.endswith('/api/shift'):
            ref=next(d for d in catalog if d['id']==body['reference_id'])
            discs=[d for d in catalog if d['speed']>ref['speed']]
        else:
            discs=[d for d in catalog if d['category']=='fairway' and d['turn']+d['fade']<0]
        if body['brands']: discs=[d for d in discs if d['brand'] in body['brands']]
        route.fulfill(json={'discs':discs,'trace':[],'run_id':'browser-fixture','mode':'fixture','message':''})
    page.route('**/api/recommend',respond)
    page.route('**/api/shift',respond)
    page.locator('#query').fill('understable fairway driver');page.locator('#find').click()
    expect(page.locator('#find')).to_be_enabled()
    all_count=len([d for d in catalog if d['category']=='fairway' and d['turn']+d['fade']<0])
    expect(page.locator('.card')).to_have_count(all_count)
    page.locator('#query').fill('unsubmitted draft')
    mvp.check()
    expect(page.locator('.card')).to_have_count(2)
    assert calls[-1][1]['query']=='understable fairway driver'
    assert calls[-1][1]['brands']==['MVP']
    innova.check()
    expect(page.locator('#find')).to_be_enabled()
    assert set(calls[-1][1]['brands'])=={'MVP','Innova'}
    assert all(b in ['MVP','Innova'] for b in page.locator('.card .brand').all_text_contents())
    mvp.uncheck();innova.uncheck()
    expect(page.locator('.card')).to_have_count(all_count)
    assert calls[-1][1]['brands']==[]
    expect(page.locator('#brand-filter-state')).to_contain_text('Brand filter off')
    page.get_by_role('button',name='Faster',exact=True).click()
    expect(page.locator('#find')).to_be_enabled()
    original_ref=calls[-1][1]['reference_id']
    mvp.check()
    expect(page.locator('#find')).to_be_enabled()
    assert calls[-1][0].endswith('/api/shift')
    assert calls[-1][1]['reference_id']==original_ref
    assert calls[-1][1]['brands']==['MVP']
    # A brand with no matches must clear old cards rather than retain excluded results.
    page.get_by_role('button',name='Show more',exact=False).click()
    elevation=page.locator('#brands input[value="Elevation"]')
    elevation.check();mvp.uncheck()
    expect(page.locator('.card')).to_have_count(0)
    elevation.uncheck()
    expect(page.locator('#find')).to_be_enabled()
    assert calls[-1][1]['brands']==[]
    assert page.locator('.card').count()>0
    assert not errors,errors
    print('PASS: immediate preview/search/shift filters; empty selection disables filtering; multi-brand OR; draft preserved; empty matches clear excluded cards; no JS errors.')
    browser.close()
