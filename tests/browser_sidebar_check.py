import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'.tools/disc-browser'))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'DGRag/.tools/disc-browser'))
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1200,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8010')
    expect(page.locator('#brand-options label')).to_have_count(7)
    assert page.locator('#brand-options label:visible').all_text_contents()==[' Discraft',' Axiom',' MVP',' Innova',' Discmania']
    assert page.locator('#sort').bounding_box()['y']<page.locator('#brands').bounding_box()['y']
    expect(page.locator('#brands input:checked')).to_have_count(0)
    page.get_by_role('button',name='Show more',exact=False).click()
    expect(page.locator('#brand-options label:visible')).to_have_count(7)
    page.locator('#brands input[value="Streamline"]').check()
    page.get_by_role('button',name='Show less',exact=True).click()
    expect(page.locator('#brand-options label:visible')).to_have_count(5)
    expect(page.locator('#show-brands')).to_contain_text('1 selected')
    page.locator('#query').fill('understable fairway driver')
    with page.expect_response('**/api/recommend',timeout=70000) as response:
        page.locator('#find').click()
    data=response.value.json()
    assert data['discs'] and all(d['brand']=='Streamline' for d in data['discs']),data
    page.get_by_role('button',name='Show more',exact=False).click()
    expect(page.locator('#brands input[value="Streamline"]')).to_be_checked()
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    assert not errors,errors
    print('PASS: sort before brands; five popular defaults; expand/collapse all seven; hidden selection retained and applied; mobile; no JS errors.')
    browser.close()
