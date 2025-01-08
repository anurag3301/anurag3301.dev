from flask import Flask, jsonify, send_from_directory, abort, redirect, url_for, send_file, render_template
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
