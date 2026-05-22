from nicegui import ui
import project_manager as pm
import shutil
from pathlib import Path


# =====================================================
# STATO GLOBALE
# =====================================================
current_project = None
uploaded_file = None
table = None
drawer_container = None


UPLOAD_DIR = Path('/tmp')


# =====================================================
# PROJECT SELECTION
# =====================================================
def set_project(name):
    global current_project
    current_project = name
    ui.notify(f'Progetto attivo: {name}')
    refresh_table()


def refresh_menu():
    drawer_container.clear()

    for p in pm.list_projects():
        ui.button(
            p,
            icon='folder',
            on_click=lambda name=p: set_project(name)
        ).props('flat').move(drawer_container)


# =====================================================
# TABLE
# =====================================================
def refresh_table():
    if not current_project:
        table.rows = []
    else:
        table.rows = pm.load_subjects(current_project)

    table.update()


# =====================================================
# UPLOAD HANDLER (CORRETTO NICEGUI)
# =====================================================
def handle_upload(e):
    # Usiamo la struttura che funziona sul tuo NiceGUI: e.file
    filename = e.file.name
    save_path = UPLOAD_DIR / filename

    # Se vuoi usare shutil.copy come nell'altro script (metodo più veloce e sicuro):
    try:
        shutil.copy(e.file._path, save_path)
    except AttributeError:
        # Se e.file._path non dovesse esistere per file piccoli in memoria,
        # leggiamo il file in modalità standard:
        with open(save_path, "wb") as f:
            f.write(e.file.read())

    ui.notify(f"Caricato: {filename}")

    global uploaded_file
    uploaded_file = {
        "name": filename,
        "tmp_path": str(save_path)
    }


# =====================================================
# CREATE SUBJECT
# =====================================================
def submit_subject():
    global uploaded_file

    if not current_project:
        ui.notify('Seleziona un progetto', color='red')
        return

    if not uploaded_file:
        ui.notify('Carica un file NIfTI', color='red')
        return

    pm.create_subject(
        current_project,
        name_input.value,
        info_input.value,
        uploaded_file["tmp_path"],
        uploaded_file["name"]
    )

    name_input.value = ''
    info_input.value = ''
    upload.reset()
    uploaded_file = None

    subject_dialog.close()
    refresh_table()


def open_subject_dialog():
    if not current_project:
        ui.notify('Seleziona un progetto', color='red')
        return
    subject_dialog.open()


# =====================================================
# DIALOG: SUBJECT
# =====================================================
with ui.dialog() as subject_dialog, ui.card():

    ui.label('Carica soggetto').classes('text-h6')

    name_input = ui.input('Nome soggetto')
    info_input = ui.textarea('Info')

    upload = ui.upload(
        label='File NIfTI (.nii / .nii.gz)',
        auto_upload=True,
        multiple=False,
        on_upload=handle_upload
    )

    ui.button('Crea soggetto', on_click=submit_subject)


# =====================================================
# DIALOG: PROJECT
# =====================================================
with ui.dialog() as project_dialog, ui.card():

    ui.label('Nuovo progetto').classes('text-h6')

    project_name = ui.input('Nome progetto')

    def create_project():
        if pm.new_project(project_name.value):
            project_name.value = ''
            project_dialog.close()
            refresh_menu()

    ui.button('Crea progetto', on_click=create_project)


# =====================================================
# DRAWER MENU
# =====================================================
with ui.left_drawer() as drawer:

    ui.label('Progetti').classes('text-h6')

    ui.button('Nuovo progetto', icon='add', on_click=project_dialog.open)

    ui.separator()

    drawer_container = ui.column()

refresh_menu()


# =====================================================
# HEADER
# =====================================================
with ui.header():
    ui.label('NIfTI Project Manager')

    ui.button(icon='menu', on_click=lambda: drawer.toggle())


# =====================================================
# DASHBOARD
# =====================================================
with ui.column().classes('w-full p-4'):

    ui.label('Subjects').classes('text-h5')

    table = ui.table(
        columns=[
            {'name': 'id', 'label': 'ID', 'field': 'id'},
            {'name': 'name', 'label': 'Name', 'field': 'name'},
            {'name': 'info', 'label': 'Info', 'field': 'info'},
        ],
        rows=[]
    )

    ui.button(
        'Carica soggetto',
        icon='upload',
        on_click=open_subject_dialog
    )


ui.run()