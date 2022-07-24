import random
import time
from selenium.webdriver.common.keys import Keys

def slow_type(element: str, text: str, delay: float=random.uniform(0.1, 0.4)):
    for character in text:
        element.send_keys(character)
        time.sleep(delay)
    return None

def clear_field(element: str, text: int, delay: float=random.uniform(0.01, 0.1)):
    for character in range(text):
        element.send_keys(Keys.BACK_SPACE)
        time.sleep(delay)
    return None

def element_exists(driver: None, path: str):
    try: 
        print('found')
        return driver.find_element_by_xpath(path)
    except:
        return False


def CustomFieldSelect(driver,element):
    return driver.execute_script("arguments[0].click();", driver.find_element_by_xpath(element))