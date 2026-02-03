# используем легкий Python 3.11
FROM python:3.11-slim

# устанавливаем системные зависимости для OpenCV (важно для YOLO)
# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# исправленая команда для Debian Trixie
RUN apt-get update && apt-get install -y \\
    libgl1 \\
    libglib2.0-0t64 \\
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*



# создаем рабочую директорию
WORKDIR /app

# копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь проект в контейнер
COPY . .

# даем права на выполнение скрипта запуска
RUN chmod +x start.sh

# открываем порт 7860 (Hugging Face)
EXPOSE 7860

# команда запуска
CMD ["./start.sh"]