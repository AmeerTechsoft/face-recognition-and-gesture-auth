# Face Recognition and Gesture Detection Web Application

![Landing Page](landingpage.jpg)

This is a web application that implements face recognition for user authentication and gesture detection using Flask, dlib, and Mediapipe.

## Features

- User registration and login
- Capture an image and confirm identity using face recognition
- Detect facial gestures using Mediapipe facial landmarks
- Redirect to the user dashboard upon successful login
- Display flash messages for authentication and gesture detection feedback

## Prerequisites

- Python 3.11
- Flask
- OpenCV
- dlib (with shape_predictor and face_recognition_model)
- SQLAlchemy (for database interaction)
- Pillow (for image processing)
- Mediapipe (for facial gesture detection)
- Other required libraries (install them using `pip install -r requirements.txt`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/AmeerTechsoft/face-recognition-and-gesture-auth.git
    cd face-recognition-gesture-app
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Download the `shape_predictor_68_face_landmarks.dat` and `dlib_face_recognition_resnet_model_v1.dat` files from the dlib website (http://dlib.net/files/) and place them in the project directory.

4. Run the application:

    ```bash
    python app.py
    ```

## Usage

- Access the web application at `http://localhost:5000`
- Register a new user account or login with existing credentials
- Capture an image and confirm identity using the face recognition feature
- Observe facial gestures using Mediapipe facial landmarks
- Upon successful face recognition, you will be redirected to the user dashboard

## Contributing

Feel free to contribute to this project. If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

