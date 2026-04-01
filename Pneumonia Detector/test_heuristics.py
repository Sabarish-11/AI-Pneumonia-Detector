import numpy as np
from PIL import Image, ImageDraw
import json
import os

def generate_test_images():
    imgs = {}
    
    # 1. Grayscale X-ray mock
    img_gray = Image.new("RGB", (150, 150))
    d = ImageDraw.Draw(img_gray)
    for i in range(150): d.line([(0, i), (150, i)], fill=(i, i, i))
    imgs['fake_xray'] = img_gray
    
    # 2. Blue Tinted X-ray mock
    img_tinted = Image.new("RGB", (150, 150))
    d = ImageDraw.Draw(img_tinted)
    for i in range(150): d.line([(0, i), (150, i)], fill=(i, i, min(255, int(i*1.1 + 10))))
    imgs['tinted_xray'] = img_tinted
    
    # 3. Screenshot mock (mostly white, some green, some blue)
    img_screen = Image.new("RGB", (150, 150), (255, 255, 255))
    d = ImageDraw.Draw(img_screen)
    d.rectangle([10, 10, 30, 30], fill=(0, 255, 0)) # green
    d.rectangle([40, 40, 60, 60], fill=(0, 0, 255)) # blue
    imgs['cisco_screenshot'] = img_screen
    
    return imgs

def test_heuristics(imgs):
    results = {}
    for name, image in imgs.items():
        arr = np.array(image, dtype=np.float32)
        std_channels = np.std(arr, axis=-1)
        mean_std = float(np.mean(std_channels))
        max_std = float(np.max(std_channels))
        color_ratio = float(np.mean(std_channels > 15.0))
        
        hsv_arr = np.array(image.convert("HSV"), dtype=np.float32)
        hue = hsv_arr[..., 0]
        sat = hsv_arr[..., 1]
        
        hue_std = float(np.std(hue[sat > 10]) if np.any(sat > 10) else 0.0)
        mean_sat = float(np.mean(sat))
        max_sat = float(np.max(sat))
        
        gray = np.array(image.convert("L"), dtype=np.float32)
        edge_energy = float(np.mean(np.abs(np.diff(gray, axis=1))) + np.mean(np.abs(np.diff(gray, axis=0))))
        
        results[name] = {
            "mean_std": round(mean_std, 2),
            "max_std": round(max_std, 2),
            "color_ratio": round(color_ratio, 4),
            "hue_std": round(hue_std, 2),
            "mean_sat": round(mean_sat, 2),
            "max_sat": round(max_sat, 2),
            "edge_energy": round(edge_energy, 2)
        }
    
    with open("heuristics_out.json", "w") as f:
        json.dump(results, f, indent=4)

test_heuristics(generate_test_images())
