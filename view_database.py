import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_PATH = "path_to_your_database.db"  # Replace with the actual path to your database


def create_tables():
    """
    Create the 'headings' and 'paragraphs' tables if they don't exist.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create 'headings' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS headings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        );
        """)

        # Create 'paragraphs' table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        );
        """)

        conn.commit()
        conn.close()
        logging.info("Tables created successfully (if they didn't already exist).")
    except sqlite3.Error as e:
        logging.error(f"Error creating tables: {e}")


def populate_tables():
    """
    Insert sample data into 'headings' and 'paragraphs' tables for testing.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if data already exists in 'headings'
        cursor.execute("SELECT COUNT(*) FROM headings")
        headings_count = cursor.fetchone()[0]

        # Check if data already exists in 'paragraphs'
        cursor.execute("SELECT COUNT(*) FROM paragraphs")
        paragraphs_count = cursor.fetchone()[0]

        if headings_count == 0:
            # Insert sample data into 'headings'
            cursor.execute("INSERT INTO headings (content) VALUES ('Sample Heading 1')")
            cursor.execute("INSERT INTO headings (content) VALUES ('Sample Heading 2')")

        if paragraphs_count == 0:
            # Insert sample data into 'paragraphs'
            cursor.execute("INSERT INTO paragraphs (content) VALUES ('Sample paragraph content 1.')")
            cursor.execute("INSERT INTO paragraphs (content) VALUES ('Sample paragraph content 2.')")

        conn.commit()
        conn.close()
        logging.info("Sample data inserted successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error inserting sample data: {e}")


def fetch_data():
    """
    Fetch data from the 'headings' and 'paragraphs' tables and print it.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch data from 'headings' table
        cursor.execute("SELECT * FROM headings")
        headings = cursor.fetchall()

        # Fetch data from 'paragraphs' table
        cursor.execute("SELECT * FROM paragraphs")
        paragraphs = cursor.fetchall()

        conn.close()

        if not headings and not paragraphs:
            logging.error("No data available in the database.")
            return None, None

        logging.info("Data fetched successfully.")
        return headings, paragraphs
    except sqlite3.Error as e:
        logging.error(f"Error fetching data from database: {e}")
        return None, None


def main():
    """
    Main script to create tables, populate data (optional), and fetch data.
    """
    logging.debug("Starting the script...")

    # Step 1: Create missing tables
    create_tables()

    # Step 2: Populate tables with sample data (optional for testing)
    populate_tables()

    # Step 3: Fetch and display data
    headings, paragraphs = fetch_data()
    if headings and paragraphs:
        print("\nHeadings:")
        for heading in headings:
            print(f"ID: {heading[0]}, Content: {heading[1]}")

        print("\nParagraphs:")
        for paragraph in paragraphs:
            print(f"ID: {paragraph[0]}, Content: {paragraph[1]}")
    else:
        logging.error("No data available for summarization.")


if __name__ == "__main__":
    main()
