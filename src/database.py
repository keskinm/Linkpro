import sqlite3


def create_search_links_infos_table(cursor, conn):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_links_infos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    current_page INTEGER DEFAULT 1,
    max_pages INTEGER,
    search_link TEXT
    );
    ''')
    conn.commit()


def create_linkedin_leads_table(cursor, conn):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS linkedin_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    linkedin_profil_link TEXT UNIQUE,
    connect_or_follow VARCHAR(50),
    is_message_sent BOOLEAN DEFAULT FALSE,
    last_message_sent_at DATETIME DEFAULT NULL
    );
    ''')
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect('../linkedin_prospection.db')
    cursor = conn.cursor()
    create_search_links_infos_table(cursor=cursor, conn=conn)
    create_linkedin_leads_table(cursor=cursor, conn=conn)
    conn.close()
