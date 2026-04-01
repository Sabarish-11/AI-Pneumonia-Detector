import numpy as np
from PIL import Image, ImageDraw

def generate_test_images():
    imgs = {}
    
    # 1. Grayscale X-ray mock
    img_gray = Image.new("L", (150, 150))
    d = ImageDraw.Draw(img_gray)
    d.rectangle([0, 0, 150, 150], fill=150)
    d.rectangle([20, 20, 60, 120], fill=50) # left lung
    d.rectangle([90, 20, 130, 120], fill=50) # right lung
    d.rectangle([65, 0, 85, 150], fill=220) # spine
    imgs['fake_xray'] = img_gray
    
    # 2. Portrait Mock
    img_portrait = Image.new("L", (150, 150), 200)
    d = ImageDraw.Draw(img_portrait)
    d.rectangle([40, 50, 110, 150], fill=30)
    imgs['portrait_photo'] = img_portrait
    
    return imgs

def test_structural_heuristics(imgs):
    for name, image in imgs.items():
        gray = image.convert("L").resize((150, 150))
        gray_arr = np.array(gray, dtype=np.float32)
        
        left = np.mean(gray_arr[:, 0:40])
        center = np.mean(gray_arr[:, 55:95])
        right = np.mean(gray_arr[:, 110:150])
        
        fails_spatial = center < left * 0.85 and center < right * 0.85
        
        diff_x = np.abs(np.diff(gray_arr, axis=1)) # shape: (150, 149)
        diff_y = np.abs(np.diff(gray_arr, axis=0)) # shape: (149, 150)
        
        edges = (diff_x[:-1, :] > 20) | (diff_y[:, :-1] > 20) # shapes: (149, 149)
        edge_ratio = np.mean(edges)
        
        print(f"--- {name} ---")
        print(f"Left: {left:.1f}, Center: {center:.1f}, Right: {right:.1f}")
        print(f"Fails Spatial (Center Darker): {fails_spatial}")
        print(f"Edge Ratio (>20 intensity diff): {edge_ratio:.4f}")
        print()

test_structural_heuristics(generate_test_images())
