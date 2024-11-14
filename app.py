from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from flask_cors import CORS

# Initialize Firebase Admin SDK with your service account credentials
cred = credentials.Certificate(
    'C:\\Users\\gills\\Desktop\\Safeupload\\safelysave-ce984-firebase-adminsdk-sggxw-ce73db26cf.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'safelysave-ce984.appspot.com'
})

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Make sure to change this for production!
db = firestore.client()
bucket = storage.bucket()

# Enable CORS to allow requests from different origins (e.g., React frontend)
CORS(app)


# Login Route - This route should accept an ID token and verify it.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the ID token sent by the client (React app)
        id_token = request.form['idToken']

        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            session['user'] = decoded_token['uid']  # Store UID in session
            return redirect(url_for('home'))  # Redirect to home page
        except Exception as e:
            return f'Invalid credentials: {str(e)}'  # Handle errors gracefully

    return render_template('login.html')


# Home Route - Display files from Firebase Storage
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not authenticated

    # Retrieve files from Firebase Storage
    blobs = bucket.list_blobs()  # Get all blobs (files) in the storage bucket
    files = [{'name': blob.name, 'url': blob.public_url} for blob in blobs]  # Get file names and URLs

    return render_template('index.html', files=files)  # Pass files to the template for rendering


# Upload Route - Allows users to upload files to Firebase Storage
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    file = request.files.get('file')  # Get the uploaded file from the request

    if file:
        try:
            # Create a blob (file) in Firebase Storage with the same name as the uploaded file
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)  # Upload the file to Firebase Storage

            return redirect(url_for('home'))  # Redirect to home page after upload
        except Exception as e:
            return f'Error uploading file: {str(e)}'  # Catch and return any errors during upload
    return 'No file uploaded'  # If no file was uploaded


# Delete Route - Deletes files from Firebase Storage
@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    try:
        # Get the blob (file) from Firebase Storage
        blob = bucket.blob(filename)
        blob.delete()  # Delete the file from Firebase Storage

        return redirect(url_for('home'))  # Redirect to home page after deleting file
    except Exception as e:
        return f'Error deleting file: {str(e)}'  # Catch and return any errors during delete


# Logout Route - Logs out the user by clearing the session
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('login'))  # Redirect to login page after logging out


if __name__ == '__main__':
    app.run(debug=True)
