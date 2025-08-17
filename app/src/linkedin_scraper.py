import random
import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from utils import remove_emojis
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager


class LinkedinScraper:
    def __init__(self):
        load_dotenv()
        self.browser = self._get_browser()

    def _get_browser(self):
        """
        Build the Firefox webdriver. We honour HEADLESS and FIREFOX_BIN
        environment variables and fall back to common binary paths.
        """
        headless = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")
        candidates = [
            os.getenv("FIREFOX_BIN"),
            "/usr/local/bin/firefox-esr",
            "/usr/bin/firefox-esr",
            "/usr/bin/firefox",
            "/snap/bin/firefox",
        ]
        firefox_bin = next((p for p in candidates if p and os.path.exists(p)), None)

        opts = FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        if firefox_bin:
            opts.binary_location = firefox_bin

        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=opts)

    def login(self):
        self.browser.get("https://www.linkedin.com/uas/login")
        self.browser.find_element(By.ID, "username").send_keys(os.getenv("LINKEDIN_USERNAME"))
        self.browser.find_element(By.ID, "password").send_keys(os.getenv("LINKEDIN_PASSWORD"))
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def check_for_authentication(self):
        try:
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, "input__email_verification_pin"))
            )
            print("Two‑factor page detected. Waiting for code…")
            return True
        except Exception:
            return False

    def ensure_authenticated(self):
        if self.check_for_authentication():
            while self.check_for_authentication():
                time.sleep(15)

    def go_to_search_link(self, link, current_page):
        """
        Load the given LinkedIn search URL with &page=… appended.
        We always attempt to accept the cookie consent banner afterwards.
        """
        url = f"{link}&page={current_page}"
        self.browser.get(url)
        self._accept_cookies_if_present()

    def get_all_profiles_on_page(self):
        """
        Extract all available profiles on the current search page.
        We try a set of selectors in case LinkedIn changes its markup.
        Only cards with “Se connecter” or “Suivre” buttons are returned.
        """
        try:
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.reusable-search__result-container"))
            )
        except Exception:
            pass

        selectors = [
            "li.reusable-search__result-container",
            "div.entity-result",
            "div.search-result__info",
        ]
        cards = []
        for sel in selectors:
            cards = self.browser.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                break

        profiles = []
        for card in cards:
            try:
                action_el = card.find_element(
                    By.CSS_SELECTOR, "div.entity-result__actions.entity-result__divider"
                )
                connect_or_follow = action_el.text.strip()
            except Exception:
                continue
            if connect_or_follow not in ("Se connecter", "Suivre"):
                continue

            try:
                linkedin_profile_link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except Exception:
                continue

            try:
                full_name_el = card.find_element(
                    By.CSS_SELECTOR, 'span.entity-result__title-text a span[dir="ltr"]'
                )
                full_name = remove_emojis(full_name_el.text.strip())
            except Exception:
                full_name = ""
            parts = full_name.split()
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""
            profiles.append(
                {
                    "full_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "linkedin_profile_link": linkedin_profile_link,
                    "connect_or_follow": connect_or_follow,
                }
            )
        return profiles

    def go_to_profile_page(self, profile_link):
        self.browser.get(profile_link)

    def is_open_to_work(self):
        try:
            profile_image = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "img.pv-top-card-profile-picture__image")
                )
            )
            if "#OPEN_TO_WORK" in profile_image.get_attribute("alt"):
                return True
        except Exception:
            return False
        return False

    def connect_to_profil(self):
        connect_button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.pvs-profile-actions__action",
                )
            )
        )
        connect_button.click()

    def first_button_text(self):
        button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.pvs-profile-actions__action",
                )
            )
        )
        return button.text

    def send_invitation_with_message(self, message):
        add_note = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[aria-label="Ajouter une note"]')
            )
        )
        add_note.click()
        custom_message = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, "custom-message"))
        )
        custom_message.send_keys(message)
        send_invitation = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[aria-label="Envoyer une invitation"]')
            )
        )
        send_invitation.click()

    def go_to_next_page(self, link, current_page):
        self.browser.get(f"{link}&page={current_page + 1}")

    def wait_random_time(self):
        wait_time = random.uniform(8, 16)
        time.sleep(wait_time)

    def _click_plus(self):
        plus_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label, 'Plus d’actions')]")
            )
        )
        plus_button.click()
        time.sleep(1)

    def click_connect_on_plus(self):
        plus_button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ph5 .artdeco-dropdown__trigger")
            )
        )
        plus_button.click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".artdeco-dropdown__content-inner")
            )
        )
        dropdown_items = self.browser.find_elements(
            By.CSS_SELECTOR, ".artdeco-dropdown__content-inner li div.artdeco-dropdown__item"
        )
        for item in dropdown_items:
            if "Se connecter" in item.text:
                item.click()
                break

    def close_browser(self):
        self.browser.quit()

    def _accept_cookies_if_present(self):
        """
        Close the LinkedIn cookie banner if it appears. Without accepting, the page
        may remain blocked and the results list may not load.
        """
        try:
            accept_btn = WebDriverWait(self.browser, 3).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(text(),'Accepter') or contains(text(),'Accept')]",
                    )
                )
            )
            accept_btn.click()
            time.sleep(1)
        except Exception:
            pass
