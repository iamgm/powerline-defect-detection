import os
import random
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(os.path.dirname(BASE_DIR), "data", "processed")

def visualize_obb():
    # читаем имена классов
    yaml_path = os.path.join(PROCESSED_DIR, "data.yaml")
    if not os.path.exists(yaml_path):
        print("❌ data.yaml не найден!")
        return
        
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    class_names = config['names']

    # ищем случайную пару (картинка + текст)
    img_dir = os.path.join(PROCESSED_DIR, "images", "train")
    lbl_dir = os.path.join(PROCESSED_DIR, "labels", "train")
    
    # фильтруем файлы, чтобы найти те, где много точек (гирлянды)
    all_files = os.listdir(img_dir)
    random.shuffle(all_files)
    
    filename = None
    for f in all_files:
        lbl_path = os.path.join(lbl_dir, os.path.splitext(f)[0] + ".txt")
        if os.path.exists(lbl_path):
            filename = f
            break
            
    if not filename:
        print("❌ Файлы не найдены")
        return

    img_path = os.path.join(img_dir, filename)
    lbl_path = os.path.join(lbl_dir, os.path.splitext(filename)[0] + ".txt")

    # рисуем
    im = Image.open(img_path)
    w, h = im.size
    
    fig, ax = plt.subplots(1, figsize=(12, 12))
    ax.imshow(im)
    
    with open(lbl_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        parts = line.strip().split()
        cls_id = int(parts[0])
        coords = list(map(float, parts[1:])) # 8 чисел
        
        # денормализация: (x * w, y * h)
        # формат: x1 y1 x2 y2 x3 y3 x4 y4
        poly_points = []
        for i in range(0, 8, 2):
            px = coords[i] * w
            py = coords[i+1] * h
            poly_points.append((px, py))
            
        # цвет: Красный для дефектов, Зеленый для нормы
        name = class_names[cls_id]
        color = '#FF0000' if 'bad' in name or 'damaged' in name else '#00FF00'
        
        # рисуем полигон
        poly = patches.Polygon(poly_points, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(poly)
        
        # подпись (берем первую точку)
        ax.text(poly_points[0][0], poly_points[0][1], name, color='white', backgroundcolor=color, fontsize=9)

    plt.title(f"YOLO OBB Check: {filename}")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    visualize_obb()