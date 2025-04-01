import psycopg2
from config import DATABASE_URL

def create_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    with open("app/models.sql", "r") as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()

def insert_data():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    with open("app/test.sql", "r") as f:
        cursor.execute(f.read())
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Tables in the database has been created.")
    insert_data()
    print("✅ Data has been inserted.")



