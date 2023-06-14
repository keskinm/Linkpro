import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from pathlib import Path

class LinkedinScraper:
    def __init__(self, driver_path):
        load_dotenv()
        self.browser = self._get_browser(driver_path)

    def _get_browser(self, driver_path):
        return webdriver.Chrome(driver_path, chrome_options=self._selenium_options())

    def _selenium_options(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--start-maximized")
        return chrome_options

    def login(self):
        self.browser.get("https://www.linkedin.com/uas/login")
        self.browser.find_element(By.ID, 'username').send_keys(os.getenv('LINKEDIN_USERNAME'))
        self.browser.find_element(By.ID, 'password').send_keys(os.getenv('LINKEDIN_PASSWORD'))
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def go_to_search_link(self, link, current_page):
        self.browser.get(f"{link}&page={current_page}")

    def get_all_profiles_on_page(self):
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.reusable-search__result-container div.entity-result')))
        all_profiles_list = self.browser.find_elements(By.CSS_SELECTOR,
                                                       'li.reusable-search__result-container div.entity-result')
        all_profiles_info = []
        for profile_content in all_profiles_list:
            connect_or_follow = profile_content.find_element(By.CSS_SELECTOR,
                                                             'div.entity-result__actions.entity-result__divider').text
            linkedin_profile_link = profile_content.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            full_name = profile_content.find_element(By.XPATH, './/span[@dir="ltr"]/span[@aria-hidden="true"]').text
            first_name = full_name.split()[0]
            last_name = full_name.split()[1]
            profile = {
                "full_name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "linkedin_profile_link": linkedin_profile_link,
                "connect_or_follow": connect_or_follow
            }
            all_profiles_info.append(profile)
        return all_profiles_info

    def connect_to_profile(self, profile_link):
        self.browser.get(profile_link)
        connect_button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.pvs-profile-actions button.artdeco-button')))
        connect_button.click()

    def send_invitation_with_message(self, message):
        add_note = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Ajouter une note"]')))
        add_note.click()
        custom_message = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'custom-message')))
        custom_message.send_keys(message)
        send_invitation = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Envoyer maintenant"]')))
        send_invitation.click()

    def go_to_next_page(self, link, current_page):
        self.browser.get(f"{link}&page={current_page + 1}")

    def wait_random_time(self):
        wait_time = random.uniform(8, 16)
        time.sleep(wait_time)

    def click_connect_on_plus(self):
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        div_plus = soup.find('div', {'class': 'ph5'})
        div_dropdown = div_plus.find('div', {'class': 'artdeco-dropdown__content-inner'})  # type: ignore
        toutli = div_dropdown.find_all('li')  # type: ignore
        # Trouver l'id "Se connecter" et cliquer dessus
        for li_textes in toutli:
            try:
                li_texte = li_textes.find('span')
                if li_texte.text.strip() == "Se connecter":
                    id_seconnecter = li_textes.find('div')['id']
                    self.browser.find_element(By.ID, id_seconnecter).click()  # type: ignore
                    WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-modal__actionbar')))
                    return
            except:
                continue
