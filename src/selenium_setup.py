import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from dotenv import load_dotenv


load_dotenv()

def get_driver_path():
    return str(Path(__file__).parent.parent / "utils" / "chromedriver.exe")

def selenium_options():
    #Gère les options du navigateur
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) #Permet de garder le navigateur ouvert après l'exécution du script
    chrome_options.add_argument("--start-maximized") #Ouvre le navigateur en mode plein écran
    return chrome_options

def get_browser():
    return webdriver.Chrome(get_driver_path(), chrome_options=selenium_options())

def account_connection(browser):
    browser.get("https://www.linkedin.com/uas/login")
    browser.find_element(By.ID, 'username').send_keys(os.getenv('LINKEDIN_USERNAME'))
    browser.find_element(By.ID, 'password').send_keys(os.getenv('LINKEDIN_PASSWORD'))
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

def go_to_search_link(browser, link = os.getenv('LINKEDIN_SEARCH_LINK')):
    browser.get(f"{link}&page=1")
    
def list_of_profils(browser):
    li_elements = browser.find_elements(By.CSS_SELECTOR, 'li.reusable-search__result-container div.entity-result')
    for li_element in li_elements:
        connect_or_follow = li_element.find_element(By.CSS_SELECTOR, 'div.entity-result__actions.entity-result__divider').text
        if connect_or_follow == "Se connecter":
            a_element = li_element.find_element(By.CSS_SELECTOR, 'a')
            linkedin_profil_link = a_element.get_attribute('href')
            print(linkedin_profil_link)
            name = a_element.text.strip()
            print(name)

        elif connect_or_follow == "Suivre":
            a_element = li_element.find_element(By.CSS_SELECTOR, 'a.app-aware-link')
            linkedin_profil_link = a_element.get_attribute('href')
            print(linkedin_profil_link)
            name = a_element.text.strip()
            print(name)

def run():
    browser = get_browser()
    account_connection(browser)
    go_to_search_link(browser)
    list_of_profils(browser)


if __name__ == "__main__":
    run()