import sqlite3

conn = sqlite3.connect('linkedin_prospection.db')

cursor = conn.cursor()

def create_search_links_infos_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS search_links_infos (

                    id SERIAL PRIMARY KEY,
                    current_page INTEGER DEFAULT 1,
                    max_pages INTEGER,
                    search_link TEXT,
                        );
                    ''')
    conn.commit()

def create_linkedin_leads_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS linkedin_leads (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    linkedin_profile_link TEXT UNIQUE,
    message_sent BOOLEAN DEFAULT FALSE,
    );
    ''')
    conn.commit()


conn.close()
