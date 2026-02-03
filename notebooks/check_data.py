import json
import os
from collections import Counter

# --- МАГИЯ ПУТЕЙ ---
# получаем абсолютный путь к папке, где лежит этот скрипт (notebooks)
current_dir = os.path.dirname(os.path.abspath(__file__))

# получаем корень проекта (родитель папки notebooks)
project_root = os.path.dirname(current_dir)

# строим пути к данным
json_path = os.path.join(project_root, "data", "raw", "annotation_data.json")
# внимание: предполагаем, что папка images лежит рядом с json
images_base_dir = os.path.join(project_root, "data", "raw", "images") 
# -------------------

def inspect_coco():
    print(f"📍 Ищем JSON здесь: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"❌ Файл не найден!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ JSON загружен. Всего изображений в индексе: {len(data['images'])}")

    # анализ категорий
    print("\n--- КАТЕГОРИИ (ID -> Name) ---")
    cat_map = {cat['id']: cat['name'] for cat in data['categories']}
    for cid, cname in cat_map.items():
        print(f"{cid}: {cname}")

    # проверка путей к картинкам
    print("\n--- ПРОВЕРКА ФАЙЛОВ (Первые 5) ---")
    found = 0
    missing = 0
    
    for img in data['images'][:5]:
        fname = img['file_name']
        # проверяем прямой путь
        full_path = os.path.join(images_base_dir, fname)
        
        if os.path.exists(full_path):
            print(f"✅ {fname}")
            found += 1
        else:
            print(f"❌ {fname} (Не найден в {images_base_dir})")
            missing += 1
            
    if missing > 0:
        print("\n⚠️ ВНИМАНИЕ: Скрипт не видит картинки. Возможно, в JSON пути прописаны с подпапками, а у нас плоская структура, или наоборот.")

    # статистика классов
    print("\n--- РАСПРЕДЕЛЕНИЕ АННОТАЦИЙ ---")
    anns = [cat_map.get(a['category_id'], 'Unknown') for a in data['annotations']]
    for k, v in Counter(anns).most_common():
        print(f"{k}: {v}")

if __name__ == "__main__":
    inspect_coco()