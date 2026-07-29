from pathlib import Path
import json

MODELS_DIR = Path("/data/MODELS")


def list_models():

    models = []

    if not MODELS_DIR.exists():
        return models

    for folder in sorted(MODELS_DIR.iterdir()):

        if not folder.is_dir():
            continue

        meta = folder / 'model_meta.json'
        model = folder / 'model.h5'

        if not (meta.exists() and model.exists()):
            continue

        with open(meta) as f:
            metadata = json.load(f)

        models.append({
            'name': folder.name,
            'meta': metadata,
        })

    return models
