import sqlite3

def init_db():
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            contact_number TEXT NOT NULL,
            favorite_foods TEXT,
            movies_rating INTEGER,
            radio_rating INTEGER,
            eating_out_rating INTEGER,
            tv_rating INTEGER
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()