import json
import os
import shutil
import yaml
import random
import math
from tqdm import tqdm


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

raw_json = os.path.join(project_root, "data", "raw", "annotation_data.json")
raw_images_dir = os.path.join(project_root, "data", "raw", "images")

output_dir = os.path.join(project_root, "data", "processed")

VAL_SPLIT = 0.2
SEED = 2026

# маппинг
ID_MAP = {
    2140001: 0, 2150001: 1, 2280011: 2, 2160001: 3,
    2220001: 4, 2280000: 5, 2280001: 6, 2270001: 7
}
NAMES_MAP = {
    0: "vibration_damper", 1: "festoon_insulators", 2: "polymer_insulators",
    3: "traverse", 4: "nest", 5: "bad_insulator", 6: "damaged_insulator",
    7: "safety_sign"
}

def setup_dirs():
	# удаляем старую версию - "обычную" YOLO c HBB
	# осталось от неправильной разметки
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir) 
    
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "labels", split), exist_ok=True)

def get_obb_coords(x, y, w, h, angle_deg, img_w, img_h):
    """
    Превращает bbox + rotation в 4 нормализованные точки 
    (x1 y1 x2 y2 x3 y3 x4 y4).
    """
    angle_rad = math.radians(angle_deg)
    cx, cy = x + w / 2, y + h / 2
    
    # смещения углов относительно центра (TL, TR, BR, BL)
    dx = [-w/2, w/2, w/2, -w/2]
    dy = [-h/2, -h/2, h/2, h/2]
    
    corners = []
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    for i in range(4):
        # поворот
        nx = dx[i] * cos_a - dy[i] * sin_a
        ny = dx[i] * sin_a + dy[i] * cos_a
        
        # абс. координаты угла
        abs_x = cx + nx
        abs_y = cy + ny
        
        # нормализация (0..1)
        # ограничиваем (clip) значениями 0..1 
        norm_x = max(0, min(1, abs_x / img_w))
        norm_y = max(0, min(1, abs_y / img_h))
        
        corners.append(f"{norm_x:.6f} {norm_y:.6f}")
        
    return " ".join(corners)

def main():
    random.seed(SEED)
    print("🚀 Начинаем конвертацию в YOLO OBB формат...")
    setup_dirs()
    
    with open(raw_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # группируем аннотации
    img_anns = {}
    for ann in data['annotations']:
        img_anns.setdefault(ann['image_id'], []).append(ann)
        
    images = data['images']
    random.shuffle(images)
    
    num_val = int(len(images) * VAL_SPLIT)
    datasets = {
        'val': images[:num_val],
        'train': images[num_val:]
    }
    
    print(f"📊 Train: {len(datasets['train'])}, Val: {len(datasets['val'])}")
    
    for split, split_imgs in datasets.items():
        print(f"📦 Processing {split}...")
        for img_info in tqdm(split_imgs):
            file_name = img_info['file_name']
            src_path = os.path.join(raw_images_dir, file_name)
            
            # фиксим пути
            src_path = src_path.replace('\\', '/')
            if not os.path.exists(src_path):
                continue
                
            new_filename = file_name.replace('/', '_').replace('\\', '_')
            
            # копируем фото
            shutil.copy(src_path, os.path.join(output_dir, "images", split, new_filename))
            
            # Label (OBB Format)
            label_path = os.path.join(output_dir, "labels", split, os.path.splitext(new_filename)[0] + ".txt")
            img_w, img_h = img_info['width'], img_info['height']
            
            with open(label_path, 'w') as f_txt:
                for ann in img_anns.get(img_info['id'], []):
                    cat_id = ann['category_id']
                    if cat_id not in ID_MAP: continue
                    
                    # если rotation нет - считаем его 0
                    angle = ann.get('rotation', 0)
                    bbox = ann['bbox'] # x, y, w, h
                    
                    coords_str = get_obb_coords(bbox[0], bbox[1], bbox[2], bbox[3], angle, img_w, img_h)
                    
                    f_txt.write(f"{ID_MAP[cat_id]} {coords_str}\n")

    # data.yaml (специфичный для OBB, но структура та же)
    yaml_content = {
        'path': output_dir,
        'train': 'images/train',
        'val': 'images/val',
        'names': NAMES_MAP
    }
    
    with open(os.path.join(output_dir, "data.yaml"), 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)
        
    print("\n✅ Конвертация завершена! Данные готовы для YOLO11-OBB.")

if __name__ == "__main__":
    main()