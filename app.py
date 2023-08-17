import os, io

import cv2
from PIL import Image
import base64
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import face_recognition
import numpy as np
from database import db
from models import User
import dlib
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_database.db'
db.init_app(app)
migrate = Migrate(app, db)

face_recognition_model = dlib.face_recognition_model_v1("Model/dlib_face_recognition_resnet_model_v1.dat")
face_shape_predictor = dlib.shape_predictor("Model/shape_predictor_68_face_landmarks.dat")


# Load user face data during application startup
## Load user face data during application startup
def load_user_face_data():
    user_face_data = {}
    users = User.query.all()
    for user in users:
        face_images = [
            face_recognition.load_image_file(user.face_image1),
            face_recognition.load_image_file(user.face_image2),
            face_recognition.load_image_file(user.face_image3)
        ]
        face_encodings = [face_recognition.face_encodings(face_image)[0] for face_image in face_images]
        user_face_data[user.username] = face_encodings
    return user_face_data

# Perform face recognition for the captured image
def recognize_face(captured_image, user_face_data):
    captured_face_encoding = face_recognition.face_encodings(captured_image)[0]
    for username, face_encodings in user_face_data.items():
        for face_encoding in face_encodings:
            match_results = face_recognition.compare_faces([face_encoding], captured_face_encoding)
            if match_results[0]:
                return username
    return None


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            flash({'message': 'Logged in, Face Confirmation Needed', 'type': 'Success'})
            return redirect(url_for('face_confirmation'))
        else:
            flash({'message': 'Invalid username or password', 'type': 'danger'})
    return render_template('login.html')



@app.route('/face_confirmation', methods=['GET', 'POST'])
def face_confirmation():
    # Check if the user is logged in
    if 'username' in session:
        if request.method == 'POST':
            # Get the username from the session
            username = session['username']

            # Retrieve the user's information from the database
            user = User.query.filter_by(username=username).first()
            if user:
                # Get the paths to the registered face images
                face_image1_path = user.face_image1
                face_image2_path = user.face_image2
                face_image3_path = user.face_image3

                # Create a list of registered face image paths
                registered_face_image_paths = [face_image1_path, face_image2_path, face_image3_path]
                registered_face_encodings = []

                # Load the registered face images, resize them, and extract face encodings
                for image_path in registered_face_image_paths:
                    registered_face = dlib.load_rgb_image(image_path)
                    registered_face_resized = dlib.resize_image(registered_face, 150, 150)
                    face_landmarks = face_shape_predictor(registered_face_resized, dlib.rectangle(0, 0, 150, 150))
                    face_encoding = face_recognition_model.compute_face_descriptor(registered_face_resized, face_landmarks)
                    registered_face_encodings.append(face_encoding)

                # Get the captured image in Base64 format from the form
                captured_image_base64 = request.form['captured_image']

                if not captured_image_base64:
                    # Display a flash message if the captured image is empty
                    flash({'message': 'No image captured. Please try again.', 'type': 'warning'})
                    return render_template('face_confirmation.html')

                # Decode the Base64 image data and convert it to a PIL image
                captured_image = Image.open(io.BytesIO(base64.b64decode(captured_image_base64.split(',')[1])))

                # Resize the captured image to 150x150 and convert to dlib format
                captured_image_resized = dlib.resize_image(np.array(captured_image), 150, 150)
                captured_face_landmarks = face_shape_predictor(captured_image_resized, dlib.rectangle(0, 0, 150, 150))
                captured_face_encoding = face_recognition_model.compute_face_descriptor(captured_image_resized, captured_face_landmarks)

                # Compare the captured face encoding with the registered face encodings
                match_results = [np.linalg.norm(np.array(captured_face_encoding) - np.array(reg_encoding)) < 0.4 for reg_encoding in registered_face_encodings]
                if any(match_results):
                    # If a match is found, log the user in and redirect to the dashboard
                    flash({'message': 'Face confirmed! You are logged in.', 'type': 'success'})
                    return redirect(url_for('dashboard'))

                # If no match is found, display a warning message
                flash({'message': 'Face not recognized. Please try again.', 'type': 'warning'})
                return render_template('face_confirmation.html')
            else:
                # If the user is not found in the database, display an error message
                flash({'message': 'User not found.', 'type': 'danger'})
                return render_template('face_confirmation.html', message='', url=url_for('login'))
        # If the request method is not POST, display the face confirmation form
        return render_template('face_confirmation.html')
    else:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Store the user's face images
        face_image1_base64 = request.form['face_image1']
        face_image2_base64 = request.form['face_image2']
        face_image3_base64 = request.form['face_image3']

        # Decode the Base64-encoded images
        face_image1 = base64.b64decode(face_image1_base64.split(',')[1])
        face_image2 = base64.b64decode(face_image2_base64.split(',')[1])
        face_image3 = base64.b64decode(face_image3_base64.split(',')[1])

        # Save the face images to a folder (adjust the path as needed)
        face_image1_path = os.path.join('uploads', f'{username}_face1.jpg')
        face_image2_path = os.path.join('uploads', f'{username}_face2.jpg')
        face_image3_path = os.path.join('uploads', f'{username}_face3.jpg')

        with open(face_image1_path, 'wb') as f1, open(face_image2_path, 'wb') as f2, open(face_image3_path, 'wb') as f3:
            f1.write(face_image1)
            f2.write(face_image2)
            f3.write(face_image3)

        # Store the user's data in the database using SQLAlchemy
        user = User(username=username, password=password, face_image1=face_image1_path,
                    face_image2=face_image2_path, face_image3=face_image3_path)
        db.session.add(user)
        db.session.commit()

        flash({'message': 'Registration successful. Please log in.', 'type': 'success'})
        return redirect(url_for('login'))

    return render_template('register.html')  # Render the registration form

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/face_gesture')
def face_gesture():
    return render_template('face_gesture.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
