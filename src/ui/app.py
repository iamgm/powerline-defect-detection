import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import base64
import random

#-----------------------------------------------------------------------------
# config
API_URL = "http://127.0.0.1:8000/predict"

# цветовая схема
THEME_COLOR = "#0078D7"  
BG_COLOR = "#F0F2F6"     

CLASS_COLORS = {
    "bad_insulator": "#FF2B2B",       
    "damaged_insulator": "#D02090",   
    "nest": "#FF8C00",                
    "festoon_insulators": "#00C853",  
    "polymer_insulators": "#00C853",  
    "vibration_damper": "#00BFFF",    
    "traverse": "#FFD700",            
    "safety_sign+": "#4169E1"         
}
ALL_CLASSES = list(CLASS_COLORS.keys())

# фразы для загрузки
SPINNER_PHRASES = [
    "Надеваем диэлектрические перчатки... 🧤",
    "Прозваниваем нейронные связи на предмет КЗ... ⚡",
    "Считаем воробьев на проводах... 🐦",
    "Ищем косинус фи в стоге сена... 🌾",
    "Заземляем ожидания... ⏚",
    "Протираем линзы виртуальных очков... 👓",
    "Торгуемся с трансформаторной будкой... 🏗️",
    "Выпрямляем синусоиду вручную... 〰️",
    "Уговариваем веса не улетать в бесконечность... 📉",
    "Объясняем нейронке, что птица — это не дефект... 🦅",
    "Матрицы перемножаются, искры летят... ✨",
    "Пытаемся найти глобальный минимум в чашке кофе... ☕",
    "Бэкпропагейтим до состояния просветления... 🧘",
    "GPU просит пощады, но мы продолжаем... 🔥",
    "Нормализуем данные и самооценку... 📏",
    "Слой за слоем, как бабушкин торт... 🍰",
    "Загружаем пиксели в ведро... 🪣",
    "Скармливаем данные тензорам. Кажется, им нравится... 😋",
    "Подождите, нейросеть пошла за синей изолентой... 🟦",
    "Спрашиваем мнение у ChatGPT, но он не отвечает... 🤖",
    "Генерируем оправдания для ложных срабатываний... 😅",
    "Квантуем пространство и время... 🌌",
    "Взламываем реальность через 443 порт... 🔓",
    "Вспоминаем формулу градиентного спуска... 📉",
    "Исправляем баги, созданные вчерашним мной... 🐛",
    "Молимся богам CUDA... 🙏",
    "Проверка пройдена на 99%. Остался 1% неопределенности... 🎲"
]

#-----------------------------------------------------------------------------
# zoom
def render_zoomable_image(image_pil, caption=""):
    img_copy = image_pil.copy()
    img_copy.thumbnail((800, 800)) 
    
    # получаем реальные размеры после ресайза
    img_w, img_h = img_copy.size
    
    buffered = io.BytesIO()
    img_copy.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    html_code = f"""
    <style>
        .zoom-container {{
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            cursor: crosshair;
            width: 100%;
            display: flex;             /* Центрируем картинку */
            justify-content: center;   /* Центрируем картинку */
        }}
        .zoom-img {{
            max-width: 100%;           /* 2. Используем max-width вместо width */
            height: auto;
            display: block;
            transition: transform 0.2s ease;
        }}
        .zoom-container:hover .zoom-img {{
            transform: scale(2.5);
            transform-origin: center center;
        }}
    </style>

    <div class="zoom-container" onmousemove="zoom(event)" onmouseleave="reset(event)">
        <img src="data:image/png;base64,{img_str}" class="zoom-img" id="img-{caption}">
    </div>
    <div style="margin-top: 5px; color: #555; font-size: 0.9em; text-align: center;">{caption}</div>

    <script>
        function zoom(e) {{
            var zoomer = e.currentTarget;
            var img = zoomer.querySelector('.zoom-img');
            var rect = zoomer.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            
            var xPercent = (x / rect.width) * 100;
            var yPercent = (y / rect.height) * 100;
            
            img.style.transformOrigin = xPercent + "% " + yPercent + "%";
        }}
        function reset(e) {{
            var img = e.currentTarget.querySelector('.zoom-img');
            img.style.transformOrigin = "center center";
        }}
    </script>
    """
    # утанавливаем высоту компонента равной высоте картинки + 50px на подпись
    st.components.v1.html(html_code, height=img_h + 50, scrolling=False)

#-----------------------------------------------------------------------------
# setup page
st.set_page_config(page_title="PowerLine Defect Detection", page_icon="⚡", layout="wide")

# CSS HACKS

st.markdown(f"""
    <style>
    :root {{ --primary-color: {THEME_COLOR}; }}
    div.stButton > button {{
        background-color: {THEME_COLOR};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: #005A9E;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    .css-164nlkn {{ display: none; }} 
    .streamlit-expanderHeader {{
        font-weight: bold;
        background-color: white;
        border-radius: 8px;
    }}
    /* фиксация сайдбара */
    section[data-testid="stSidebar"] {{
        position: sticky !important;
        top: 0 !important;
        height: 100vh !important;
        overflow-y: auto !important; /* Разрешить скролл внутри сайдбара */
        z-index: 1000 !important;
    }}
    </style>
""", unsafe_allow_html=True)

#-----------------------------------------------------------------------------
# state
if 'results' not in st.session_state:
    st.session_state.results = {} 
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'clean_expanded' not in st.session_state:
    st.session_state.clean_expanded = False

def reset_uploader():
    st.session_state.uploader_key += 1
    st.session_state.results = {}

#-----------------------------------------------------------------------------
# обрабатка 1 файла
def process_single_file(file_obj, model_key, conf):
    try:
        file_obj.seek(0)
        params = {"model_type": model_key, "conf_threshold": conf}
        files = {"file": ("image", file_obj, file_obj.type)}
        response = requests.post(API_URL, params=params, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def draw_detections(file_obj, detections, selected_classes):
    image = Image.open(file_obj).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    count_defects = 0
    count_visible = 0
    
    for det in detections:
        cls = det['class_name']
        if cls not in selected_classes:
            continue
            
        count_visible += 1
        if cls in ["bad_insulator", "damaged_insulator", "nest"]:
            count_defects += 1
            
        color = CLASS_COLORS.get(cls, "#FFFFFF")
        
        if det.get('polygon'):
            poly = [c for p in det['polygon'] for c in p]
            draw.polygon(poly, outline=color, width=4)
            txt_pos = tuple(det['polygon'][0])
        else:
            b = det['box']
            draw.rectangle([b['x1'], b['y1'], b['x2'], b['y2']], outline=color, width=4)
            txt_pos = (b['x1'], b['y1'])
            
        label = f"{cls} {det['confidence']:.2f}"
        bbox = draw.textbbox(txt_pos, label)
        draw.rectangle(bbox, fill=color)
        draw.text(txt_pos, label, fill="black")
        
    return image, count_defects, count_visible

#-----------------------------------------------------------------------------
# sidebar
with st.sidebar:
    
    #-----------------------------------------------------------------------------
    # Ссылка на профиль github
    
    
    # SVG икончка github
    svg_code = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.399 1.02 0 2.047.133 3.006.4 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>"""
    
    # кодируем в строку Base64
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    img_src = f"data:image/svg+xml;base64,{b64_str}"
    github_url = "https://github.com/iamgm"
    
    st.markdown(f"""
    <a href="{github_url}" target="_blank" style="text-decoration: none; display: block; margin-bottom: 20px;">
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 16px;
            color: #333;
            transition: 0.3s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        ">
            <img src="{img_src}" width="24" height="24" style="margin-right: 12px; display: block;">
            <span style="font-weight: 600; font-size: 16px;">GitHub Profile</span>
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    
    #-----------------------------------------------------------------------------
    
    st.title("⚙️ Настройки")
    
    model_choice = st.radio("Модель:", ("Fast (Small)", "Accurate (Large)"))
    model_key = "fast" if "Small" in model_choice else "accurate"
    
    st.divider()
    conf_threshold = st.slider("Порог уверенности:", 0.1, 0.9, 0.4, 0.05)
    
    st.divider()
    st.write("Фильтр классов:")
    
    try:
        selected_classes = st.pills(
            "Классы", options=ALL_CLASSES, default=ALL_CLASSES, selection_mode="multi", label_visibility="collapsed"
        )
    except AttributeError:
        selected_classes = st.multiselect("Показать:", ALL_CLASSES, default=ALL_CLASSES)

#-----------------------------------------------------------------------------
# main page
st.title("⚡ PowerLine Defect Detection")

# загрузка
with st.container():
    col_up, col_btn = st.columns([4, 1])
    with col_up:
        uploaded_files = st.file_uploader(
            "Перетащите файлы сюда:", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )
    with col_btn:
        st.write("") 
        st.write("") 
        if st.button("🗑️ Clear All"):
            reset_uploader()
            st.rerun()
#-----------------------------------------------------------------------------
# запуск первичного анализа
if uploaded_files:
    if st.button(f"▶️ ЗАПУСТИТЬ АНАЛИЗ ({len(uploaded_files)} ФОТО)", type="primary"):
        progress = st.progress(0)
        total_files = len(uploaded_files)
        
        for i, f in enumerate(uploaded_files):
            phrase = random.choice(SPINNER_PHRASES)
            spinner_text = f"[{i+1}/{total_files}] {phrase}"
            
            with st.spinner(spinner_text):
                res = process_single_file(f, model_key, conf_threshold)
                st.session_state.results[f.name] = {
                    "file_obj": f,
                    "data": res,
                    "model": model_key,
                    "checked_again": False 
                }
            
            progress.progress((i+1)/total_files)
        st.rerun()

#-----------------------------------------------------------------------------
# отображение результатов
if st.session_state.results:
    st.divider()
    
    defects_list = []
    clean_list = []
    
    for name, item in st.session_state.results.items():
        detections = item['data'].get('detections', [])
        visible_dets = [d for d in detections if d['class_name'] in selected_classes]
        has_defects = any(d['class_name'] in ["bad_insulator", "damaged_insulator", "nest"] for d in visible_dets)
        
        if has_defects:
            defects_list.append((name, item))
        else:
            clean_list.append((name, item))

    # блок 1. найдены дефекты
    if defects_list:
        st.subheader(f"🔴 Обнаружены дефекты ({len(defects_list)})")
        for name, item in defects_list:
            detections = item['data'].get('detections', [])
            img_res, cnt_def, cnt_vis = draw_detections(item['file_obj'], detections, selected_classes)
            
            with st.expander(f"⚠️ {name} | Дефектов: {cnt_def} | Модель: {item['model']}", expanded=True):
                st.caption("Наведите для увеличения 🔍")
                render_zoomable_image(img_res, caption="Результат")

    # блок 2. допроверка 
    if clean_list:
        
        # заголовок и кнопка Expand All
        col_head, col_toggle = st.columns([3, 1])
        with col_head:
            st.subheader(f"🟢 Не найдено ({len(clean_list)})")
        with col_toggle:
            btn_label = "📂 Раскрыть все" if not st.session_state.clean_expanded else "📂 Свернуть все"
            if st.button(btn_label):
                st.session_state.clean_expanded = not st.session_state.clean_expanded
                st.rerun()
        
        need_check_names = [name for name, item in clean_list if not item.get('checked_again')]
        
        if need_check_names:
            st.info(f"Есть {len(need_check_names)} файлов, где ничего не найдено. Попробовать Accurate модель?")
            if st.button("🕵️ Перепроверить 'Accurate' моделью"):
                prog_bar = st.progress(0)
                total_check = len(need_check_names)
                
                for i, name in enumerate(need_check_names):
                    phrase = random.choice(SPINNER_PHRASES)
                    with st.spinner(f"[{i+1}/{total_check}] {phrase}"):
                        item = st.session_state.results[name]
                        new_res = process_single_file(item['file_obj'], "accurate", conf_threshold)
                        st.session_state.results[name]['data'] = new_res
                        st.session_state.results[name]['model'] = "accurate (re-check)"
                        st.session_state.results[name]['checked_again'] = True
                    prog_bar.progress((i+1)/total_check)
                st.rerun()

        with st.container():
            for name, item in clean_list:
                detections = item['data'].get('detections', [])
                img_res, _, cnt_vis = draw_detections(item['file_obj'], detections, selected_classes)
                
                icon = "✅" if not item.get('checked_again') else "🕵️✅"
                status = "Чисто" if cnt_vis == 0 else f"Объектов: {cnt_vis} (Норма)"
                
                # используем состояние для expanded
                with st.expander(f"{icon} {name} | {status} | {item['model']}", expanded=st.session_state.clean_expanded):
                     st.caption("Наведите для увеличения 🔍")
                     render_zoomable_image(img_res, caption=name)
