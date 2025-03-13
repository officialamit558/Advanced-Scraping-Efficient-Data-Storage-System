# src/storage/contact_store.py
import mysql.connector
from config.config import Config
import json

class ContactStore:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='@#$Amit1736',
                database='contacts'
            )
            self.cursor = self.conn.cursor()
            self.create_table()
            print("Connected to MySQL and initialized contacts table")
        except mysql.connector.Error as e:
            print(f"Failed to connect to MySQL: {e}")
            raise

    def create_table(self):
        """Create the contacts table if it doesn’t exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    organization VARCHAR(255),
                    email VARCHAR(255) UNIQUE,  -- Added UNIQUE constraint for email
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error creating table: {e}")
            raise

    def save(self, data):
        """Save structured contact data to MySQL."""
        try:
            structured = data.get("structured", [])
            if not structured:
                print("No structured data to save")
                return 0

            inserted_count = 0
            for item in structured:
                # Ensure required fields are present, provide defaults if missing
                name = item.get("name") or "Unknown"
                org = item.get("org") or "Unknown"
                email = item.get("email")
                if not email:  # Skip if no email (assuming email is key identifier)
                    print(f"Skipping contact with no email: {item}")
                    continue

                # Convert metadata to JSON string if present, else empty dict
                metadata = json.dumps(item.get("metadata", {}))

                try:
                    self.cursor.execute("""
                        INSERT INTO contacts (name, organization, email, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            organization = VALUES(organization),
                            metadata = VALUES(metadata)
                    """, (name, org, email, metadata))
                    inserted_count += 1
                except mysql.connector.Error as e:
                    if e.errno == 1062:  # Duplicate entry error
                        print(f"Duplicate email skipped: {email}")
                    else:
                        print(f"Error inserting contact {email}: {e}")

            self.conn.commit()
            print(f"Saved {inserted_count} contacts to MySQL")
            return inserted_count

        except Exception as e:
            print(f"Error saving data: {e}")
            self.conn.rollback()  # Roll back on error
            raise

    def close(self):
        """Close the MySQL connection."""
        try:
            self.cursor.close()
            self.conn.close()
            print("MySQL connection closed")
        except mysql.connector.Error as e:
            print(f"Error closing MySQL connection: {e}")

# Test standalone
if __name__ == "__main__":
    store = ContactStore()
    sample_data = {
        "structured": [
            {"name": "John", "org": "xAI", "email": "john@xai.com", "metadata": {"source": "table"}},
            {"name": "Jane", "org": "xAI", "email": "jane@xai.com", "metadata": {"source": "list"}},
            {"name": "NoEmail", "org": "Unknown"}  # Should be skipped
        ]
    }
    inserted = store.save(sample_data)
    print(f"Inserted {inserted} contacts")
    store.close()