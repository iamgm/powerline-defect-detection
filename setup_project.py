import os

def create_structure():
    # Define project structure
    project_structure = {
        "data": ["raw", "processed"],
        "notebooks": [],  # For EDA and experiments
        "weights": [],    # Store .pt models here
        "src": [
            "ml",         # Model training and inference logic
            "api",        # FastAPI backend
            "ui",         # Streamlit frontend
            "worker",     # Celery tasks
            "core"        # Configs and utils
        ],
        "deploy": [],     # Dockerfiles and configs
        "tests": []
    }

    # Define files to create with initial content
    files = {
        ".gitignore": "data/\nweights/\n__pycache__/\n.env\n.ipynb_checkpoints/\n*.pyc\n",
        "requirements.txt": "ultralytics\nfastapi\nuvicorn\nstreamlit\ncelery\nredis\npython-multipart\npydantic-settings\nclearml\n",
        "README.md": "# Power Line Defect Detection\n\nProject for DLS School.\n",
        "docker-compose.yml": "# Docker compose configuration will go here\n",
        
        # Source modules
        "src/__init__.py": "",
        "src/config.py": "import os\n\nclass Settings:\n    PROJECT_NAME = 'PowerLine Defects'\n    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')\n\nsettings = Settings()\n",
        
        # ML Module
        "src/ml/__init__.py": "",
        "src/ml/predictor.py": "# Inference logic (YOLO11/26 wrapper)\nclass DefectPredictor:\n    pass\n",
        "src/ml/trainer.py": "# Training pipeline with ClearML\n",
        
        # API Module
        "src/api/__init__.py": "",
        "src/api/main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'PowerLine API is running'}\n",
        "src/api/schemas.py": "# Pydantic models for request/response\n",
        
        # UI Module
        "src/ui/__init__.py": "",
        "src/ui/app.py": "import streamlit as st\n\nst.title('⚡ Power Line Defect Detection')\n",
        
        # Worker Module
        "src/worker/__init__.py": "",
        "src/worker/celery_app.py": "# Celery app configuration\n",
        "src/worker/tasks.py": "# Async tasks definitions\n",
        
        # Dockerfiles
        "deploy/Dockerfile.api": "# Dockerfile for FastAPI\n",
        "deploy/Dockerfile.ui": "# Dockerfile for Streamlit\n"
    }

    print(f"🚀 Initializing project structure...")

    # Create directories
    for root, subdirs in project_structure.items():
        os.makedirs(root, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(root, subdir), exist_ok=True)
            # Create __init__.py in python packages
            if root == "src":
                with open(os.path.join(root, subdir, "__init__.py"), "w") as f:
                    pass

    # Create files
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {path}")

    print("\n✨ Project structure created successfully!")

if __name__ == "__main__":
    create_structure()