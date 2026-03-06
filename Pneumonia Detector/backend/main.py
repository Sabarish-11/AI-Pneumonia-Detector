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
from PIL import Image


# =====================================================
# APP CONFIG
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'pneumonia_app.db')}"

SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


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
        image = Image.open(io.BytesIO(await file.read()))
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
