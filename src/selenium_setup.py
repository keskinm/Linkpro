import random
import time
from datetime import datetime
import os
from pathlib import Path
from pprint import pprint
import sqlite3
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC

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
    conn = sqlite3.connect('linkedin_prospection.db')
    cursor = conn.cursor()
    cursor.execute("SELECT current_page FROM search_links_infos WHERE search_link = ?", (link,))
    current_page = cursor.fetchone()

    browser.get(f"{link}&page={current_page}")

    conn.close()

#Clique sur le "Se connecter" du "Plus"
def click_connect_on_plus(browser):
    soup = BeautifulSoup(browser.page_source, "html.parser")
    div_plus = soup.find('div', {'class': 'ph5'})
    div_dropdown = div_plus.find('div', {'class': 'artdeco-dropdown__content-inner'}) # type: ignore
    toutli = div_dropdown.find_all('li') # type: ignore
    #Trouver l'id "Se connecter" et cliquer dessus
    for li_textes in toutli:
        try:
            li_texte = li_textes.find('span')
            if li_texte.text.strip() == "Se connecter":
                id_seconnecter = li_textes.find('div')['id']
                browser.find_element(By.ID, id_seconnecter).click() # type: ignore
                WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-modal__actionbar')))
                return
        except:
            continue

def get_all_profil_in_the_page(browser, cursor):
    all_profils_list = browser.find_elements(By.CSS_SELECTOR, 'li.reusable-search__result-container div.entity-result')
    all_profils_info = []
    for profil_content in all_profils_list:
        connect_or_follow = profil_content.find_element(By.CSS_SELECTOR, 'div.entity-result__actions.entity-result__divider').text
        linkedin_profil_link = profil_content.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        if check_database(cursor, linkedin_profil_link):
            continue
        full_name = profil_content.find_element(By.XPATH, './/span[@dir="ltr"]/span[@aria-hidden="true"]').text
        first_name = full_name.split()[0]
        last_name = full_name.split()[1]
        profil = {
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "linkedin_profil_link": linkedin_profil_link,
            "connect_or_follow": connect_or_follow
            }
        all_profils_info.append(profil)
    return all_profils_info

def connect_to_profil(browser):
    conn = sqlite3.connect('linkedin_prospection.db')
    cursor = conn.cursor()
    while check_number_of_message_sent_today(cursor) < int(os.getenv('MAX_MESSAGE_PER_DAY')):
        check_and_save_link_info(conn=conn, cursor=cursor )
        all_profils_info = get_all_profil_in_the_page(browser, cursor)
        
        pprint(all_profils_info)
        for profil in all_profils_info:
            if check_number_of_message_sent_today(cursor) >= int(os.getenv('MAX_MESSAGE_PER_DAY')):
                print("Vous avez atteint le nombre maximum de messages à envoyer aujourd'hui")
                break

            if profil["connect_or_follow"] == "Se connecter":
                browser.get(profil["linkedin_profil_link"])
                connect_button = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pvs-profile-actions button.artdeco-button')))
                connect_button.click()
                add_note = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Ajouter une note"]')))
                add_note.click()
                custom_message = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'custom-message')))
                message = os.getenv('MESSAGE').replace("{first_name}", profil["first_name"])
                custom_message.send_keys(message)
                send_invitation = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Envoyer maintenant"]')))
                send_invitation.click()

            elif profil["connect_or_follow"] == "Suivre":
                browser.get(profil["linkedin_profil_link"])
                plus_action_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pvs-profile-actions button.artdeco-dropdown__trigger')))
                plus_action_button.click()
                click_connect_on_plus(browser)
                add_note = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Ajouter une note"]')))
                add_note.click()
                custom_message = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'custom-message')))
                message = os.getenv('MESSAGE').replace("{first_name}", profil["first_name"])
                custom_message.send_keys(message)
                send_invitation = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Envoyer maintenant"]')))
                send_invitation.click()

            else : 
                print("Erreur")
                print(profil)
                print(50*"-")
                continue

            save_in_db(cursor, conn, profil["full_name"], profil["first_name"], profil["last_name"], profil["linkedin_profil_link"], profil["connect_or_follow"])
            wait_random_time()
        if check_number_of_message_sent_today(cursor) < int(os.getenv('MAX_MESSAGE_PER_DAY')):
            go_to_next_page(browser, cursor, conn)
    conn.commit()
    conn.close()


def wait_random_time():
    wait_time = random.uniform(8, 16)
    time.sleep(wait_time)


def save_in_db(cursor, conn, full_name, first_name, last_name, linkedin_profil_link, connect_or_follow):
    today = datetime.now().date()
    cursor.execute("INSERT INTO linkedin_leads (full_name, first_name, last_name, linkedin_profil_link, connect_or_follow, is_message_sent, last_message_sent_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (full_name, first_name, last_name, linkedin_profil_link, connect_or_follow, True, today))
    conn.commit()
    print(f"Le profil de {full_name} à été sauvegardé en base.")

def check_database(cursor,linkedin_link):
    cursor.execute('''SELECT * FROM linkedin_leads WHERE linkedin_profil_link = ?''', (linkedin_link,))
    return bool(result := cursor.fetchone())

def check_number_of_message_sent_today(cursor):
    today = datetime.now().date()
    cursor.execute('''SELECT * FROM linkedin_leads WHERE last_message_sent_at = ?''', (today,))
    return len(cursor.fetchall())

def save_current_page():
    pass

def check_and_save_link_info(cursor, conn):
    link = os.getenv('LINKEDIN_SEARCH_LINK')
    current_page = 1
    max_pages = os.getenv("MAX_PAGES")
    cursor.execute("SELECT * FROM search_links_infos WHERE search_link = ?", (link,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO search_links_infos (search_link, current_page, max_pages) VALUES (?, ?, ?)", (link, current_page, max_pages ))
        conn.commit()

def go_to_next_page(browser, cursor, conn):
    increment_current_page(cursor, conn)
    link = os.getenv('LINKEDIN_SEARCH_LINK')
    cursor.execute("SELECT current_page FROM search_links_infos WHERE search_link = ?", (link,))
    current_page = cursor.fetchone()
    browser.get(f"{link}&page={current_page}")


def increment_current_page(cursor, conn):
    link = os.getenv('LINKEDIN_SEARCH_LINK')
    cursor.execute("UPDATE search_links_infos SET current_page = current_page + 1 WHERE search_link = ?", (link,))
    conn.commit()


def run():
    browser = get_browser()
    account_connection(browser)
    go_to_search_link(browser)
    connect_to_profil(browser)


if __name__ == "__main__":
    run()