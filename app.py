from flask import Flask, jsonify, send_from_directory, abort, redirect, url_for, send_file, render_template, abort, request
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import hashlib
import sqlite3
import string
import random

load_dotenv()
UPLOAD_KEY = os.getenv("UPLOAD_KEY")

UPLOAD_DIR = f"{os.getenv('HOME')}/uploads"
DB_PATH = "files.db"
SERVER_ADDR = "https://anurag3301.com"

app = Flask(__name__)
CORS(app)
os.makedirs(UPLOAD_DIR, exist_ok=True)
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name TEXT,
                hashed_name TEXT UNIQUE
            )
        ''')
        conn.commit()

init_db()


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def index(path):
    file_path = os.path.join('home/public', path)
    if os.path.isfile(file_path):
        return send_from_directory('home/public', path)
    elif os.path.isdir(file_path):
        return send_from_directory(file_path, 'index.html')
    else:
        return abort(404)

@app.route('/classgap')
def contact_page():
    return render_template('classgap.html')

@app.route('/resume')
def get_resume():
    # Path to the PDF file
    pdf_path = os.path.join(app.root_path, 'static', 'Resume.pdf')

    try:
        return send_file(pdf_path, mimetype='application/pdf')
    except FileNotFoundError:
        abort(404, description="Resume not found")


@app.route('/blog/', defaults={'path': 'index.html'})
@app.route('/blog/<path:path>')
def blog(path):
    file_path = os.path.join('blog/public', path)
    if os.path.isfile(file_path):
        return send_from_directory('blog/public', path)
    elif os.path.isdir(file_path):
        return send_from_directory(file_path, 'index.html')
    else:
        return abort(404)


@app.route('/game')
@cross_origin()
def game_index():
    return send_from_directory('game', 'spacebuddy.html')

@app.route('/game/<path:path>')
@cross_origin()
def serve_game_static(path):
    return send_from_directory('game', path)


def generate_short_hash(existing_hashes):
    chars = string.ascii_letters + string.digits  # base62
    while True:
        short = ''.join(random.choices(chars, k=5))
        if short not in existing_hashes:
            return short

def hash_filename(filename):
    ext = os.path.splitext(filename)[1]
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT hashed_name FROM files")
        used = {row[0].rsplit('.', 1)[0] for row in c.fetchall()}
    return generate_short_hash(used) + ext


@app.route("/upload", methods=["POST"])
def upload_file():
    provided_key = request.headers.get("X-Upload-Key")
    if not provided_key or provided_key != UPLOAD_KEY:
        return "Unauthorized", 401

    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    original_name = secure_filename(file.filename)
    hashed_name = hash_filename(original_name)
    save_path = os.path.join(UPLOAD_DIR, hashed_name)
    file.save(save_path)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO files (original_name, hashed_name) VALUES (?, ?)",
                     (original_name, hashed_name))
        conn.commit()

    return f"{SERVER_ADDR}/files/{hashed_name}\n", 200

@app.route("/files/<path:hashed_name>", methods=["GET"])
def get_file(hashed_name):
    file_path = os.path.join(UPLOAD_DIR, hashed_name)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(UPLOAD_DIR, hashed_name)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
