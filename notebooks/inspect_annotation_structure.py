import json
import os

# пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(os.path.dirname(BASE_DIR), "data", "raw", "annotation_data.json")

def check_one_annotation():
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Всего аннотаций: {len(data['annotations'])}")
    
    # ищем первую попавшуюся аннотацию с полем segmentation (если есть)
    sample = data['annotations'][0]
    
    print("\n--- ПРИМЕР АННОТАЦИИ ---")
    print(json.dumps(sample, indent=4))
    
    # проверка на segmentation
    if 'segmentation' in sample and len(sample['segmentation']) > 0:
        seg = sample['segmentation'][0]
        print(f"\n✅ Segmentation найдена! Количество точек: {len(seg) // 2}")
        print(f"Координаты: {seg}")
        
        if len(seg) == 8: # 4 точки * 2 (x,y)
            print("🚀 Это похоже на OBB (4 угла)!")
        elif len(seg) > 8:
            print("ℹ️ Это точный полигон (обводит контур). Тоже можно превратить в OBB.")
    else:
        print("\n❌ Segmentation отсутствует или пуста. Мы застряли с HBB.")

if __name__ == "__main__":
    check_one_annotation()