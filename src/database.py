import sqlite3

def create_search_links_infos_table(cursor, conn):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_links_infos (
    id SERIAL PRIMARY KEY,
    current_page INTEGER DEFAULT 1,
    max_pages INTEGER,
    search_link TEXT
    );
    ''')
    conn.commit()

def create_linkedin_leads_table(cursor, conn):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS linkedin_leads (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    linkedin_profile_link TEXT UNIQUE,
    is_message_sent BOOLEAN DEFAULT FALSE
    );
    ''')
    conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect('linkedin_prospection.db')
    cursor = conn.cursor()
    create_search_links_infos_table(cursor=cursor, conn=conn)
    create_linkedin_leads_table(cursor=cursor, conn=conn)
    conn.close()
