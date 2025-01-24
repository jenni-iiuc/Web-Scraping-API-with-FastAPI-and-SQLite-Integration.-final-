import sys
import io
import sqlite3
from bs4 import BeautifulSoup
import cloudscraper
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Initialize FastAPI app
app = FastAPI()

# SQLite database path
DB_PATH = r"C:\Users\Asus\Final Project\Project\scraped_data.db"

# Database Initialization
def init_database():
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
        except sqlite3.DatabaseError:
            print("Invalid database file found. Replacing with a new one.")
            os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS headings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            href TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Scrape the website
def scrape_website(url):
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_title = soup.title.string if soup.title else "No Title Found"
            print(f"Page Title: {page_title}")

            data = {
                "headings": [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])],
                "paragraphs": [p.get_text(strip=True) for p in soup.find_all("p")],
                "images": [img["src"] for img in soup.find_all("img") if img.get("src")],
                "links": [
                    {"text": a.get_text(strip=True), "href": a["href"]}
                    for a in soup.find_all("a", href=True)
                    if "mailto:" not in a["href"]
                ],
            }
            return data
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while scraping the website: {e}")
        return None

# Store data into the database
def store_data(conn, data):
    try:
        cursor = conn.cursor()

        for heading in data["headings"]:
            cursor.execute("INSERT INTO headings (content) VALUES (?)", (heading,))
        
        for paragraph in data["paragraphs"]:
            cursor.execute("INSERT INTO paragraphs (content) VALUES (?)", (paragraph,))
        
        for img in data["images"]:
            cursor.execute("INSERT INTO images (src) VALUES (?)", (img,))
        
        for link in data["links"]:
            cursor.execute("INSERT INTO links (text, href) VALUES (?, ?)", (link["text"], link["href"]))
        
        conn.commit()
        print("Data has been successfully stored in the database.")
    except Exception as e:
        print(f"An error occurred while storing data in the database: {e}")

# Summarize content (Placeholder for LLaMA/Groq Cloud API integration)
def summarize_content(paragraphs: List[str]) -> str:
    # Placeholder for external API call to Groq Cloud or LLaMA model
    # For now, we'll just concatenate the paragraphs and return the first 200 characters
    content = " ".join(paragraphs)
    return content[:200] + "..." if len(content) > 200 else content

# FastAPI Endpoints
@app.get("/data/raw")
def get_raw_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM paragraphs")
    paragraphs = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT content FROM headings")
    headings = [row[0] for row in cursor.fetchall()]

    conn.close()
    return {"headings": headings, "paragraphs": paragraphs}

@app.get("/data/summarized")
def get_summarized_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM paragraphs")
    paragraphs = [row[0] for row in cursor.fetchall()]

    conn.close()
    summary = summarize_content(paragraphs)
    return {"summary": summary}

@app.get("/data/paragraphs")
def get_paragraphs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM paragraphs")
    paragraphs = [row[0] for row in cursor.fetchall()]

    conn.close()
    return {"paragraphs": paragraphs}

@app.get("/data/headings")
def get_headings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT content FROM headings")
    headings = [row[0] for row in cursor.fetchall()]

    conn.close()
    return {"headings": headings}

# Main script
if __name__ == "__main__":
    # Initialize database connection
    conn = init_database()
    
    # URL to scrape
    url = "https://dailyamardesh.com/business"

    # Scrape the website
    print("Scraping the website...")
    scraped_data = scrape_website(url)

    if scraped_data:
        # Store scraped data into the database
        print("Storing data in the database...")
        store_data(conn, scraped_data)
    else:
        print("No data to store.")

    # Close the database connection
    conn.close()
