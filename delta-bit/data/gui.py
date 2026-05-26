from nicegui import ui
from pathlib import Path
import json
import shutil
import os

UPLOAD_DIR = Path("/data/uploads")
CONFIG_DIR = Path("/data/config")
initialize_config = os.path.join(CONFIG_DIR, "saved_config.json")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

nifti_folder = Path("/data/NIFTI")
nifti_folder.mkdir(parents=True, exist_ok=True)
selected_files = set()

ui.label("🧠 DeLTA-BIT").classes("text-2xl")

def reset_state():
    global saved_patients, selected_ids , selected_files

    output_container.set_text('Selected: none')

    saved_patients = []
    selected_ids.clear()
    selected_files.clear()
    table.selected = []

def remove_selection():
    def delete_action():
        global nifti_folder
        for sub in sel:
            sub_dir=nifti_folder / sub["id"]
            shutil.rmtree(sub_dir)
        ui.notify("Subject(s) removed")

    sel = table.selected
    if len(sel)>0:
        #ui.notify(f"Removing subject: "+', '.join(r['id'] for r in sel))
        with ui.dialog() as dialog, ui.card():
            ui.label('Subjects:\n'+'\n'.join(r['id'] for r in sel)).style('white-space: pre-line')
            ui.label('Are beeing removed. Are you sure?').style('white-space: pre-line')

            with ui.row():
                ui.button('Annulla', on_click=dialog.close)
                ui.button('Conferma', on_click=lambda: [delete_action(),reset_state(), load_and_refresh(), dialog.close()])

        dialog.open()
        
        #output_container = ui.label('Selected: none')

def create_config():
    sel = table.selected
    if len(sel)>0:
        subjects=[sub['id'] for sub in sel]        
        meta = [f for f in saved_patients if f["id"] in subjects ]

        config= { "subjects": {f['id'] : {"images" : f["images"], "registered":f["registered"], "predictions":f["predictions"], "native_predictions":f["native_predictions"] } for f in meta}}
        
        out_path = CONFIG_DIR / "config.json"
        out_path.write_text(json.dumps(config, indent=4))
            


def run_vim():
    print("Running VIM prediction...")
    create_config()
    import requests
    try:
        response = requests.post("http://tf:9000/predict")
        if response.status_code == 200:
            ui.notify("VIM prediction completed successfully!")
        else:
            ui.notify(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        ui.notify(f"Request failed: {e}")


# =====================================================
# GLOBAL STATE
# =====================================================
saved_patients = []
selected_ids = set()

# Definiamo un container per l'output in modo da poterlo aggiornare facilmente
output_container = ui.label('Selected: none')


# =====================================================
# DATA LOADING
# =====================================================
def list_uploaded_files():
    if not os.path.exists(nifti_folder):
        return []
        
    subjects = sorted(
        f for f in os.listdir(nifti_folder)
        if os.path.isdir(os.path.join(nifti_folder, f))
    )

    conf = []
    for sub in subjects:
        folder = os.path.join(nifti_folder, sub)
        files = sorted(os.listdir(folder))

        entry = {
            "id": sub,
            "images": [],
            "registered": [],
            "predictions": [],
            "native_predictions": []
        }

        if 'nativeT1.nii.gz' in files:
            entry["images"].append(os.path.join(folder, 'nativeT1.nii.gz'))
        if 'T1_mni.nii.gz' in files:
            if 'output0GenericAffine.mat' in files and 'outputInverseWarped.nii.gz' in files:
                entry["registered"].append(os.path.join(folder, 'T1_mni.nii.gz'))
        if 'vim_prediction.nii.gz' in files:
            entry["predictions"].append(os.path.join(folder, 'vim_prediction.nii.gz'))
        if 'vim_prediction_native.nii.gz' in files:
            entry["native_predictions"].append(os.path.join(folder, 'vim_prediction_native.nii.gz'))

        conf.append(entry)
    
    save_conf= CONFIG_DIR / 'database.json'
    save_conf.write_text(json.dumps(conf, indent=4))
    

    ui.notify(f"Loaded {len(conf)} subjects")
    return conf


# =====================================================
# TABLE REFRESH
# =====================================================

def refresh_table():

    rows = []

    for s in saved_patients:

        files = []

        for f in s.get('images', []):
            files.append({'type': 'Native Image', 'path': f})

        for f in s.get('registered', []):
            files.append({'type': 'MNI Registered', 'path': f})

        for f in s.get('predictions', []):
            files.append({'type': 'VIM Prediction', 'path': f})

        for f in s.get('native_predictions', []):
            files.append({'type': 'Native Prediction', 'path': f})

        rows.append({
            'id': s['id'],
            'files': files,
        })

    table.rows = rows
    table.update()


# =====================================================
# LOAD DATA
# =====================================================

def load_and_refresh():
    global saved_patients

    try:
        saved_patients = list_uploaded_files()
    except Exception as e:
        saved_patients = []
        ui.notify(f"Error loading database: {e}")

    refresh_table()
    ui.notify(f"Loaded {len(saved_patients)} subjects")


# =====================================================
# SHOW SELECTED
# =====================================================

def show_selected():
    sel = table.selected  # <-- NATIVE NICEGUI

    if not sel:
        output_container.set_text('Selected: none')
        return

    output_container.set_text(
        'Selected: ' + ', '.join(r['id'] for r in sel)
    )


# =====================================================
# GUI
# =====================================================

with ui.column().classes('w-full p-4'):

    ui.label('Database').classes('text-h5')

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
        {'name': 'expand', 'label': '', 'field': 'expand', 'align': 'center'},
    ]

    table = ui.table(
        columns=columns,
        rows=[],
        row_key='id',
        selection='multiple',   # Attiva la selezione multipla nell'header
    ).classes('w-full')


    # EXPAND SLOT (Aggiornato con il checkbox funzionante)
    table.add_slot('body', r'''
    <q-tr :props="props" class="cursor-pointer" @click="props.selected = !props.selected">

        <q-td auto-width>
            <q-checkbox v-model="props.selected" />
        </q-td>

        <q-td key="id" :props="props" class="text-left">
            {{ props.row.id }}
        </q-td>

        <q-td key="expand" class="text-center" @click.stop>
            <q-btn
                size="sm"
                color="primary"
                round
                dense
                :icon="props.expand ? 'remove' : 'add'"
                @click="props.expand = !props.expand"
            />
        </q-td>

    </q-tr>

    <q-tr v-show="props.expand" :props="props">
        <q-td colspan="100%">

            <div class="text-subtitle2 q-mb-sm">Files</div>

            <div
                v-for="file in props.row.files"
                :key="file.path"
                class="row items-center q-gutter-sm q-mb-xs"
            >
                <q-badge color="primary">{{ file.type }}</q-badge>
                <span class="text-body2">{{ file.path }}</span>
            </div>

        </q-td>
    </q-tr>
    ''')


    # BUTTONS
    with ui.row().classes('gap-2 q-mt-md'):
        ui.button("Refresh DB", on_click=load_and_refresh)
        ui.button("Show selected", on_click=show_selected)
        ui.button("Run VIM", on_click=run_vim)
        ui.button("Remove selection", on_click=remove_selection)

    # Nota: serve richiamare l'oggetto nel contesto per renderizzarlo a schermo
    output_container

# =====================================================
# INIT
# =====================================================

load_and_refresh()





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
    auto_upload=False,
    multiple=True,
).props('accept=.nii,.nii.gz')



# # -------------------------
# # CONFIG
# # -------------------------
def add_to_database():
    selected_files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    subjects = sorted(os.path.basename(f).split('_')[0] for f in selected_files)
    t1s=[]
    for idx, sub in enumerate(subjects):
        subdir= os.path.join(nifti_folder, sub)
        os.makedirs(subdir, exist_ok=True)
        src= os.path.join(UPLOAD_DIR, selected_files[idx])
        dst= os.path.join(subdir, 'nativeT1.nii.gz')
        t1s.append(dst)
        shutil.move(src, dst)


    ui.notify(f"Data loaded, refreshing database")
    load_and_refresh()


ui.button("Add to the database", on_click=add_to_database)







ui.run()