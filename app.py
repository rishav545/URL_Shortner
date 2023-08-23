from flask import Flask, request, redirect, render_template, flash
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database initialization
conn = sqlite3.connect('urls.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS short_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_code TEXT NOT NULL UNIQUE
    )
''')
conn.commit()
conn.close()

# Function to generate a short code
def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']

        # Check if the URL is already shortened
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute('SELECT short_code FROM short_urls WHERE original_url = ?', (original_url,))
        existing_short_code = cursor.fetchone()
        conn.close()

        if existing_short_code:
            flash(f'This URL is already shortened: {request.host_url}{existing_short_code[0]}')
            return redirect('/')

        # Generate a unique short code
        short_code = generate_short_code()

        # Save the original URL and the short code to the database
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO short_urls (original_url, short_code) VALUES (?, ?)', (original_url, short_code))
        conn.commit()
        conn.close()

        flash(f'Your shortened URL: {request.host_url}{short_code}')
        return redirect('/')

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_original_url(short_code):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM short_urls WHERE short_code = ?', (short_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        flash('Shortened URL not found.')
        return redirect('/')

if __name__ == '__main__':
    app.run()
