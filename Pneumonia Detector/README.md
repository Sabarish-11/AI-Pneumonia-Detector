# Pneumonia Detector

This project detects pneumonia from chest X-ray images. It consists of a React frontend and a FastAPI backend with a TensorFlow ML model.

## Recent Fixes & Improvements

### Robust Memory & State Management
- **Explicit Garbage Collection:** The backend now actively clears memory allocations (tensors, image bytes) after each prediction. This stabilizes the app, especially in limit-constrained environments like Render (512MB RAM limit), preventing the API from crashing after consecutive or invalid image uploads.
- **Improved File Handling:** Resetting the file upload stream correctly and ensuring all `PIL.Image` objects are closed on both success and failure states so there are no dangling descriptors leading to OOM issues.
- **Frontend State Sync:** Refactored the `UploadBox` logic so React state inherently controls the prediction input rather than buggy DOM references.

### Validation Layer Enhancement
- **Strict Image Validation:** The backend now properly intercepts and checks validation layers BEFORE prediction runs.
- **Clear Error Messaging:** The system will smoothly reject and explicitly return `"Invalid Image (Please upload a chest X-ray)"` in `JSON` without failing or crashing the FastAPI event loop for following requests.

## Tech Stack
- Frontend: React + Vite (Ready for Vercel)
- Backend: FastAPI, SQLModel, TensorFlow (Ready for Render)
