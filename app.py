from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import os

# Initialize Firebase Admin
cred = credentials.Certificate('')
firebase_admin.initialize_app(cred, {
    'storageBucket': '
})

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db = firestore.client()
bucket = storage.bucket()


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            session['user'] = user.uid  # Store user ID in session
            return redirect(url_for('home'))
        except:
            return 'Invalid credentials or user not found'
    return render_template('login.html')


# Home Route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Retrieve files from Firebase Storage
    blobs = bucket.list_blobs()
    files = [{'name': blob.name, 'url': blob.public_url} for blob in blobs]

    return render_template('index.html', files=files)


# Upload Route
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    if file:
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)
        return redirect(url_for('home'))
    return 'No file uploaded'


# Delete Route
@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if 'user' not in session:
        return redirect(url_for('login'))

    blob = bucket.blob(filename)
    blob.delete()
    return redirect(url_for('home'))


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
