import time
import re

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from items import Item

driver = webdriver.Chrome(executable_path="C:/Users/balls/PycharmProjects/chromedriver")

driver.get("https://orteil.dashnet.org/cookieclicker/")

driver.implicitly_wait(0)

cookie = driver.find_element_by_id("bigCookie")

click_rate = 1
cookies_per_click = 1
cookies_per_second = 1

product_list = dict()
upgrade_list = dict()

topLeftAnchor = None


def main_loop():
    global click_rate
    global cookies_per_click

    time.sleep(2)
    remove_banner()
    while True:

        item = get_next_purchase()

        # spam click till we can afford the item. Timed so we can estimate our click rate.
        start = time.time()
        i = 0
        while get_cookie_count() <= item.cost:
            cookie.click()
            i += 1
        click_rate = i / (time.time() - start)

        # buy item.
        click_item_by_location(item)

        # if purchased item upgrades mouse and cursors, double the cookies per click.
        if item.type == "upgrade":
            for key, val in upgrade_list.items():
                if val.upgrades == 'Cursor':
                    cookies_per_click *= 2
            upgrade_list.clear()

        else:
            item.count += 1
            update_item(item)


# gather information on products and upgrades to then calculate which one to purchase next.
def get_next_purchase():
    get_products()
    get_upgrades()

    purchase_options = []

    # iterate over items in the product_list to
    for k, v in product_list.items():
        cost = v.cost
        increase = v.increase

        ttr = (cost / increase)  # time to return investment

        print("considering purchase ", v.name, "with ttr of ", ttr)
        purchase_options.append((ttr, product_list[k]))

    for k, v in upgrade_list.items():
        cost = v.cost
        try:
            product = product_list[v.upgrades]
            increase = product.count * product.increase
            if v.upgrades == "Cursor":
                increase = increase + (click_rate * cookies_per_click)
            if v.upgrades == "cps":
                increase = get_cps() * 0.01

            if increase:
                ttr = (cost / increase)
            else:
                ttr = float("inf")
        except KeyError:
            print("couldn't find a product with name ", v.upgrades)

        print("considering upgrade ", v.name, "with ttr of ", ttr)
        purchase_options.append((ttr, upgrade_list[k]))

    the_product = min(purchase_options, key=lambda t: t[0])
    the_product = the_product[1]
    print("next buy:", the_product.name, the_product.cost, the_product.increase)
    return the_product


# gets information of products available, add or update them to the product_list dict
def get_products():
    products = driver.find_elements_by_xpath("//*[@class='product unlocked enabled']")
    products += driver.find_elements_by_xpath("//*[@class='product unlocked disabled']")
    products.append(driver.find_element_by_xpath("//*[@class='product locked disabled']"))

    for product in products:
        elemText = product.text.split()
        name = elemText[0]
        cost = elemText[1]
        location = (product.location['x'], product.location['y'])

        # if cost is over 1 million, the cost is split into elemText[1] abd elemText[2]
        if len(elemText) > 3:
            cost += elemText[2]

        if name not in product_list.keys():
            product_list[name] = Item(name, make_num(cost), location, "product")

        product_list[name].cost = make_num(cost)


# locates upgrades, hovers mouse, gathers information from the tooltip.
def get_upgrades():
    upgrades = driver.find_elements_by_xpath("//*[@class='crate upgrade']")
    upgrades += driver.find_elements_by_xpath("//*[@class='crate upgrade enabled']")

    for upgrade in upgrades:
        id = upgrade.get_attribute("id")

        # check if we already have information on this upgrade, if not then hover and collect from tooltip
        if id not in upgrade_list.keys():
            try:
                action = ActionChains(driver)
                action.move_to_element(upgrade).perform()
                tooltip = driver.find_element_by_xpath("//*[@id='tooltip']").text.splitlines()

                cost = make_num(tooltip[0])
                upgrade_name = tooltip[1]
                improves = tooltip[3]
                location = (upgrade.location['x'], upgrade.location['y'])
                new_item_obj = Item(upgrade_name, cost, location, "upgrade")
                new_item_obj.upgrades = improves
                upgrade_list[id] = new_item_obj
            except:
                pass

        # update upgrade's cookies per second increase, does not need to hover over upgrade.
        item = upgrade_list[id]
        location = (upgrade.location['x'], upgrade.location['y'])
        item.location = location
        for product_name in product_list.keys():
            if product_name.upper() in item.upgrades.upper():
                item.upgrades = product_name
                increase = product_list[product_name].cps
                item.increase = increase
            elif "%" in item.upgrades:
                item.upgrades = "cps"


# hover over item then gather information from the tooltip
def update_item(item):
    move_to_item_location(item)
    tooltip = driver.find_element_by_xpath("//*[@id='tooltip']").text.splitlines()

    if len(tooltip) > 4:
        increase = make_num(tooltip[4])
        item.increase = increase

        pattern = "producing (.*) cookies"
        cps = tooltip[5]
        match = re.findall(pattern, cps)
        match = make_num(match)
        item.cps = match

    get_products()


# moves cursor to the location of passed element
def move_to_item_location(item):
    anchor = driver.find_element_by_id("storeBulk1")
    x = anchor.location['x']
    y = anchor.location['y']
    action = ActionChains(driver)
    action.move_to_element_with_offset(anchor, item.x - x, item.y - y)
    action.perform()


# click on element location by passing through an element
def click_item_by_location(item):
    move_to_item_location(item)
    action = ActionChains(driver)
    action.click().perform()


# click on element by passing through an element
def click_elem(elem):
    action = ActionChains(driver)
    action.move_to_element(elem).click().perform()


# takes a string and returns it as a float.
def make_num(string: str):
    string = f"{string}"
    try:
        pattern1 = "[0-9\.]+"
        found = re.findall(pattern1, string)
        num_as_string = ""
        for i in found:
            num_as_string += i

        num_as_string = float(num_as_string)

        if "million" in string:
            num_as_string *= 10 ** 6
        if "billion" in string:
            num_as_string *= 10 ** 9
        if "trillion" in string:
            num_as_string *= 10 ** 12
        if "quadrillion" in string:
            num_as_string *= 10 ** 15
    except:
        num_as_string = 1

    return num_as_string


# returns cookie count
def get_cookie_count():
    cookies = driver.find_element_by_id("cookies")
    cookie_count = cookies.text.split(" ")[0]
    cookie_count = make_num(cookie_count)

    return cookie_count


# returns the cookies per second generation
def get_cps():
    cookies = driver.find_element_by_id("cookies")
    cps = (cookies.text.split(" ")[4])
    cps = make_num(cps) + (cookies_per_click * click_rate)
    return cps


# removes the cookie accept banner at the bottom of the page. Not needed but definitely wanted
def remove_banner():
    elem = driver.find_element_by_css_selector("body > div.cc_banner-wrapper > div > a.cc_btn.cc_btn_accept_all")
    action = ActionChains(driver)
    action.move_to_element(elem)
    action.click()
    action.perform()


if __name__ == "__main__":
    main_loop()
