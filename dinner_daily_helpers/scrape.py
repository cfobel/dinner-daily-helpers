import enum
import time
from typing import Optional

import chromedriver_binary  # Adds chromedriver binary to path
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.remote.webelement
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .types.menu import Menu
from .types.shopping_list import ShoppingList

__all__ = ["Week", "WeekOption", "scrape_week"]


class WeekOption(str, enum.Enum):
    PREVIOUS = "previous"
    CURRENT = "current"


class LoginFields(BaseModel):
    email: selenium.webdriver.remote.webelement.WebElement
    password: selenium.webdriver.remote.webelement.WebElement
    button: selenium.webdriver.remote.webelement.WebElement

    class Config:
        arbitrary_types_allowed = True


class Session(BaseModel):
    token: str
    refreshToken: str  # XXX TODO: find refresh URL


def shadow(
    browser: selenium.webdriver.chrome.webdriver.WebDriver,
    element: selenium.webdriver.remote.webelement.WebElement,
) -> selenium.webdriver.remote.webelement.WebElement:
    return browser.execute_script("return arguments[0].shadowRoot", element)


def login_fields(
    browser: selenium.webdriver.chrome.webdriver.WebDriver,
) -> LoginFields:
    dd_app = browser.find_element_by_tag_name("dd-app")
    dd_app_shadow_root = shadow(browser, dd_app)
    dd_login = dd_app_shadow_root.find_element_by_tag_name("dd-login")
    dd_login_shadow_root = shadow(browser, dd_login)
    main_fab = shadow(browser, dd_app_shadow_root.find_element_by_id("main-fab"))
    log_in_button = main_fab.find_element_by_tag_name("button")

    def get_input_field(id_: str):
        field = dd_login_shadow_root.find_element_by_id(id_)
        field_shadow_root = shadow(browser, field)
        return field_shadow_root.find_element_by_css_selector("input")

    return LoginFields(
        button=log_in_button,
        **{
            name: get_input_field(f"{ name }-text-field")
            for name in ("email", "password")
        },
    )


def fetch_json(
    browser: selenium.webdriver.chrome.webdriver.WebDriver, session: Session, url: str
) -> dict:
    script = f"""var done = arguments[0];
fetch("{ url }", {{
	method: "GET",
	headers: {{
		"Authorization": "Bearer { session.token }"
	}}
}}).then(function(response) {{
    response.json().then(function(result) {{
        done(result);
    }});
}});"""
    return browser.execute_async_script(script)


class Week(BaseModel):
    menu: Menu
    shopping_list: ShoppingList


def scrape_week(
    username: str,
    password: str,
    week_option: Optional[WeekOption] = WeekOption.CURRENT,
    driver: Optional[selenium.webdriver.chrome.webdriver.WebDriver] = None,
) -> Week:
    if driver is None:
        # The following options are required to make headless Chrome
        # work in a Docker container
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--disable-gpu")
        # Initialize a new driver
        driver = webdriver.Chrome(options=options)
        driver_created = True
    else:
        driver_created = False

    #  https://selenium-python.readthedocs.io/waits.html#implicit-waits
    driver.implicitly_wait(10)
    driver.get("https://app.thedinnerdaily.com")

    login_fields_ = login_fields(driver)

    login_fields_.email.send_keys(username)
    login_fields_.password.send_keys(password)

    login_fields_.button.click()

    # Retry 5 times to read access token from local storage; wait 1 second between
    for i in range(5):
        try:
            local_storage = driver.execute_script("return window.localStorage;")
            session = Session.parse_obj(local_storage)
            break
        except Exception as exception:
            time.sleep(1)
    else:
        raise exception

    base_url = "https://db.thedinnerdaily.com/api/v2"
    menu_url = f"{ base_url }/week-menu?week={ week_option }"
    shopping_list_url = f"{ base_url }/shopping-list?week={ week_option }"

    menu_dict = fetch_json(driver, session, menu_url)
    shopping_list_dict = fetch_json(driver, session, shopping_list_url)

    menu = Menu.parse_obj(menu_dict)
    shopping_list = ShoppingList.parse_obj(shopping_list_dict)
    result = Week(menu=menu, shopping_list=shopping_list)

    if driver_created:
        driver.quit()

    return result
