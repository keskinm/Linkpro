import os
from pathlib import Path
from .database_manager import DatabaseManager
from .linkedin_scraper import LinkedinScraper

def get_driver_path():
    return str(Path(__file__).parent.parent / "utils" / "chromedriver.exe")

class LinkedinBot:
    def __init__(self, username, password, search_link, max_pages, max_messages, message):
        self.username = username
        self.password = password
        self.search_link = search_link
        self.max_pages = max_pages
        self.max_messages = max_messages
        self.message = message

    def start(self):
        os.environ["LINKEDIN_USERNAME"] = self.username
        os.environ["LINKEDIN_PASSWORD"] = self.password
        os.environ["LINKEDIN_SEARCH_LINK"] = self.search_link
        os.environ["MAX_PAGES"] = str(self.max_pages)
        os.environ["MAX_MESSAGE_PER_DAY"] = str(self.max_messages)
        os.environ["MESSAGE"] = self.message

        db_manager = DatabaseManager('linkedin_prospection.db')
        db_manager.create_tables()

        scraper = LinkedinScraper(get_driver_path())
        scraper.login()

        db_manager.check_and_save_link_info(self.search_link, self.max_pages)
        search_link_id = db_manager.get_search_link_id(self.search_link)

        message_limit_reached = False
        for _ in range(self.max_pages):
            if message_limit_reached:
                break
            current_page = db_manager.get_current_page(self.search_link)
            scraper.go_to_search_link(self.search_link, current_page)

            profiles = scraper.get_all_profiles_on_page()
            for profile in profiles:
                if db_manager.check_number_of_messages_sent_today() >= self.max_messages:
                    print("Vous avez atteint le nombre maximum de messages à envoyer aujourd'hui")
                    message_limit_reached = True
                    break

                if (not db_manager.check_lead(profile["linkedin_profile_link"])) and (profile["connect_or_follow"]):
                    if profile["connect_or_follow"] == "Se connecter":
                        scraper.connect_to_profil(profile["linkedin_profile_link"])
                    elif profile["connect_or_follow"] == "Suivre":
                        scraper.click_connect_on_plus(profile["linkedin_profile_link"])
                    else:
                        continue
                    scraper.send_invitation_with_message(self.message.replace("{first_name}", profile["first_name"]))
                    db_manager.save_lead(profile["full_name"], profile["first_name"], profile["last_name"], profile["linkedin_profile_link"], profile["connect_or_follow"], search_link_id)
                    scraper.wait_random_time()
            if not message_limit_reached and int(current_page)+1 < self.max_pages:
                db_manager.increment_current_page(self.search_link)
            else:
                message_limit_reached = True
                print("Tous les profils du lien ont été parcourus.")
                break

        scraper.close_browser()
