import time
from bs4 import BeautifulSoup
from selenium import webdriver

def getSchoolAddress(driver,school):
    driver.get('https://www.google.com/search?hl=en&q=' + school)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    address = soup.find('div', {'data-attrid': 'kc:/location/location:address'})
    driver.execute_script("window.scrollTo(0, 700)")
    time.sleep(1)
    if address:
        print(address.get_text())
        return address.get_text()
    return None