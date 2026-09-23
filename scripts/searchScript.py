from page.FrontPage import FrontPage


def search(page):
    gp = FrontPage(page)

    gp.search_input.fill("3C")
    gp.search_button.click()
    gp.page.wait_for_timeout(2000)
