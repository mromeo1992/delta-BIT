import json
from pathlib import Path
from nicegui import ui

FT_FOLDER = Path("/data/fine_tuning")

def validate_model_name(value):
    if not value:
        return "Model name is required"

    if (FT_FOLDER / value).exists():
        return "A model with this name already exists"

    return None

