import os
import sqlite3
from flask import Flask, request, render_template_string, redirect
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# бдшка
def init_db():
    conn = sqlite3.connect('insta_clone.db')
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        image_path TEXT,
        description TEXT,
        location TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS hashtags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS post_hashtags (
        post_id INTEGER,
        hashtag_id INTEGER,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (hashtag_id) REFERENCES hashtags(id)
    );

    CREATE TABLE IF NOT EXISTS mentions (
        post_id INTEGER,
        mentioned_user_id INTEGER,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (mentioned_user_id) REFERENCES users(id)
    );
    """)

    # тест юзеры
    cur.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ("testuser",))
    cur.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ("andriy_123",))
    cur.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ("marta.k",))

    conn.commit()
    conn.close()

# главная страница
@app.route('/', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        author_id = 1  # временно фиксированый, поменять по тому айди который у типочков
        description = request.form['description']
        location = request.form['location']
        hashtags = request.form['hashtags'].split()
        mentions = request.form['mentions'].split()

        image = request.files['image']
        filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        conn = sqlite3.connect('insta_clone.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO posts (author_id, image_path, description, location, created_at) VALUES (?, ?, ?, ?, ?)",
                    (author_id, image_path, description, location, datetime.now()))
        post_id = cur.lastrowid

        for tag in hashtags:
            tag = tag.strip()
            if tag:
                cur.execute("INSERT OR IGNORE INTO hashtags (tag) VALUES (?)", (tag,))
                cur.execute("SELECT id FROM hashtags WHERE tag = ?", (tag,))
                tag_id = cur.fetchone()[0]
                cur.execute("INSERT INTO post_hashtags (post_id, hashtag_id) VALUES (?, ?)", (post_id, tag_id))

        for username in mentions:
            username = username.strip()
            if username:
                cur.execute("SELECT id FROM users WHERE username = ?", (username,))
                user = cur.fetchone()
                if user:
                    cur.execute("INSERT INTO mentions (post_id, mentioned_user_id) VALUES (?, ?)", (post_id, user[0]))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template_string(FORM_HTML)

# хтмл встроеная форма
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Новий пост</title>
</head>
<body>
    <h1>Створити пост</h1>
    <form method="POST" enctype="multipart/form-data">
        <label>Фото:</label><br>
        <input type="file" name="image" required><br><br>

        <label>Опис:</label><br>
        <textarea name="description" required></textarea><br><br>

        <label>Геолокація:</label><br>
        <input type="text" name="location"><br><br>

        <label>Хештеги (через пробіл):</label><br>
        <input type="text" name="hashtags" placeholder="природа літо море"><br><br>

        <label>Згадки користувачів (через пробіл):</label><br>
        <input type="text" name="mentions" placeholder="andriy_123 marta.k"><br><br>

        <button type="submit">Опублікувати</button>
    </form>
</body>
</html>
"""

# старт
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
