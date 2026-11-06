from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1200,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8010')
    card=page.locator('.card').filter(has=page.get_by_role('heading',name='Leopard3',exact=True))
    expect(card).to_be_visible()
    with page.expect_response('**/api/discs/innova-leopard3/stock',timeout=40000) as response:
        card.click()
    data=response.value.json()
    assert data['status']=='ok',data
    assert data['tool']=='find_retailer_stock'
    assert data['source']=='https://finder.golfwithdiscs.com/mcp'
    assert data['offers'],data
    expect(page.locator('.stock-offer')).to_have_count(len(data['offers']))
    assert all(a.get_attribute('href').startswith('https://') for a in page.locator('.stock-offer a').all())
    with page.expect_response('**/api/discs/innova-leopard3/stock',timeout=40000) as response:
        page.locator('#stock-country').select_option('GB')
    data=response.value.json()
    assert data['query_context']['target_country']=='GB',data
    expect(page.locator('#stock-retry')).to_be_enabled()
    page.screenshot(path='runtime/discfinder-dialog.png',full_page=True)
    page.route('**/api/discs/*/stock',lambda route:route.fulfill(status=503,json={'message':'DiscFinder unavailable'}))
    page.locator('#stock-retry').click()
    expect(page.locator('#stock-status')).to_contain_text('DiscFinder is unavailable')
    expect(page.locator('.stock-offer')).to_have_count(0)
    page.set_viewport_size({'width':390,'height':844})
    assert page.locator('#detail').evaluate('(node)=>node.scrollWidth<=node.clientWidth')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert not errors,errors
    print('PASS: View disc calls live DiscFinder; offers and country changes render; outage clears stale offers with no substitute; mobile; no JS errors.')
    browser.close()
