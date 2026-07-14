import json
import time
from google import genai
from database import init_db, get_connection 

CATEGORIES = [
    "Technology", "Mystery", "Sci-Fi", "Fantasy", "Romance", 
    "Thriller", "History", "Philosophy", "Science fiction", "Adventure", 
    "Biography", "Self-Help", "Computer Science", "Social", "Drama", "Psychology", "Detective"
]

# 🚨 PUT YOUR GEMINI API KEY HERE 🚨
client = genai.Client(api_key="AQ.Ab8RN6JcSsQycUCAfbzb7ldHRDkadcdHJYlvOxjXZ-oajTiU2w")

def ask_ai_for_books(category):
    print(f"🧠 Asking AI Librarian to write 40 books for {category}...")
    
    prompt = f"""
    You are a massive database of books. Generate exactly 40 famous and popular real books for the category: {category}.
    You MUST respond exclusively with a valid raw JSON array containing exactly 40 objects.
    Each object must have these exact keys:
    - "title": Book title
    - "author": Author name
    - "isbn": A real 13-digit ISBN number for this book (no dashes).
    - "rating": A string representing a rating between "4.0" and "4.9".
    Do not wrap the response in markdown code blocks. Return pure text JSON.
    """
    
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            clean_text = response.text.strip().strip("`").replace("json", "", 1).strip()
            books = json.loads(clean_text)
            
            for book in books:
                book["category"] = category
            return books
            
        except Exception as e:
            print(f"  ⚠️ AI Formatting Error. Retrying... ({e})")
            time.sleep(2)
            
    return []

def seed_database():
    print("Building database tables in the Cloud...")
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materials') 
    
    total_books = 0
    print("\n🚀 Booting up Gemini AI to generate your Cloud Database...\n")
    
    for category in CATEGORIES:
        books = ask_ai_for_books(category)
        
        for book in books:
            title = book.get("title", "Unknown")
            author = book.get("author", "Unknown")
            isbn = book.get("isbn", "0")
            rating = book.get("rating", "4.5")
            
            cursor.execute('''
                INSERT INTO materials (category, title, author, isbn, rating)
                VALUES (%s, %s, %s, %s, %s)
            ''', (category, title, author, isbn, rating))
        
        conn.commit()
        total_books += len(books)
        print(f"✅ Saved {len(books)} AI-generated books to {category}. (Total so far: {total_books})\n")
        
        time.sleep(5)
        
    conn.close()
    print(f"🎉 SUCCESS! Your AI successfully wrote a library of {total_books} books to the Cloud.")

if __name__ == '__main__':
    seed_database()