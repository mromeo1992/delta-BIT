import json
from pathlib import Path

import requests
from nicegui import ui, run

FT_FOLDER = Path("/data/fine_tuning")

def validate_model_name(value):
    if not value:
        return "Model name is required"

    if (FT_FOLDER / value).exists():
        return "A model with this name already exists"

    return None


async def get_finetuning_status():

    response = await run.io_bound(
        requests.get,
        "http://tf:9000/fine_tuning/status",
        timeout=2
    )

    return response.json()
