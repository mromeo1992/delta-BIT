from nicegui import ui, run, app, background_tasks
from pathlib import Path
import requests
import asyncio

from script.GUI.services.datasets import list_datasets
from script.GUI.services.datasets import handle_dataset_upload
from script.GUI.services.datasets import get_dataset_images
from script.GUI.services.datasets import build_rows
#from script.GUI.services.datasets import handle_view_mri

from script.GUI.services.models import list_models

from script.GUI.services.finetuning import validate_model_name

from script.GUI import utility

from script.GUI.services.tensorboard import start_tensorboard
from script.GUI.services.tensorboard import stop_tensorboard

FT_FOLDER = Path("/data/fine_tuning")
FT_FOLDER.mkdir(parents=True, exist_ok=True)

job_running = False

def go_home():
    stop_tensorboard()

    ui.navigate.to('/')

async def finetune_model(config):
    global job_running
    if job_running:
        ui.notify('A fine-tuning job is already running', type='warning')
        return

    job_running = True

    try:
        #model_folder = setup_ftmodel(config)
        #ui.notify(f'Fine-tuning model folder created at: {model_folder}', type='positive')
        
        notif = await run.io_bound(
            requests.post,
            "http://tf:9000/fine_tuning",
            json= config
        )
        ui.notify(f'Fine-tuning job response: {notif.text}', type='positive')
        ui.notify('Fine-tuning job started', type='positive')
    except Exception as e:
        ui.notify(f'Error starting fine-tuning job: {e}', type='negative')
    finally:
        job_running = False


def finetune():

    # ---------- INITIALIZE OBJECTS -------------------------------------------

    start_tensorboard()

    train_table = None
    test_table = None

    datasets = list_datasets()
    models = list_models()

    current_dataset = {
        'name': datasets[0] if datasets else None
    }

    current_model = {
        'value': models[0] if models else None
    }

    dataset_select = None
    model_select = None


    # ---------- LOADERS -----------------------------------------------------

    def load_dataset(dataset_name):

        current_dataset['name'] = dataset_name
        if dataset_select.value != dataset_name:
            dataset_select.value = dataset_name
            dataset_select.update()

        train, test = get_dataset_images(dataset_name)

        train_table.rows = build_rows(train)
        train_table.update()

        test_table.rows = build_rows(test)
        test_table.update()

    def load_Dbit_model(model_name):

        model = next(
            m for m in list_models()
            if m['name'] == model_name
        )

        current_model['value'] = model

        if model_select.value != model_name:
            model_select.value = model_name
            model_select.update()

        show_model.refresh()


    # ---------- VIEWER -------------------------------------------------------

    async def handle_view_mri(e):

        dataset_name = current_dataset['name']

        tab = e.args['table']
        row_name = e.args['file']
        async def get_paths():
            if tab == 'train':
                img_path = f"/data/datasets/{dataset_name}/imagesTr/{row_name}"
                msk_path = f"/data/datasets/{dataset_name}/labelsTr/{row_name}"
            else:
                img_path = f"/data/datasets/{dataset_name}/imagesTs/{row_name}"
                msk_path = f"/data/datasets/{dataset_name}/labelsTs/{row_name}"
            return img_path, msk_path
        
        img_path, msk_path = await get_paths()
        ui.notify(
            f"paths: {img_path}, {msk_path}"
        )
        utility.open_viewer(img_path, [msk_path])


    # ---------- HEADER -------------------------------------------------------

    with ui.header().classes('items-center justify-between'):

        with ui.row().classes('items-center'):
            ui.button(
                icon='home',
                on_click=go_home
            ).props('flat color=white')
            
            ui.button(
                icon='menu',
                on_click=lambda: drawer.toggle()
            ).props('flat color=white')


            ui.label('🧠 DeLTA-BIT').classes(
                'text-3xl font-bold ml-2'
            )

        ui.label('Fine-tuning Workspace').classes(
            'text-lg'
        )


    # ---------- LEFT DRAWER --------------------------------------------------

    with ui.left_drawer().classes('bg-grey-1 w-72') as drawer:

        drawer_content = ui.column().classes('w-full')

        refresh_drawer(
            drawer_content,
            'Datasets',
            load_dataset,
            load_Dbit_model
            )


    # ---------- TABS ---------------------------------------------------------

    with ui.tabs(
        on_change=lambda e: refresh_drawer(drawer_content, e.value, load_dataset, load_Dbit_model)
        ) as tabs:
        ui.tab('Datasets', icon='dataset')
        ui.tab('Models', icon='memory')
        ui.tab('Fine-tuning', icon='tune')

    with ui.tab_panels(tabs, value='Datasets').classes('w-full'):

        # =====================================================================
        # DATASETS
        # =====================================================================

        with ui.tab_panel('Datasets'):

            ui.label('Training Images').classes(
                'text-xl font-bold'
            )

            train_table = ui.table(
                columns=[
                    {'name': 'name', 'label': 'Image', 'field': 'name', 'align': 'left'},
                    {'name': 'label', 'label': 'Label', 'field': 'label', 'align': 'left'},
                    {'name': 'size', 'label': 'Size', 'field': 'size', 'align': 'left'},
                    {'name': 'view', 'label': 'View', 'field': 'view', 'align': 'left'}
                ],
                rows=[],
                row_key='name',
                pagination={'rowsPerPage': 0}, 
            ).classes('max-h-[600px] w-full')

            # scrolling parameters
            train_table.props('virtual-scroll style="max-height: 600px; width: w-full; margin-right: auto;"')

            train_table.add_slot('body', r'''
                <q-tr :props="props" class="cursor-pointer">

                    <q-td key="name" :props="props" class="text-left">
                        {{ props.row.name }}
                    </q-td>

                    <q-td key="label" :props="props" class="text-left">
                        {{ props.row.label }}
                    </q-td>

                    <q-td key="size" :props="props" class="text-left">
                        {{ props.row.size }}
                    </q-td>

                    <q-td key="view" class="text-left" @click.stop>
                        <q-btn
                            size="sm"
                            color="secondary"
                            icon="visibility"
                            round
                            dense
                            @click="() => $parent.$parent.$emit('view_mri', 
                                {
                                'table': 'train',
                                'file' : props.row.name
                                }
                                )"
                        />
                    </q-td>

                </q-tr>
            ''')

            ui.separator()

            ui.label('Testing Images').classes(
                'text-xl font-bold'
            )

            test_table = ui.table(
                columns=[
                    {'name': 'name', 'label': 'Image', 'field': 'name', 'align': 'left'},
                    {'name': 'label', 'label': 'Label', 'field': 'label', 'align': 'left'},
                    {'name': 'size', 'label': 'Size', 'field': 'size', 'align': 'left'},
                    {'name': 'view', 'label': 'View', 'field': 'view', 'align': 'left'}
                ],
                rows=[],
                row_key='name',
                pagination={'rowsPerPage': 0}, 
            ).classes('max-h-[600px] w-full')

            # scrolling parameters
            test_table.props('virtual-scroll style="max-height: 600px; width: w-full; margin-right: auto;"')

            test_table.add_slot('body', r'''
                <q-tr :props="props" class="cursor-pointer">

                    <q-td key="name" :props="props" class="text-left">
                        {{ props.row.name }}
                    </q-td>

                    <q-td key="label" :props="props" class="text-left">
                        {{ props.row.label }}
                    </q-td>

                    <q-td key="size" :props="props" class="text-left">
                        {{ props.row.size }}
                    </q-td>

                    <q-td key="view" class="text-left" @click.stop>
                        <q-btn
                            size="sm"
                            color="secondary"
                            icon="visibility"
                            round
                            dense
                            @click="() => $parent.$parent.$emit('view_mri', 
                                {
                                'table': 'test',
                                'file' : props.row.name
                                }
                                )"
                        />
                    </q-td>

                </q-tr>
            ''')

            ui.markdown(r"""
                **Dataset requirements**

                - Scans and labels must be in **NIfTI** format (`.nii` or `.nii.gz`).
                - All images must be registered to the **MNI 1 mm standard space**.
                - The dataset must have the following structure:

                ```
                dataset_name/
                ├── imagesTr/
                │   ├── image1.nii.gz
                │   ├── image2.nii.gz
                │   └── ...
                ├── labelsTr/
                │   ├── label1.nii.gz
                │   ├── label2.nii.gz
                │   └── ...
                ├── imagesTs/
                │   ├── image1.nii.gz
                │   ├── image2.nii.gz
                │   └── ...
                └── labelsTs/
                    ├── label1.nii.gz
                    ├── label2.nii.gz
                    └── ...
                ```
            """).classes('text-black-7')

        train_table.on('view_mri', handle_view_mri)
        test_table.on('view_mri', handle_view_mri)
                    
      
        # =====================================================================
        # MODELS
        # =====================================================================

        with ui.tab_panel('Models'):

            model_container = ui.column().classes('w-full')

            @ui.refreshable
            def show_model():

                model_container.clear()

                with model_container:
                    if current_model['value'] is None:
                        ui.label('Select a model from the drawer')
                        return

                    model = current_model['value']
                    meta = model['meta']['model']

                    with ui.card().classes('w-80'):
                        ui.label(model['name']).classes('text-xl font-bold')

                        ui.separator()

                        ui.label(f'Input size: {" × ".join(map(str, meta["img_size"]))}')
                        ui.label(f'Input channels: {meta["num_input"]}')
                        ui.label(f'Base filters: {meta["n_can_in"]}')

                        ui.button('Load', icon='play_arrow')

            show_model()


        # =====================================================================
        # FINE-TUNING
        # =====================================================================

        with ui.tab_panel('Fine-tuning'):

            async def start_finetuning():

                if current_dataset['name'] is None:
                    ui.notify('Please select a dataset', type='warning')
                    return

                if current_model['value'] is None:
                    ui.notify('Please select a model', type='warning')
                    return
                
                if validate_model_name(model_name.value):
                    ui.notify(validate_model_name(model_name.value), type='warning')
                    return

                config = {
                    'name': model_name.value,
                    'dataset': current_dataset['name'],
                    'model': current_model['value'],
                    'epochs': epochs.value,
                    'batch_size': batch_size.value,
                    'learning_rate': lr.value,
                    'optimizer': optimizer.value,
                    'augmentation': Augmentation.value,
                }

                #ui.notify(config)
                await finetune_model(config)

            with ui.row().classes('q-mt-md gap-4').style('width: 100%; flex-wrap: nowrap;'):
                with ui.card().classes('w-full max-w-xl'):

                    ui.label('Training Parameters').classes(
                        'text-xl font-bold'
                    )
                    
                    model_name = ui.input(
                            label='Model Name',
                            placeholder='Enter a name for the fine-tuned model',
                            validation=validate_model_name
                        ).classes('w-full')

                    dataset_select = ui.select(
                        options=list_datasets(),
                        label='Dataset',
                        value=current_dataset['name'],
                        on_change=lambda e: load_dataset(e.value)
                    ).classes('w-full')

                    model_select = ui.select(
                        options=[m['name'] for m in list_models()],
                        label='Model',
                        value=current_model['value']['name'] if current_model['value'] else None,
                        on_change=lambda e: load_Dbit_model(e.value)
                    ).classes('w-full')

                    ui.separator()

                    epochs = ui.number(
                        'Epochs',
                        value=50,
                    )

                    batch_size = ui.number(
                        'Batch Size',
                        value=2,
                    )

                    lr = ui.number(
                        'Learning Rate',
                        value=0.0001,
                        format='%.5f',
                    )

                    optimizer = ui.select(
                        ['Adam', 'AdamW', 'SGD'],
                        label='Optimizer',
                        value='Adam',
                    )

                    Augmentation = ui.checkbox('Use data augmentation')

                    ui.button(
                        'Start Fine-tuning',
                        icon='play_arrow',
                        color='green',
                        on_click=start_finetuning
                    )

                with ui.card().classes("w-full"):


                    ui.html(
                        """
                        <iframe
                            src="/tensorboard/"
                            style="
                                width:100%;
                                height:calc(100vh - 150px);
                                border:none;">
                        </iframe>
                        """,
                        sanitize=False
                    ).classes("w-full")
                
    if current_dataset['name']:
        load_dataset(current_dataset['name'])

    if current_model['value']:
        load_Dbit_model(current_model['value']['name'])

def refresh_drawer(drawer_content, current_tab, load_dataset, load_Dbit_model):

    drawer_content.clear()

    with drawer_content:

        selected_dataset = {'name': None}
        selected_model = {'name': None}

        async def upload_finished(e):
            await handle_dataset_upload(
                    e,
                    selected_dataset['name']
                )

            refresh_drawer(drawer_content, current_tab, load_dataset, load_Dbit_model)
            load_dataset(selected_dataset['name'])
            #load_Dbit_models(selected_model['name'])

        upload = ui.upload(
            on_upload=upload_finished,
            multiple=False,
            auto_upload=True,
        ).props('accept=".zip"').classes('hidden')


        def dataset_name():

            with ui.dialog() as dialog, ui.card():

                ui.label(
                    'Insert Dataset name'
                ).classes('text-h6')

                d_name = ui.input(
                    value='ciao',
                    placeholder='Dataset ID'
                ).classes('w-60')

                async def confirm_dataset_name():

                    if d_name.value in list_datasets():
                        ui.notify(
                            'Dataset ID already exists',
                            type='negative'
                        )
                        return

                    selected_dataset['name'] = d_name.value

                    dialog.close()

                    await asyncio.sleep(0.1)

                    await upload.run_method('pickFiles')

                with ui.row():

                    ui.button(
                        'Confirm',
                        on_click=confirm_dataset_name
                    )

                    ui.button(
                        'Cancel',
                        on_click=dialog.close
                    )

            dialog.open()

        # =============================
        # DATASETS
        # =============================
        if current_tab == 'Datasets':

            ui.label('Datasets').classes(
                'text-xl font-bold'
            )

            ui.separator()

            ui.button(
                '+ Import Dataset',
                icon='upload_file',
                on_click=dataset_name
            ).classes('w-full justify-start')

            for ds in list_datasets():
                ui.button(
                    ds,
                    icon='folder',
                    on_click=lambda d=ds: load_dataset(d)
                ).props('flat align=left').classes(
                        'w-full justify-start text-left')

        # =============================
        # MODELS
        # =============================
        elif current_tab == 'Models':

            ui.label('Models').classes(
                'text-xl font-bold'
            )

            ui.separator()

            for model in list_models():
                ui.button(
                    model['name'],
                    icon='memory',
                    on_click=lambda m=model: load_Dbit_model(m['name'])
                ).props('flat align=left').classes(
                        'w-full justify-start text-left')

        # =============================
        # FINE-TUNING
        # =============================
        else:

            ui.label('Fine-tuning').classes(
                'text-xl font-bold'
            )

            ui.separator()
