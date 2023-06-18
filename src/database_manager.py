import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self._create_search_links_infos_table()
        self._create_linkedin_leads_table()

    def _create_search_links_infos_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_links_infos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_page INTEGER DEFAULT 1,
        max_pages INTEGER,
        search_link TEXT
        );
        ''')
        self.conn.commit()

    def _create_linkedin_leads_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS linkedin_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name VARCHAR(100),
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        linkedin_profil_link TEXT UNIQUE,
        connect_or_follow VARCHAR(50),
        is_message_sent BOOLEAN DEFAULT FALSE,
        last_message_sent_at DATETIME DEFAULT NULL,
        search_link_id INTEGER
        );
        ''')
        self.conn.commit()

    def save_lead(self, full_name, first_name, last_name, linkedin_profil_link, connect_or_follow, search_link_id):
        today = datetime.now().date()
        self.cursor.execute(
            "INSERT INTO linkedin_leads (full_name, first_name, last_name, linkedin_profil_link, connect_or_follow, is_message_sent, last_message_sent_at, search_link_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (full_name, first_name, last_name, linkedin_profil_link, connect_or_follow, True, today, search_link_id))
        self.conn.commit()

    def check_lead(self, linkedin_link):
        self.cursor.execute('''SELECT * FROM linkedin_leads WHERE linkedin_profil_link = ?''', (linkedin_link,))
        return bool(result := self.cursor.fetchone())

    def check_number_of_messages_sent_today(self):
        today = datetime.now().date()
        self.cursor.execute('''SELECT * FROM linkedin_leads WHERE last_message_sent_at = ?''', (today,))
        return len(self.cursor.fetchall())

    def check_and_save_link_info(self, link, max_pages):
        current_page = 1
        self.cursor.execute("SELECT * FROM search_links_infos WHERE search_link = ?", (link,))
        result = self.cursor.fetchone()
        if result is None:
            self.cursor.execute(
                "INSERT INTO search_links_infos (search_link, current_page, max_pages) VALUES (?, ?, ?)",
                (link, current_page, max_pages))
            self.conn.commit()

    def get_current_page(self, link):
        self.cursor.execute("SELECT current_page FROM search_links_infos WHERE search_link = ?", (link,))
        return self.cursor.fetchone()[0]
    
    def get_search_link_id(self, link):
        self.cursor.execute("SELECT id FROM search_links_infos WHERE search_link = ?", (link,))
        return self.cursor.fetchone()[0]

    def increment_current_page(self, link):
        self.cursor.execute("UPDATE search_links_infos SET current_page = current_page + 1 WHERE search_link = ?",
                            (link,))
        self.conn.commit()

    #Fonction utile pour ajouter une colonne a une table
    def add_search_link_id_column(self):
        self.cursor.execute('''
        ALTER TABLE linkedin_leads
        ADD COLUMN search_link_id INTEGER;
        ''')
        self.conn.commit()