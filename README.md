AI Pneumonia Detector

AI Pneumonia Detector is a full-stack web application that uses Deep Learning to detect pneumonia from chest X-ray images.
The system allows users to upload an X-ray image and receive an AI-based prediction indicating whether the lungs appear Normal or Pneumonia.

This project demonstrates the integration of Deep Learning, Backend APIs, and a Modern Frontend to build an intelligent healthcare assistant.

Features

User Registration and Login

Upload Chest X-ray Image

AI-based Pneumonia Detection

Confidence Score for Predictions

Prediction History for Logged-in Users

Secure Backend using JWT Authentication

Clean and responsive React UI

Tech Stack
Frontend

React

Axios

CSS

Backend

FastAPI

JWT Authentication

REST API

Machine Learning

TensorFlow

MobileNetV2

Image preprocessing using NumPy and PIL

Database

SQLite

Project Architecture
User (React Frontend)
        │
        ▼
FastAPI Backend API
        │
        ▼
Deep Learning Model (MobileNetV2)
        │
        ▼
Prediction Result
        │
        ▼
Stored in SQLite Database
Model Download

The trained model file is not included in this repository because it exceeds GitHub's file size limit.

Download the model from the link below and place it in the correct directory.

Model Download Link:

https://drive.google.com/drive/folders/1x4PG9Uy_UVAo9nA4UPRmh75JnZS7b9BK?usp=drive_link

After downloading, place the file in:

backend/model/pneumonia_model.h5
Project Setup
1 Clone the Repository
git clone https://github.com/yourusername/AI-Pneumonia-Detector.git
cd AI-Pneumonia-Detector
Backend Setup

Navigate to backend folder:

cd backend

Create virtual environment:

python -m venv venv

Activate environment:

Windows

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the backend server:

uvicorn main:app --reload

Backend will run on:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs
Frontend Setup

Navigate to frontend folder:

cd frontend

Install dependencies:

npm install

Run React app:

npm run dev

Frontend will run on:

http://localhost:5173
How the System Works

User registers and logs into the system.

User uploads a chest X-ray image.

The image is sent to the FastAPI backend.

Backend preprocesses the image.

The trained MobileNetV2 model analyzes the image.

The model predicts:

Normal

Pneumonia

Prediction and confidence score are returned to the frontend.

The result is displayed to the user and stored in the database.

Future Improvements

Detect multiple lung diseases

Cloud deployment

Mobile application

Integration with hospital systems

Improved dataset and training

Disclaimer

This system is designed for educational and research purposes only.
It should not be used as a replacement for professional medical diagnosis.

Author

Sabarish

AI Pneumonia Detection System – Deep Learning Project
