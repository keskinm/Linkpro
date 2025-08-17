import os

from dotenv import load_dotenv

from database_manager import DatabaseManager
from linkedin_scraper import LinkedinScraper

load_dotenv()


class LinkedinBot:
    def __init__(self):
        self.username = os.getenv("LINKEDIN_USERNAME")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.search_link = os.getenv("LINKEDIN_SEARCH_LINK")
        self.max_pages = int(os.getenv("MAX_PAGES"))
        self.max_messages = int(os.getenv("MAX_MESSAGE_PER_DAY"))
        self.message = os.getenv("MESSAGE")
        self.check_open_to_work = os.getenv("CHECK_OPEN_TO_WORK", "False") == "True"

    def start(self):

        db_manager = DatabaseManager('linkedin_prospection.db')
        db_manager.create_tables()

        scraper = LinkedinScraper()
        scraper.login()
        scraper.ensure_authenticated()

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
                print(f"Nombre de message envoyé aujourd'hui : {db_manager.check_number_of_messages_sent_today()}")
                if db_manager.check_number_of_messages_sent_today() >= self.max_messages:
                    print("Vous avez atteint le nombre maximum de messages à envoyer aujourd'hui")
                    message_limit_reached = True
                    break

                if (not db_manager.check_lead(profile["linkedin_profile_link"])) and (profile["connect_or_follow"]):
                    scraper.go_to_profile_page(profile["linkedin_profile_link"])
                    if self.check_open_to_work and scraper.is_open_to_work():
                        continue
                    first_button = scraper.first_button_text()
                    did_connect = False
                    try:
                        if (profile["connect_or_follow"] == "Se connecter") and (first_button == "Se connecter"):
                            scraper.connect_to_profil()
                            did_connect = True
                        elif (profile["connect_or_follow"] == "Suivre") or (first_button == "Suivre"):
                            scraper.click_connect_on_plus()
                            did_connect = True
                    except Exception as exc:
                        continue
                    if did_connect:
                        scraper.send_invitation_with_message(self.message.replace("{first_name}", profile["first_name"]))
                        db_manager.save_lead(
                            profile["full_name"],
                            profile["first_name"],
                            profile["last_name"],
                            profile["linkedin_profile_link"],
                            profile["connect_or_follow"],
                            search_link_id
                        )
                        scraper.wait_random_time()

            if int(current_page)+1 > self.max_pages:
                print("Tous les profils du lien ont été parcourus.")
                break
            if not message_limit_reached :
                db_manager.increment_current_page(self.search_link)

        scraper.close_browser()


if __name__ == "__main__":
    bot = LinkedinBot()
    bot.start()
