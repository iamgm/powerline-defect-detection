import os
import random
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(os.path.dirname(BASE_DIR), "data", "processed")

def visualize_sample():
    # получаем имена классов
    with open(os.path.join(PROCESSED_DIR, "data.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    class_names = config['names']

    # берем случайный файл из train
    img_dir = os.path.join(PROCESSED_DIR, "images", "train")
    lbl_dir = os.path.join(PROCESSED_DIR, "labels", "train")
    
    filename = random.choice(os.listdir(img_dir))
    img_path = os.path.join(img_dir, filename)
    lbl_path = os.path.join(lbl_dir, os.path.splitext(filename)[0] + ".txt")

    # рисуем
    im = Image.open(img_path)
    w, h = im.size
    
    fig, ax = plt.subplots(1, figsize=(12, 8))
    ax.imshow(im)
    
    if os.path.exists(lbl_path):
        with open(lbl_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.strip().split()
            cls_id = int(parts[0])
            cx, cy, bw, bh = map(float, parts[1:])
            
            # денормализация (YOLO -> Pixel)
            x1 = (cx - bw/2) * w
            y1 = (cy - bh/2) * h
            width = bw * w
            height = bh * h
            
            # цвет рамки (красный для дефектов, зеленый для остальных)
            color = 'red' if class_names[cls_id] in ['bad_insulator', 'damaged_insulator'] else '#00FF00'
            
            rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            ax.text(x1, y1, class_names[cls_id], color='white', backgroundcolor=color, fontsize=8)

    plt.title(f"Sample: {filename}")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    visualize_sample()