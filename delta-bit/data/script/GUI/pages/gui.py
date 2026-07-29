import zipfile
import requests
import httpx
from nicegui import ui, run, app, background_tasks
from pathlib import Path
import json
import shutil
import os
from script.GUI import utility
import uuid
import asyncio

saved_patients = []
selected_ids = set()
selected_files = set()

table = None
btn = None

job_running = False
pending_files = []
id_state = {}

UPLOAD_DIR = Path("/tmp/uploads")
CONFIG_DIR = Path("/data/config")
STAGING_DIR = Path('/data/staging')
STAGING_DIR.mkdir(parents=True, exist_ok=True)
initialize_config = os.path.join(CONFIG_DIR, "saved_config.json")
MODELS_DIR = Path("/data/MODELS")
model_data_config_file='/data/script/utils/config_file.json'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
nifti_folder = Path("/data/NIFTI")
nifti_folder.mkdir(parents=True, exist_ok=True)



# # -------------------------
# # CONFIG
# # -------------------------
def add_to_database():
    subjects = sorted(sub for sub in os.listdir(UPLOAD_DIR))
    
    for sub in subjects:
        subdir= os.path.join(nifti_folder, sub)
        os.makedirs(subdir, exist_ok=True)
        src= next(UPLOAD_DIR.joinpath(sub).iterdir())
        dst= os.path.join(subdir, 'nativeT1.nii.gz')
        shutil.move(src, dst)

    shutil.rmtree(STAGING_DIR)
    shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)


    ui.notify(f"Data loaded, refreshing database")
    load_and_refresh()

def reset_state():
    global saved_patients, selected_ids , selected_files

    #output_container.set_text('Selected: none')

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
        ui.notify("Subject(s) removed",type="warning")

    sel = table.selected
    if len(sel)>0:
        #ui.notify(f"Removing subject: "+', '.join(r['id'] for r in sel))
        with ui.dialog() as dialog, ui.card():
            ui.label('Subjects:\n'+'\n'.join(r['id'] for r in sel)).style('white-space: pre-line')
            ui.label('Are beeing removed. Are you sure?').style('white-space: pre-line')

            with ui.row():
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Confirm', on_click=lambda: [delete_action(),reset_state(), load_and_refresh(), dialog.close()])

        dialog.open()

async def delete_later(path, delay=3600):

    print(f'Scheduled deletion: {path}')
    #ui.notify(f'Scheduled deletion of {os.path.basename(path)} in {delay} seconds', type='info')

    await asyncio.sleep(delay)

    try:
        os.remove(path)
        print(f'Deleted: {path}')
    except Exception as e:
        print(f'Error deleting {path}: {e}')      

def export_selection():


    async def export_action(sel):
        import tempfile
        tmp = tempfile.NamedTemporaryFile(
            suffix='.zip',
            delete=False
        )

        zip_path =tmp.name
        tmp.close()

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for sub in sel:
                sub_dir = nifti_folder / sub["id"]

                for file in sub_dir.glob("*"):
                    zipf.write(
                        file,
                        arcname=f"{sub['id']}/{file.name}"
                    )

        ui.download.file(
            zip_path,
            filename='exported_subjects.zip'
        )

        ui.notify(
            f"Exporting subjects: {', '.join(r['id'] for r in sel)}",
            type='positive'
        )
        background_tasks.create(delete_later(zip_path))

    async def confirm_export():
        dialog.close()
        await export_action(sel)        

    sel = table.selected
    if len(sel)>0:
        with ui.dialog() as dialog, ui.card():
            ui.label('Exporting subjects:\n'+'\n'.join(r['id'] for r in sel)).style('white-space: pre-line')
            ui.label('This will export the selected subjects to a specified location. Are you sure?').style('white-space: pre-line')

            with ui.row():
                ui.button('Cancel', on_click=dialog.close)
                #ui.button('Confirm', on_click=lambda: [export_action(sel), dialog.close()])
                ui.button('Confirm', on_click=lambda: confirm_export())
        dialog.open()

        
        #output_container = ui.label('Selected: none')

def create_config(side):
    sel = table.selected
    if len(sel)>0:
        subjects=[sub['id'] for sub in sel]        
        meta = [f for f in saved_patients if f["id"] in subjects ]

        config= { "subjects": {f['id'] : {"images" : f["images"], "registered":f["registered"], "predictions":f["predictions"], "native_predictions":f["native_predictions"], "hemisphere_side": [side] } for f in meta}}
        
        out_path = CONFIG_DIR / "config.json"
        out_path.write_text(json.dumps(config, indent=4))
            


async def run_vim():

    global job_running, btn

    if job_running:
        ui.notify(
            "A job is already running",
            type="warning"
        )
        return


    # =============================
    # MODEL LIST
    # =============================

    models_list = sorted([
        f for f in os.listdir(MODELS_DIR)
        if os.path.isdir(os.path.join(MODELS_DIR, f))
    ])


    # =============================
    # DIALOG
    # =============================

    with ui.dialog() as dialog, ui.card():

        ui.label(
            'Select model and hemisphere side before running VIM.'
        ).classes('text-h6')


        with ui.row():
            ui.label('Select model:')

            select_model = ui.select(
                options=models_list,
                value=models_list[0] if models_list else None
            ).classes('w-64')


        with ui.row():
            ui.label('Select hemisphere side:')

            side_select = ui.select(
                options=[
                    'left',
                    'right',
                    'both'
                ],
                value='left'
            ).classes('w-64')



        async def confirm():

            if select_model.value is None:

                ui.notify(
                    "Please select a model",
                    type="warning"
                )
                return


            model = select_model.value
            side = side_select.value


            dialog.close()


            await execute_vim(
                model,
                side
            )



        with ui.row():

            ui.button(
                'Cancel',
                on_click=dialog.close
            )

            ui.button(
                'Confirm',
                on_click=confirm
            )


    dialog.open()



async def execute_vim(model, side):

    global job_running, btn


    if job_running:
        ui.notify(
            "A job is already running",
            type="warning"
        )
        return


    job_running = True

    if btn is not None:
        btn.disable()



    def write_model_to_config(model):

        model_meta = os.path.join(
            MODELS_DIR,
            model,
            'model_meta.json'
        )


        with open(model_meta) as f:
            model_meta_data = json.load(f)


        model_meta_data['model']['path_model'] = os.path.join(
            MODELS_DIR,
            model,
            'model.h5'
        )


        with open(model_data_config_file, "w") as f:
            json.dump(
                model_meta_data,
                f,
                indent=4
            )



    try:

        # -------------------------
        # Update model configuration
        # -------------------------

        write_model_to_config(model)


        # -------------------------
        # Create prediction config
        # -------------------------

        create_config(side)



        ui.notify(
            f"Running VIM prediction\n"
            f"Model: {model}\n"
            f"Hemisphere: {side}"
        )


        # -------------------------
        # Call TensorFlow container
        # -------------------------

        response = await run.io_bound(
            requests.post,
            "http://tf:9000/predict"
        )



        if response.status_code == 200:

            ui.notify(
                "VIM prediction completed successfully!",
                type="positive"
            )


        else:

            ui.notify(
                f"Prediction error: "
                f"{response.status_code}\n{response.text}",
                type="negative"
            )



    except Exception as e:

        ui.notify(
            f"VIM execution failed:\n{e}",
            type="negative"
        )



    finally:

        job_running = False


        if btn is not None:
            btn.enable()


        load_and_refresh()


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
        for f in files:
            if f.startswith('vim_prediction') and not f.startswith('vim_prediction_native'):
                entry["predictions"].append(os.path.join(folder, f))
            if f.startswith('vim_prediction_native') and f.endswith('.nii.gz'):
                entry["native_predictions"].append(os.path.join(folder, f))

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
@app.post("/refresh")
def load_and_refresh():
    global saved_patients

    try:
        saved_patients = list_uploaded_files()
    except Exception as e:
        saved_patients = []
        ui.notify(f"Error loading database: {e}")

    refresh_table()
    ui.notify(f"Loaded {len(saved_patients)} subjects")


async def handle_view_mri(msg):
    async def chose_mri(r):
        options=[line["type"] for line in r["files"] if line["type"]=="Native Image" or line ["type"] == "MNI Registered" ]
        with ui.dialog() as dialog, ui.card():
            ui.label("Choose image space").classes("text-h6")

            select = ui.select(
                options=options,
                value='Native Image'
            ).classes('w-64')

            def confirm():
                global selected_value
                selected_value = select.value
                ui.notify(f'{selected_value} selected')
                dialog.close()

            with ui.row():
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Confirm', on_click=confirm)

        results = await dialog 


        path=[p["path"] for p in r["files"] if p["type"]==selected_value]
        if selected_value=="Native Image":
            mask_path=[p["path"] for p in r["files"] if p["type"]=="Native Prediction"] 
            if len(mask_path)==0:
                mask_path=[None] # placeholder per non mandare lista vuota
        else:
            mask_path=[p["path"] for p in r["files"] if p["type"]=="VIM Prediction"] 
            if len(mask_path)==0:
                mask_path=[None] # placeholder per non mandare lista vuota
        
        #ui.notify([path[0], mask_path[0]])
        #return path[0], mask_path[0]
        return path[0], mask_path

    row_id = msg.args
    row = next(r for r in table.rows if r['id'] == row_id)
    #ui.notify("print "+str(chose_mri(row)))
    to_open= await chose_mri(row)
    #ui.notify(to_open)
    # esempio: apri primo file MRI
    if row['files']:
        utility.open_viewer(to_open[0], mask_path=to_open[1])    

# =====================================================
# UPLOAD HANDLER (PICCOLI + GRANDI FILE)
# =====================================================
async def handle_upload(e):
    file = e.file

    unique_name = f"{uuid.uuid4()}_{file.name}"
    staging_path = STAGING_DIR / unique_name

    temp_path = getattr(file, "_path", None)

    # -----------------------------
    # CASO 1: file su disco
    # -----------------------------
    if temp_path and Path(temp_path).exists():
        shutil.copy(temp_path, staging_path)

    # -----------------------------
    # CASO 2: file in memoria
    # -----------------------------
    else:
        data = file.read()
        if asyncio.iscoroutine(data):
            data = await data
        staging_path.write_bytes(data)

    sub_id= file.name.split('_')[0]
    if file.name.split('_')[0]== file.name:
        sub_id= file.name.split('.')[0]

    pending_files.append({
        "staging_path": staging_path,
        "original_name": file.name,
        "id": sub_id
    })

    ui.notify(f"Staged: {file.name}")


# =====================================================
# DIALOG CONFIRM IDS (ROBUSTO)
# =====================================================
def open_confirm_dialog():
    if not pending_files:
        ui.notify("No files uploaded")
        return

    with ui.dialog() as dialog, ui.card():
        ui.label("Confirm Subject IDs").classes("text-h6")

        inputs = []

        for item in pending_files:
            ui.label(item["original_name"])

            inp = ui.input(
                value=item["id"],
                placeholder="Subject ID"
            ).classes("w-60")

            inputs.append(inp)

        def confirm():
            def get_existing_subject_ids():
                dirs = [UPLOAD_DIR, nifti_folder]

                return {
                    p.name.strip().lower()
                    for d in dirs
                    for p in d.iterdir()
                    if p.is_dir()
                }
            ids = [inp.value.strip().lower() for inp in inputs]

            # 1. check vuoti
            if any(not i for i in ids):
                ui.notify("All Subject IDs must be filled", type="negative")
                return

            # 2. check duplicati nel batch corrente
            if len(ids) != len(set(ids)):
                ui.notify("Duplicate Subject IDs in this upload", type="negative")
                return

            # 3. check contro "database" (cartelle esistenti)
            existing_ids = get_existing_subject_ids()

            conflicts = set(ids) & existing_ids

            if conflicts:
                ui.notify(
                    f"IDs already exist: {', '.join(conflicts)}",
                    type="negative"
                )
                return

            # salva
            for i, item in enumerate(pending_files):
                item["id"] = inputs[i].value.strip()

            dialog.close()
            process_upload()

        def cancel():
            for item in pending_files:
                if item["staging_path"].exists():
                    item["staging_path"].unlink()
            pending_files.clear()
            dialog.close()

        with ui.row():
            ui.button("Confirm", on_click=confirm)
            ui.button("Cancel", on_click=cancel)

    dialog.open()


# =====================================================
# FINAL PROCESSING
# =====================================================
def process_upload():
    for item in pending_files:
        subject_dir = UPLOAD_DIR / item["id"]
        subject_dir.mkdir(parents=True, exist_ok=True)

        shutil.move(
            str(item["staging_path"]),
            subject_dir / item["original_name"]
        )

    ui.notify(f"Processed {len(pending_files)} files")

    pending_files.clear()
    id_state.clear()


# =====================================================
# UI
# =====================================================
async def handle_dicom_upload(e):
    file = e.file

    unique_name = f"{uuid.uuid4()}_{file.name}"
    staging_path = STAGING_DIR / unique_name

    temp_path = getattr(file, "_path", None)

    if temp_path and Path(temp_path).exists():
        shutil.copy(temp_path, staging_path)
    else:
        data = await file.read()
        staging_path.write_bytes(data)

    async with httpx.AsyncClient() as client:
        await client.post(
            'http://tools:8000/upload_dcm',
            params={'zip_path': str(staging_path)}
        )






def query():


    with ui.row().classes('w-full items-center p-4'):

        # Pulsante Home a sinistra
        ui.button(
            icon='home',
            on_click=lambda: ui.navigate.to('/')
        ).props('round flat').classes('w-10 h-10')


        # Titolo centrato
        with ui.row().classes('absolute left-1/2 transform -translate-x-1/2'):
            ui.label("🧠 DeLTA-BIT").classes("text-2xl font-bold")

    global table
    global btn 



    # =====================================================
    # GUI
    # =====================================================

    with ui.column().classes('w-full p-4'):

        ui.label('Database').classes('text-h5')

        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
            {'name': 'view', 'label': '', 'field': 'view', 'align': 'center'},
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
            <q-tr :props="props" class="cursor-pointer">

                <!-- SELECT -->
                <q-td auto-width>
                    <q-checkbox v-model="props.selected" />
                </q-td>

                <!-- ID -->
                <q-td key="id" :props="props" class="text-left">
                    {{ props.row.id }}
                </q-td>

                <!-- VIEW BUTTON (NUOVO) -->
                <q-td key="view" class="text-center" @click.stop>
                    <q-btn
                        size="sm"
                        color="secondary"
                        icon="visibility"
                        round
                        dense
                        @click="() => $parent.$emit('view_mri', props.row.id)"
                    />
                </q-td>

                <!-- EXPAND -->
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

            <!-- EXPANDED ROW -->
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
            #ui.button("Show selected", on_click=show_selected)
            btn = ui.button("Run VIM", on_click=run_vim)
            ui.button("Export selection", on_click=export_selection)
            ui.button("Remove selection", on_click=remove_selection)

        # Nota: serve richiamare l'oggetto nel contesto per renderizzarlo a schermo
        #output_container

    # =====================================================
    # INIT
    # =====================================================

    



    table.on('view_mri', handle_view_mri)
    load_and_refresh()      


    # =====================================================
    # STATE
    # =====================================================


    pending_files = []



    # stato reale (FONTE DI VERITÀ)
    id_state = {}



            




    with ui.row().classes('q-mt-md gap-4').style('width: 100%; flex-wrap: nowrap;'):

        with ui.column().classes('col'):
            ui.label("MRI Upload Manager").classes("text-h5")
            ui.upload(
                on_upload=handle_upload,
                multiple=True,
                auto_upload=False,
            ).props('accept=.nii,.nii.gz')

        with ui.column().classes('col'):
            ui.label("MRI DICOM Upload Manager").classes("text-h5")
            ui.upload(
                on_upload=handle_dicom_upload,
                multiple=False,
                auto_upload=False,
            ).props('accept=.zip')







    db_ready = False
    with ui.row().classes('gap-2 q-mt-md'):

        def open_and_unlock():
            global db_ready
            open_confirm_dialog()
            db_ready = True
            db_button.enable()

        ui.button("Configure IDs & Upload", on_click=open_and_unlock)

        db_button = ui.button(
            "Add to the database",
            on_click=add_to_database
        ).disable()
