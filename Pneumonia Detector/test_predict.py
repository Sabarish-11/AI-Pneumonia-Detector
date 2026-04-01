import tensorflow as tf
from PIL import Image
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "model", "pneumonia_model.tflite")

interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Input details:")
print(input_details)
print("Output details:")
print(output_details)

def preprocess_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    arr = np.array(image, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

# Create a dummy image
test_img = Image.new("RGB", (300, 300))
processed = preprocess_image(test_img)

print("Processed shape:", processed.shape, "dtype:", processed.dtype)

try:
    interpreter.set_tensor(input_details[0]['index'], processed)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prob = float(output_data[0][0])
    print("Probability:", prob)
except Exception as e:
    print("Exception during TFLite inference:", str(e))
