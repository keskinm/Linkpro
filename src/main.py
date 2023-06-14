from pathlib import Path

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
    max_pages = int(os.getenv("MAX_PAGES"))

    db_manager.check_and_save_link_info(link, max_pages)

    message_limit_reached = False
    for _ in range(max_pages):
        if message_limit_reached:
            break
        current_page = db_manager.get_current_page(link)
        scraper.go_to_search_link(link, current_page)

        profiles = scraper.get_all_profiles_on_page()
        for profile in profiles:
            if not db_manager.check_lead(profile["linkedin_profile_link"]):
                scraper.connect_to_profile(profile["linkedin_profile_link"])
                scraper.send_invitation_with_message(os.getenv('MESSAGE').replace("{first_name}", profile["first_name"]))
                db_manager.save_lead(profile["full_name"], profile["first_name"], profile["last_name"], profile["linkedin_profile_link"], profile["connect_or_follow"])
                scraper.wait_random_time()
        if not message_limit_reached:
            db_manager.increment_current_page(link)

    scraper.close_browser()
