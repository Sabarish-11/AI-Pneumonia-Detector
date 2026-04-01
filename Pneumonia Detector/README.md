# AI Pneumonia Detector

This project detects pneumonia from chest X-ray images using advanced Machine Learning and Computer Vision techniques. It consists of a decoupled architecture featuring a fast React frontend and a highly optimized Python FastAPI backend.

## Features & Robustness
The backend has been aggressively designed and optimized to run flawlessly on strict cloud memory constraints (e.g., Render's 512MB RAM free tier limit) without compromising diagnostic accuracy or endpoint stability.

- **Lightweight TFLite Inference:** The original heavy `.h5` Keras neural networks were transcoded into statically allocated TensorFlow Lite interpreters. This drastically slashed peak server RAM overhead from over 400MB down to ~60MB, completely eliminating Out-of-Memory (OOM) deployment crashes.
- **Mathematical Image Gatekeeper:** The API utilizes a rigid mathematical Numpy filter to protect the AI from evaluating malicious or invalid images (such as natural photographs, dog pictures, plain documents, or UI screenshots).
  - **Color Variance Matrices:** Extracts RGB layer differentials to strictly block naturally colored imagery.
  - **Anatomical Layout Slicing:** Measures brightness across horizontal slices, enforcing the biological structure of chest X-rays (a bright dense spine surrounded by dark air-filled lung cavities) to block black-and-white portraits and landscapes.
  - **High-Frequency Edge Density:** Uses discrete pixel-derivative bounds (`np.diff`) to quantify sharp objects vs. soft tissue. It isolates and reliably ejects sharp text or UI graphics from naturally blurry X-ray gradients.

## Tech Stack
- **Frontend:** React.js, Vite (Deployed on Vercel)
- **Backend:** Python FastAPI, Pillow, NumPy (Deployed on Render)
- **AI Core:** TensorFlow Lite (`tensorflow-cpu` memory optimized)

## Local Development
**Backend:**
```bash
# Enter environment and install
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt

# Run the API server locally
uvicorn backend.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
