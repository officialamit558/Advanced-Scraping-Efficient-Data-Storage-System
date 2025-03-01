# MySQL for contacts
# src/storage/contact_store.py
import mysql.connector
from config.config import Config

class ContactStore:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="user",
            password="password",
            database="contacts",
            port=3306
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                organization VARCHAR(255),
                email VARCHAR(255),
                metadata JSON
            )
        """)
        self.conn.commit()

    def save(self, data):
        structured = data.get("structured", [])
        for item in structured:  # Assume structured is a list of dicts
            self.cursor.execute("""
                INSERT INTO contacts (name, organization, email, metadata)
                VALUES (%s, %s, %s, %s)
            """, (
                item.get("name"),
                item.get("org"),
                item.get("email"),
                '{}'  # MySQL supports JSON; empty dict as string
            ))
        self.conn.commit()

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    store = ContactStore()
    store.save({"structured": [{"name": "John", "org": "xAI", "email": "john@xai.com"}]})
    store.close()