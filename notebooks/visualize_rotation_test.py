import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import math
import random

# пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
JSON_PATH = os.path.join(ROOT_DIR, "data", "raw", "annotation_data.json")
IMG_DIR = os.path.join(ROOT_DIR, "data", "raw", "images")

def get_corners_degrees(x, y, w, h, angle_deg):
    """
    Вычисляет углы, считая, что angle_deg в ГРАДУСАХ.
    """
    # переводим в радианы только для математики
    angle_rad = math.radians(angle_deg)
    
    cx = x + w / 2
    cy = y + h / 2
    
    # векторы от центра до углов (неповернутые)
    # tL, TR, BR, BL
    dx = [-w/2, w/2, w/2, -w/2]
    dy = [-h/2, -h/2, h/2, h/2]
    
    corners = []
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    for i in range(4):
        # поворот
        nx = dx[i] * cos_a - dy[i] * sin_a
        ny = dx[i] * sin_a + dy[i] * cos_a
        corners.append((cx + nx, cy + ny))
        
    return corners

def main():
    with open(JSON_PATH, 'r', encoding="utf-8") as f:
        data = json.load(f)
    
    # ищем кандидатов с явным наклоном (> 15 градусов)
    candidates = []
    for ann in data['annotations']:
        rot = ann.get('rotation', 0)
        # берем только гирлянды и только с заметным углом
        if abs(rot) > 15 and ann['category_id'] in [2150001, 2280011]:
            candidates.append(ann)
            
    print(f"Найдено кандидатов с наклоном > 15 град: {len(candidates)}")
    
    if not candidates:
        print("Нет наклонных гирлянд, пробуем любые с rotation != 0")
        candidates = [a for a in data['annotations'] if abs(a.get('rotation', 0)) > 1]

    # берем 4 случайных примера
    samples = random.sample(candidates, min(4, len(candidates)))
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    axes = axes.flatten()
    
    for i, ann in enumerate(samples):
        # ищем картинку
        img_info = next(img for img in data['images'] if img['id'] == ann['image_id'])
        img_path = os.path.join(IMG_DIR, img_info['file_name'])
        
        ax = axes[i]
        
        if os.path.exists(img_path):
            im = Image.open(img_path)
            ax.imshow(im)
            
            bx, by, bw, bh = ann['bbox']
            angle = ann.get('rotation', 0)
            
            # синий (HBB) - Оригинал COCO
            rect = patches.Rectangle((bx, by), bw, bh, linewidth=1, edgecolor='blue', facecolor='none', linestyle='--')
            ax.add_patch(rect)
            
            # красный (OBB) - Гипотеза Градусов
            corners = get_corners_degrees(bx, by, bw, bh, angle)
            poly = patches.Polygon(corners, linewidth=3, edgecolor='red', facecolor='none')
            ax.add_patch(poly)
            
            ax.set_title(f"Rot: {angle:.1f}°")
        else:
            ax.text(0.5, 0.5, "Image not found", ha='center')
            
        ax.axis('off')
        
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()