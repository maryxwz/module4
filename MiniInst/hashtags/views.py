from django.shortcuts import render
import sqlite3
from .models import Hashtag

def create_table():
    conn = sqlite3.connect('hashtags.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS hashtags(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hashtag_name TEXT NOT NULL)''')

    all_hashtags = Hashtag.objects.all()

    for tag in all_hashtags:
        cur.execute('INSERT INTO hashtags (hashtag_name) VALUES (?)', (tag.hashtag_text,))

    conn.commit()
    conn.close()