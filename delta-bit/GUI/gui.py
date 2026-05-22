from nicegui import ui
from pathlib import Path
import json
import shutil
import os

UPLOAD_DIR = Path("uploads")
CONFIG_DIR = Path("config")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

selected_files = set()

ui.label("🧠 Image Pipeline Config Builder").classes("text-2xl")


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


def refresh_file_list():
     file_container.clear()

     for f in sorted(UPLOAD_DIR.glob("*")):
         checkbox = ui.checkbox(f.name)

         def toggle(e, file=f):
             if e.value:
                 selected_files.add(str(file))
             else:
                 selected_files.discard(str(file))
         checkbox.on("update:model-value", toggle)

         file_container.add(checkbox)


refresh_file_list()


# # -------------------------
# # CONFIG
# # -------------------------
def generate_config():
     config = {
         "images": list(selected_files),
         "n_images": len(selected_files)
     }

     out_path = CONFIG_DIR / "config.json"
     out_path.write_text(json.dumps(config, indent=2))

     ui.notify(f"Config salvato: {out_path}")


ui.button("Generate config", on_click=generate_config)

ui.run()