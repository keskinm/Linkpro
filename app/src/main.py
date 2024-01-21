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

    def start(self):

        db_manager = DatabaseManager('linkedin_prospection.db')
        db_manager.create_tables()

        scraper = LinkedinScraper()
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

            if int(current_page)+1 > self.max_pages:
                print("Tous les profils du lien ont été parcourus.")
                break
            if not message_limit_reached :
                db_manager.increment_current_page(self.search_link)

        scraper.close_browser()


if __name__ == "__main__":
    bot = LinkedinBot()
    bot.start()
