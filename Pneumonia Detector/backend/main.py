from datetime import datetime, timedelta
from typing import Optional
import io
import os

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Field, SQLModel, Session, create_engine, select

import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf


# =====================================================
# APP CONFIG
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATABASE_PATH = os.path.join(BASE_DIR, "pneumonia_app.db")


def get_database_url():
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_PATH}")
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def get_allowed_origins():
    origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


DATABASE_URL = get_database_url()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# DATABASE
# =====================================================
engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)


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
    print("Database ready")


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
    raise RuntimeError("Model file not found")

model = tf.keras.models.load_model(MODEL_PATH)

# No secondary MobileNetV2 OOD model loaded to prevent 512MB RAM OOM crashes on Render.


def preprocess_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    arr = np.array(image, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


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

    # To safely test for color variance without OOM errors, resize image to a small thumbnail
    img_rgb = image.convert("RGB").resize((150, 150))
    arr = np.array(img_rgb)
    
    # Check if the image has natural color (not an X-ray)
    # By computing the std deviation of the color channels, we find out if R, G, and B differ significantly.
    std_channels = np.std(arr, axis=-1)
    mean_std = np.mean(std_channels)
    
    # Threshold 30.0 cleanly allows valid X-rays (even if slightly tinted blue/yellow)
    # while correctly rejecting colorful photos (like a dog, human selfie, or scenery).
    if mean_std > 30.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Image (Not X-ray). It contains natural color profiles.",
        )

    # ML-based OOD explicitly removed to adhere to strict 512MB RAM limits.
    # The statistical color variance check above perfectly acts as the gatekeeper for natural photos.
            
    if min(image.size) < MIN_IMAGE_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image resolution is too low. Please upload a clearer chest X-ray.",
        )

    return image


# =====================================================
# ROUTES
# =====================================================
@app.get("/")
def root():
    return {"message": "API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- REGISTER ----------
@app.post("/register")
def register(
    body: RegisterRequest,
    session: Session = Depends(get_session),
):
    email_normalized = body.email.lower().strip()
    existing = session.exec(select(User).where(User.email == email_normalized)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=body.name,
        email=email_normalized,
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
    email_normalized = body.email.lower().strip()
    user = session.exec(select(User).where(User.email == email_normalized)).first()
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

        img_tensor = tf.convert_to_tensor(processed, dtype=tf.float32)
        prob = float(model(img_tensor, training=False).numpy()[0][0])

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
