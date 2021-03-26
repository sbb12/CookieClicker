from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome(executable_path="C:/Users/balls/PycharmProjects/chromedriver")

driver.get("https://orteil.dashnet.org/cookieclicker/")
print(driver.title)

actions = ActionChains(driver)
actions.click()

driver.implicitly_wait(5)
cookie = driver.find_element_by_id("bigCookie")
cookie_count = driver.find_element_by_id("cookies").text

while True:
    cookie.click()
    products = [driver.find_element_by_id("productPrice" + str(i)) for i in range(1, -1, -1)]

    cookie_count = driver.find_element_by_id("cookies").text.split(" ")[0]

    # remove delimiter from cookie count
    for i in cookie_count:
        if not i.isdigit():
            cookie_count.replace(i, "")

    for product in products:
        if int(product.text) <= cookie_count:
            upgrade_actions = ActionChains(driver)
            upgrade_actions.move_to_element(product)
            upgrade_actions.click()
            upgrade_actions.perform()


