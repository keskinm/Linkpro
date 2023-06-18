from pathlib import Path
from pprint import pprint
import time

from database_manager import DatabaseManager
from linkedin_scraper import LinkedinScraper
import os


def get_driver_path():
    return str(Path(__file__).parent.parent / "utils" / "chromedriver.exe")


if __name__ == "__main__":
    db_manager = DatabaseManager('linkedin_prospection.db')
    db_manager.create_tables()

    scraper = LinkedinScraper(get_driver_path())
    scraper.login()

    link = os.getenv('LINKEDIN_SEARCH_LINK')
    max_pages = int(os.getenv("MAX_PAGES")) # type: ignore

    db_manager.check_and_save_link_info(link, max_pages)

    message_limit_reached = False
    for _ in range(max_pages):
        if message_limit_reached:
            break
        current_page = db_manager.get_current_page(link)[0]
        scraper.go_to_search_link(link, current_page)

        profils = scraper.get_all_profiles_on_page()
        for profil in profils:
            if db_manager.check_number_of_messages_sent_today() >= int(os.getenv('MAX_MESSAGE_PER_DAY')): # type: ignore
                print("Vous avez atteint le nombre maximum de messages à envoyer aujourd'hui")
                message_limit_reached = True
                break

            if (not db_manager.check_lead(profil["linkedin_profile_link"])) and (profil["connect_or_follow"]):
                if profil["connect_or_follow"] == "Se connecter":
                    scraper.connect_to_profil(profil["linkedin_profile_link"])
                elif profil["connect_or_follow"] == "Suivre":
                    scraper.click_connect_on_plus(profil["linkedin_profile_link"])
                else:
                    continue
                scraper.send_invitation_with_message(os.getenv('MESSAGE').replace("{first_name}", profil["first_name"]))
                db_manager.save_lead(profil["full_name"], profil["first_name"], profil["last_name"], profil["linkedin_profile_link"], profil["connect_or_follow"])
                scraper.wait_random_time()
        if not message_limit_reached:
            db_manager.increment_current_page(link)

    scraper.close_browser()
