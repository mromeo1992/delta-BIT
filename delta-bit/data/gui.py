from nicegui import ui
from pathlib import Path
import json
import shutil
import os

UPLOAD_DIR = Path("data/uploads")
CONFIG_DIR = Path("data/config")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

selected_files = set()

ui.label("🧠 DeLTA-BIT").classes("text-2xl")


# -------------------------
# FILE UPLOAD
# -------------------------
def handle_upload(e):

    print(e)

    filename = e.file.name
    temp_path = e.file._path

    save_path = UPLOAD_DIR / filename

    # copia il file temporaneo
    shutil.copy(temp_path, save_path)

    ui.notify(f'Salvato in {save_path}')


ui.upload(
    on_upload=handle_upload,
    auto_upload=True,
).props('accept=.nii,.nii.gz')





# # -------------------------
# # FILE LIST
# # -------------------------
file_container = ui.column()


# # -------------------------
# # CONFIG
# # -------------------------
def generate_config():
    selected_files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    config = {
         "images": list(selected_files),
         "n_images": len(selected_files)
     }

    out_path = CONFIG_DIR / "config.json"
    out_path.write_text(json.dumps(config, indent=2))

    ui.notify(f"Config salvato: {out_path}")


ui.button("Generate config", on_click=generate_config)

def run_mnireg():
    #devo chiamare il servizio di tools
    pass

ui.button("Run MNIREG", on_click=run_mnireg)

ui.run()