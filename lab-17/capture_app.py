"""Save the actual running browser app for visible submission evidence."""
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1500, "height": 1100}, device_scale_factor=1)
    page.goto('http://localhost:8517', wait_until='networkidle')
    page.get_by_text('Download comparison CSV', exact=True).wait_for(timeout=120000)
    page.set_viewport_size({'width': 1800, 'height': 3600})
    page.screenshot(path=str(root / 'outputs/app_default.png'), full_page=True)
    page.get_by_role('textbox', name='Add another FRED series ID').fill('GS10')
    page.get_by_role('textbox', name='Add another FRED series ID').press('Enter')
    page.get_by_text('GS10 — Additional FRED series', exact=True).wait_for(timeout=120000)
    page.wait_for_function("document.querySelectorAll('[data-testid=\"stVegaLiteChart\"]').length >= 5",timeout=120000)
    page.set_viewport_size({'width': 1800, 'height': 4300})
    page.screenshot(path=str(root / 'outputs/app_with_GS10.png'), full_page=True)
    page.get_by_test_id('stDataFrame').screenshot(path=str(root / 'outputs/app_comparison.png'))
    (root / 'outputs/browser_visible_text.txt').write_text(page.locator('body').inner_text())
    browser.close()
print('Saved actual app screenshots: outputs/app_default.png and outputs/app_with_GS10.png')
