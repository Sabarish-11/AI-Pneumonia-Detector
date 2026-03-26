from datetime import datetime, timedelta
from typing import Optional
import os
import io

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, Session, create_engine, select

import tensorflow as tf
import numpy as np
from PIL import Image, UnidentifiedImageError


# =====================================================
# APP CONFIG
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'pneumonia_app.db')}"

SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MIN_IMAGE_DIMENSION = 128


# =====================================================
# APP INIT
# =====================================================
app = FastAPI(title="Pneumonia Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# DATABASE
# =====================================================
# SQLite needs check_same_thread=False when used across threads (e.g., FastAPI workers).
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# =====================================================
# SECURITY
# =====================================================
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# MODELS
# =====================================================
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    image_name: str
    label: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RegisterRequest(SQLModel):
    name: str
    email: str
    password: str


class LoginRequest(SQLModel):
    email: str
    password: str


# =====================================================
# STARTUP
# =====================================================
@app.on_event("startup")
def startup():
    create_db()
    print("✅ Database ready")


# =====================================================
# AUTH DEPENDENCY
# =====================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =====================================================
# ML MODEL
# =====================================================
MODEL_PATH = os.path.join(BASE_DIR, "model", "pneumonia_model.h5")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("❌ Model file not found")

model = tf.keras.models.load_model(MODEL_PATH)


def preprocess_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    arr = np.array(image) / 255.0
    return np.expand_dims(arr, axis=0)


def is_likely_chest_xray(image: Image.Image):
    rgb_image = image.convert("RGB")
    grayscale_image = image.convert("L")

    width, height = rgb_image.size
    aspect_ratio = width / height if height else 0
    if not 0.3 <= aspect_ratio <= 3.5:
        return False, "Image proportions are too unusual for chest X-ray analysis."

    rgb_array = np.asarray(rgb_image, dtype=np.float32)
    grayscale_array = np.asarray(grayscale_image, dtype=np.float32)

    # Chest X-rays are typically grayscale; color photographs show larger channel gaps.
    mean_channel_gap = float(
        np.mean(np.abs(rgb_array[:, :, 0] - rgb_array[:, :, 1]))
        + np.mean(np.abs(rgb_array[:, :, 1] - rgb_array[:, :, 2]))
        + np.mean(np.abs(rgb_array[:, :, 0] - rgb_array[:, :, 2]))
    ) / 3.0

    contrast = float(grayscale_array.std())

    if mean_channel_gap > 12:
        return False, "This appears to be a color photo, not a chest X-ray."

    if contrast < 12:
        return False, "This image has too little contrast for reliable chest X-ray analysis."

    return True, None


def validate_uploaded_image(file: UploadFile, file_bytes: bytes):
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file data received.",
        )

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are supported.",
        )

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is too large. Please upload a file smaller than 10 MB.",
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid image.",
        )

    if min(image.size) < MIN_IMAGE_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image resolution is too low. Please upload a clearer chest X-ray.",
        )

    is_valid_xray, reason = is_likely_chest_xray(image)
    if not is_valid_xray:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    return image


# =====================================================
# ROUTES
# =====================================================
@app.get("/")
def root():
    return {"message": "API running"}


# ---------- REGISTER ----------
@app.post("/register")
def register(
    body: RegisterRequest,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    return {"message": "Registered successfully"}


# ---------- LOGIN ----------
@app.post("/login")
def login(
    body: LoginRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token(user.email)
    return {"access_token": token, "token_type": "bearer"}


# ---------- PREDICT ----------
@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        file_bytes = await file.read()
        image = validate_uploaded_image(file, file_bytes)
        processed = preprocess_image(image)

        prob = float(model.predict(processed)[0][0])

        if prob > 0.5:
            label = "PNEUMONIA"
            confidence = prob
        else:
            label = "NORMAL"
            confidence = 1 - prob

        record = Prediction(
            user_id=user.id,
            image_name=file.filename,
            label=label,
            confidence=confidence,
        )
        session.add(record)
        session.commit()

        return {
            "prediction": label,
            "confidence": round(confidence, 3),
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed. Please try again with a valid chest X-ray image.",
        )


# ---------- HISTORY ----------
@app.get("/history")
def history(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    data = session.exec(
        select(Prediction)
        .where(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
    ).all()
    return data
