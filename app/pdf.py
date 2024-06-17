import playwright.sync_api


def from_html(html: str, dest: str):
    with playwright.sync_api.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.emulate_media(media="screen")
        page.pdf(
            path=dest,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()
