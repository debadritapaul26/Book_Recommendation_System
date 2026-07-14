import time
from database import init_db, get_connection 

# A pre-curated, hardcoded starter library (No API required!)
STARTER_LIBRARY = [
    {"category": "Technology", "title": "The Innovators", "author": "Walter Isaacson", "isbn": "9781471138799", "rating": "4.6"},
    {"category": "Technology", "title": "Steve Jobs", "author": "Walter Isaacson", "isbn": "9781451648539", "rating": "4.8"},
    {"category": "Technology", "title": "Hackers", "author": "Steven Levy", "isbn": "9781449328120", "rating": "4.3"},
    {"category": "Sci-Fi", "title": "Dune", "author": "Frank Herbert", "isbn": "9780441172719", "rating": "4.7"},
    {"category": "Sci-Fi", "title": "The Martian", "author": "Andy Weir", "isbn": "9780804139021", "rating": "4.8"},
    {"category": "Sci-Fi", "title": "Foundation", "author": "Isaac Asimov", "isbn": "9780553293357", "rating": "4.5"},
    {"category": "Mystery", "title": "Gone Girl", "author": "Gillian Flynn", "isbn": "9780307588371", "rating": "4.1"},
    {"category": "Mystery", "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "isbn": "9780307454546", "rating": "4.4"},
    {"category": "Mystery", "title": "The Girl on the Train", "author": "Paula Hawkins", "isbn": "9780316558990", "rating": "4.0"},
    {"category": "Fantasy", "title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "9780547928227", "rating": "4.9"},
    {"category": "Fantasy", "title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "isbn": "9780590353427", "rating": "4.8"},
    {"category": "Fantasy", "title": "A Game of Thrones", "author": "George R.R. Martin", "isbn": "9780553593716", "rating": "4.7"},
    {"category": "Psychology", "title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "isbn": "9780374533557", "rating": "4.6"},
    {"category": "Psychology", "title": "Quiet", "author": "Susan Cain", "isbn": "9780307352156", "rating": "4.5"},
    {"category": "Biography", "title": "Educated", "author": "Tara Westover", "isbn": "9780399590504", "rating": "4.7"},
    {"category": "Biography", "title": "Becoming", "author": "Michelle Obama", "isbn": "9781524763138", "rating": "4.8"},
    {"category": "Biography", "title": "The Diary of a Young Girl", "author": "Anne Frank", "isbn": "9780553296983", "rating": "4.7"},
    {"category": "Self-Help", "title": "Atomic Habits", "author": "James Clear", "isbn": "9780735211292", "rating": "4.8"},
    {"category": "Self-Help", "title": "The Power of Habit", "author": "Charles Duhigg", "isbn": "9780812981605", "rating": "4.6"},
    {"category": "Self-Help", "title": "How to Win Friends and Influence People", "author": "Dale Carnegie", "isbn": "9780671027032", "rating": "4.7"},
    {"category": "Computer Science", "title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", "rating": "4.7"},
    {"category": "Computer Science", "title": "The Pragmatic Programmer", "author": "Andrew Hunt and David Thomas", "isbn": "9780201616224", "rating": "4.8"},
    {"category": "Computer Science", "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "isbn": "9780262033848", "rating": "4.5"},
    {"category": "History", "title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "isbn": "9780062316097", "rating": "4.7"},
    {"category": "History", "title": "Guns, Germs, and Steel", "author": "Jared Diamond", "isbn": "9780393354324", "rating": "4.5"},
    {"category": "History", "title": "The Wright Brothers", "author": "David McCullough", "isbn": "9781476728759", "rating": "4.6"},
    {"category": "Philosophy", "title": "Meditations", "author": "Marcus Aurelius", "isbn": "9780486298238", "rating": "4.7"},
    {"category": "Philosophy", "title": "The Republic", "author": "Plato", "isbn": "9780140455113", "rating": "4.6"},
    {"category": "Philosophy", "title": "Beyond Good and Evil", "author": "Friedrich Nietzsche", "isbn": "9780140449235", "rating": "4.5"},
    {"category": "Adventure", "title": "The Call of the Wild", "author": "Jack London", "isbn": "9781503215153", "rating": "4.4"},
    {"category": "Adventure", "title": "Into the Wild", "author": "Jon Krakauer", "isbn": "9780385486804", "rating": "4.6"},
    {"category": "Adventure", "title": "Life of Pi", "author": "Yann Martel", "isbn": "9780156027328", "rating": "4.7"},
    {"category": "Social", "title": "The Tipping Point", "author": "Malcolm Gladwell", "isbn": "9780316346627", "rating": "4.5"},
    {"category": "Social", "title": "Outliers", "author": "Malcolm Gladwell", "isbn": "9780316017923", "rating": "4.6"},
    {"category": "Social", "title": "Freakonomics", "author": "Steven D. Levitt and Stephen J. Dubner", "isbn": "9780060731335", "rating": "4.4"},
    {"category": "Drama", "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780061120084", "rating": "4.8"},
    {"category": "Drama", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "rating": "4.4"},
    {"category": "Drama", "title": "1984", "author": "George Orwell", "isbn": "9780451524935", "rating": "4.7"},
    {"category": "Romance", "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9781503290563", "rating": "4.8"},
    {"category": "Romance", "title": "The Notebook", "author": "Nicholas Sparks", "isbn": "9780446605236", "rating": "4.5"},
    {"category": "Romance", "title": "Me Before You", "author": "Jojo Moyes", "isbn": "9780143124542", "rating": "4.6"},
    {"category": "Thriller", "title": "The Da Vinci Code", "author": "Dan Brown", "isbn": "9780307474278", "rating": "4.3"},
    {"category": "Thriller", "title": "The Silence of the Lambs", "author": "Thomas Harris", "isbn": "9780312924584", "rating": "4.5"},
    {"category": "Thriller", "title": "Shutter Island", "author": "Dennis Lehane", "isbn": "9781416550602", "rating": "4.4"},
    {"category": "Science fiction", "title": "Dune", "author": "Frank Herbert", "isbn": "9780441172023", "rating": "4.5"},
    {"category": "Science fiction", "title": "Ender's Game", "author": "Orson Scott Card", "isbn": "9780812550702", "rating": "4.6"},
    {"category": "Science fiction", "title": "Neuromancer", "author": "William Gibson", "isbn": "9780441569595", "rating": "4.3"},
    {"category": "Detective", "title": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle", "isbn": "9781505255607", "rating": "4.6"},
    {"category": "Detective", "title": "Murder on the Orient Express", "author": "Agatha Christie", "isbn": "9780062693662", "rating": "4.7"},  
    {"category": "Detective", "title": "The Maltese Falcon", "author": "Dashiell Hammett", "isbn": "9780394703654", "rating": "4.5"},
  
  
    
]

def seed_database():
    print("Building database tables in the Cloud...")
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materials') 
    
    print("\n🚀 Injecting offline starter library into PostgreSQL...\n")
    
    for book in STARTER_LIBRARY:
        cursor.execute('''
            INSERT INTO materials (category, title, author, isbn, rating)
            VALUES (%s, %s, %s, %s, %s)
        ''', (book["category"], book["title"], book["author"], book["isbn"], book["rating"]))
    
    conn.commit()
    conn.close()
    print(f"🎉 SUCCESS! Saved {len(STARTER_LIBRARY)} books to your Cloud Database.")

if __name__ == '__main__':
    seed_database()