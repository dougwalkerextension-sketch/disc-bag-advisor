"""Optional browser verification; requires Playwright and installed Edge."""
import json
import sys
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:8010')
    page.locator('.card').first.wait_for()
    page.get_by_role('button',name='Understable fairways',exact=True).click()
    expect(page.locator('#result-count')).to_have_text(re.compile(r'\d+ matches'),timeout=60000)
    assert page.locator('.card').count()>=3
    page.locator('.card').filter(has=page.get_by_role('heading',name='Leopard3',exact=True)).click()
    page.locator('#add-bag').click()
    assert page.locator('#bag-count').inner_text()=='1'
    page.locator('#close-detail').click()
    page.locator('#brands input[value="MVP"]').check()
    expect(page.locator('#find')).to_be_enabled(timeout=60000)
    assert page.locator('.card').count()==2
    page.screenshot(path=str(Path(__file__).resolve().parents[1]/'runtime/desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    page.screenshot(path=str(Path(__file__).resolve().parents[1]/'runtime/mobile.png'),full_page=True)
    page.reload()
    page.locator('.card').first.wait_for()
    assert page.locator('#bag-count').inner_text()=='1'
    assert not errors,errors
    print(json.dumps({'browser':'Edge','desktop':'passed','mobile':'passed','bag_persistence':'passed','javascript_errors':errors}))
    browser.close()
