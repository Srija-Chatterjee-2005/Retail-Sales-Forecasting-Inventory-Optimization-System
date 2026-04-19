import os

def ensure_directories():
    folders = [
        "data",
        "outputs",
        "images",
        "models",
        "reports",
        "app"
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)