import random
import time
import os
from selenium.common.exceptions import TimeoutException
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
            print("Two-factor page detected. Waiting for code…")
            return True
        except Exception:
            return False

    def ensure_authenticated(self):
        if self.check_for_authentication():
            while self.check_for_authentication():
                time.sleep(15)

    def _accept_cookies_if_present(self):
        try:
            accept_btn = WebDriverWait(self.browser, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Accepter') or contains(text(),'Accept')]")
                )
            )
            accept_btn.click()
            time.sleep(1)
        except Exception:
            pass

    def go_to_search_link(self, link, current_page):
        url = f"{link}&page={current_page}"
        self.browser.get(url)
        self._accept_cookies_if_present()

    def get_all_profiles_on_page(self):
        """
        Find every profile link on the page and return a list of dicts with name, first_name,
        last_name and linkedin_profile_link. We default connect_or_follow to 'Se connecter'
        because we will decide what to do on the profile page itself.
        """
        # Wait for at least one profile link to appear
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/in/']"))
        )
        anchors = self.browser.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
        profiles = []
        seen = set()
        for a in anchors:
            href = a.get_attribute("href")
            if not href or "/in/" not in href or href in seen:
                continue
            seen.add(href)
            full_name = remove_emojis(a.text.strip())
            parts = full_name.split()
            first_name = parts[0] if parts else ""
            last_name = parts[1] if len(parts) > 1 else ""
            profiles.append(
                {
                    "full_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "linkedin_profile_link": href,
                    "connect_or_follow": "Se connecter",
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
        """
        Retrieve the connection/follow button via its aria-label or inner text.
        Normalises the label to 'Se connecter' or 'Suivre'.
        """
        try:
            button = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//button[contains(@aria-label,'Invitez') or "
                    "contains(@aria-label,'Se connecter') or "
                    "contains(@aria-label,'Connect') or "
                    "contains(@aria-label,'Suivre') or "
                    "contains(@aria-label,'Follow')]"
                ))
            )
            label = button.get_attribute("aria-label") or ""
            if not label:
                try:
                    label = button.find_element(
                        By.CSS_SELECTOR, "span.artdeco-button__text"
                    ).text.strip()
                except Exception:
                    label = ""
            if not label:
                label = button.text.strip()
        except TimeoutException:
            return "Se connecter"

        lower = label.lower()
        if "suivre" in lower or "follow" in lower:
            return "Suivre"
        if "invitez" in lower or "connect" in lower or "se connecter" in lower:
            return "Se connecter"
        return label.split()[0]

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
        time.sleep(random.uniform(8, 16))

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
            if "Se connecter" in item.text or "Connect" in item.text:
                item.click()
                break

    def close_browser(self):
        self.browser.quit()
