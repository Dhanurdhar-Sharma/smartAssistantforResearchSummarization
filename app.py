from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
from summerize import summarize_pdf  # Your summarizer logic
from quationing import answer_question_from_pdf  # Your QA logic

# === Configurations ===
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Helper Functions ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')


# === File Upload ===
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Avoid filename conflicts
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                filename = f"{base}_{counter}{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1

            file.save(save_path)
            return jsonify({ 'filename': filename })

        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        print("❌ Upload Error:", e)
        return jsonify({'error': 'Server error during upload'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/list-files')
def list_files():
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    else:
        files = []
    return jsonify(files)


@app.route('/delete-file/<filename>', methods=['DELETE'])
def delete_file(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': 'File deleted successfully'})
    return jsonify({'error': 'File not found'}), 404


# === Summarization ===
@app.route('/summarize/<filename>')
def summarize(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        summary = summarize_pdf(filepath)
        return jsonify({ 'summary': summary or "⚠️ No summary generated." })
    except Exception as e:
        print("❌ Summarization error:", e)
        return jsonify({ 'summary': '⚠️ Failed to summarize document.' }), 500


# === Question Answering ===
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '')
    filename = data.get('filename', '')

    if not question.strip():
        return jsonify({'answer': '❌ No question provided.'}), 400

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if not os.path.exists(pdf_path):
        return jsonify({'answer': '❌ PDF file not found.'}), 404

    try:
        result = answer_question_from_pdf(pdf_path, question)
        if "error" in result:
            return jsonify({'answer': f"⚠️ {result['error']}"} )
        return jsonify({
            'answer': result['answer'],
            'source': result['source']
        })
    except Exception as e:
        print("❌ QA processing error:", e)
        return jsonify({'answer': '⚠️ Internal error while answering the question.'}), 500


# === Signup ===
@app.route('/signup_req', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['pass']
    profile_photo = request.form['pp']

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (email, password, profile_photo) VALUES (?, ?, ?)',
            (email, password, profile_photo)
        )
        conn.commit()
        return jsonify({ "status": "success", "message": "User registered successfully" })
    except sqlite3.IntegrityError:
        return jsonify({ "status": "error", "message": "User with this email already exists" })
    except Exception as e:
        print("❌ Server error during signup:", e)
        return jsonify({ "status": "error", "message": "Server error. Please try again." })
    finally:
        conn.close()


# === Login ===
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pass']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and user['password'] == password:
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "email": user['email'],
            "profile_photo": user['profile_photo']
        })
    else:
        return jsonify({ "status": "error", "message": "Invalid email or password" })


# === Run the App ===
if __name__ == '__main__':
    app.run(debug=True)
