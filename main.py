import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome(executable_path="C:/Users/balls/PycharmProjects/chromedriver")

driver.get("https://orteil.dashnet.org/cookieclicker/")
print(driver.title)

actions = ActionChains(driver)
actions.click()
driver.implicitly_wait(5)

cookie = driver.find_element_by_id("bigCookie")

click_rate = 0
cookies_per_click = 1


def main_loop():
    while True:

        next_product_cost, next_p_elem = get_next_purchase()

        # click till we have enough cookies, also update click rate for more accurate calculations
        start = time.time()
        clicks = 0
        while get_cookie_count() < next_product_cost:
            cookie.click()
            clicks += 1
        click_rate = round(clicks / (time.time() - start))
        
        # actions to purchase product
        purchase_actions = ActionChains(driver)
        purchase_actions.move_to_element(next_p_elem)
        purchase_actions.click()
        purchase_actions.perform()


def make_float(num):  # removes deliminator from string and returns as a float
    num = num.replace(",", "")
    num_as_f = float(num)
    return num_as_f


def get_next_purchase():  # Find the next thing to purchase
    cheapest = (float("inf"), None)

    # find cheapest product
    products = [driver.find_element_by_id("productPrice" + str(i)) for i in range(1, -1, -1)]
    for product in products:
        product_price = make_float(product.text)
        if product_price <= cheapest[0]:
            cheapest = (product_price, product)

    return cheapest


def get_cookie_count():  # get cookie count
    cookie_count = driver.find_element_by_id("cookies").text.split(" ")[0]
    cookie_count = make_float(cookie_count)
    return cookie_count


if __name__ == "__main__":
    main_loop()
