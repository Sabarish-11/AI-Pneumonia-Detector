import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "backend", "model", "pneumonia_model.h5")
tflite_path = os.path.join(BASE_DIR, "backend", "model", "pneumonia_model.tflite")

print(f"Loading Keras model from {model_path}...")
model = tf.keras.models.load_model(model_path)

print("Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Standard conversion (no quantization) shrinks operational RAM drastically
# while retaining exact float32 accuracy.
tflite_model = converter.convert()

print(f"Saving TFLite model to {tflite_path}...")
with open(tflite_path, "wb") as f:
    f.write(tflite_model)

print("Conversion complete!")
