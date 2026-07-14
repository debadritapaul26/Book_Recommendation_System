import os
import json
import random
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai

from database import (
    init_db, save_logs, fetch_history, 
    create_user, get_user_by_email, update_password, 
    get_all_materials
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_developer_key")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# 🚨 PUT YOUR EMAIL CREDENTIALS HERE 🚨
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)
init_db()

# 🚨 PUT YOUR GEMINI API KEY HERE 🚨
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def send_otp_email(email, otp):
    try:
        msg = Message("Your AI Librarian Login OTP", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Your One-Time Password is: {otp}\n\nThis will expire soon. Do not share it with anyone."
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email failed to send: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    current_recommendations = None
    if request.method == 'POST':
        user_query = request.form.get('query')
        if user_query:
            try:
                prompt = f"""
                You are a professional book recommender. Based on this request: "{user_query}", 
                suggest exactly THREE great books. 
                You must respond exclusively with a valid raw JSON array containing three objects:
                [{{ "title": "Title", "author": "Author", "reason": "Reason.", "rating": "4.5/5", "isbn": "ISBN" }}]
                Do not wrap the response in markdown code blocks.
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                clean_text = response.text.strip().strip("`").replace("json", "", 1).strip()
                data = json.loads(clean_text)
                
                save_logs(user_query, data)
                current_recommendations = data
                
            except Exception as e:
                current_recommendations = [{"title": "System Error", "author": "N/A", "reason": str(e), "rating": "0/0", "isbn": "0"}]

    history = fetch_history()
    return render_template('index.html', recommendations=current_recommendations, history=history)

@app.route('/materials')
def materials():
    categories = ["All", "Technology", "Mystery", "Sci-Fi", "Fantasy", "Romance", 
                  "Thriller", "History", "Philosophy", "Science", "Adventure", 
                  "Biography", "Self-Help", "Computer Science", "Social", "Drama", "Psychology"]
    selected_category = request.args.get('category', 'All')
    books = get_all_materials(selected_category)
    return render_template('materials.html', categories=categories, books=books, selected_category=selected_category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if action == 'register':
            hashed_pw = generate_password_hash(password)
            if create_user(email, hashed_pw):
                flash("Account created! Please log in.", "success")
            else:
                flash("Email already exists.", "error")
            return redirect(url_for('login'))
            
        elif action == 'login':
            user = get_user_by_email(email)
            if user and check_password_hash(user[1], password):
                otp = str(random.randint(100000, 999999))
                session['temp_email'] = email
                session['otp'] = otp
                send_otp_email(email, otp)
                print(f"\n--- [DEVELOPER LOG] OTP FOR {email} IS: {otp} ---\n") 
                return redirect(url_for('verify'))
            else:
                flash("Invalid email or password.", "error")
                
    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp_email' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session.get('otp'):
            session['logged_in'] = True
            session['email'] = session.get('temp_email')
            session.pop('temp_email', None)
            session.pop('otp', None)
            return redirect(url_for('index'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            
    return render_template('verify.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)
        if user:
            otp = str(random.randint(100000, 999999))
            session['reset_email'] = email
            session['reset_otp'] = otp
            send_otp_email(email, otp)
            print(f"\n--- [DEVELOPER LOG] RESET OTP FOR {email} IS: {otp} ---\n")
            return redirect(url_for('reset_password'))
        else:
            flash("If that email exists, an OTP was sent.", "info") 
            
    return render_template('forgot.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        new_password = request.form.get('new_password')
        if user_otp == session.get('reset_otp'):
            hashed_pw = generate_password_hash(new_password)
            update_password(session['reset_email'], hashed_pw)
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            flash("Password successfully reset! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Invalid OTP.", "error")
            
    return render_template('reset.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)