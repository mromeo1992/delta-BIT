from nicegui import ui
import asyncio

from script.GUI.services.datasets import list_datasets
from script.GUI.services.datasets import handle_dataset_upload
from script.GUI.services.datasets import get_dataset_images
from script.GUI.services.datasets import build_rows
#from script.GUI.services.datasets import handle_view_mri

from script.GUI.services.models import list_models
from script.GUI import utility

def finetune():

    train_table = None
    test_table = None

    current_dataset = {'name': None}

    def load_dataset(dataset_name):
        current_dataset['name'] = dataset_name

        train, test = get_dataset_images(dataset_name)

        ui.notify(f"{dataset_name}")
        ui.notify(f"{len(train)}, {len(test)}")

        train_table.rows = build_rows(train)
        train_table.update()

        test_table.rows = build_rows(test)
        test_table.update()

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
                on_click=lambda: ui.navigate.to('/')
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

        refresh_drawer(drawer_content, 'Datasets', load_dataset)


    # ---------- TABS ---------------------------------------------------------

    with ui.tabs(
        on_change=lambda e: refresh_drawer(drawer_content, e.value, load_dataset)
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



            train_table.on('view_mri', handle_view_mri)

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

        
        test_table.on('view_mri', handle_view_mri)         
        # =====================================================================
        # MODELS
        # =====================================================================

        with ui.tab_panel('Models'):

            with ui.row().classes(
                'w-full gap-4 items-start wrap'
            ):

                for model in list_models():

                    meta = model['meta']['model']

                    with ui.card().classes('w-80'):

                        ui.label(model['name']).classes(
                            'text-xl font-bold'
                        )

                        ui.separator()

                        ui.label(
                            f'Input size: {" × ".join(map(str, meta["img_size"]))}'
                        )

                        ui.label(
                            f'Input channels: {meta["num_input"]}'
                        )

                        ui.label(
                            f'Base filters: {meta["n_can_in"]}'
                        )

                        with ui.row():

                            ui.button(
                                'Load',
                                icon='play_arrow',
                            )


        # =====================================================================
        # FINE-TUNING
        # =====================================================================

        with ui.tab_panel('Fine-tuning'):

            with ui.card().classes('w-full max-w-xl'):

                ui.label('Training Parameters').classes(
                    'text-xl font-bold'
                )

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
                )

def refresh_drawer(drawer_content, current_tab, load_dataset):

    drawer_content.clear()

    with drawer_content:
        selected_dataset = {'name': None}

        async def upload_finished(e):
            await handle_dataset_upload(
                    e,
                    selected_dataset['name']
                )

            refresh_drawer(drawer_content, current_tab, load_dataset)
            load_dataset(selected_dataset['name'])

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

        elif current_tab == 'Models':

            ui.label('Models').classes(
                'text-xl font-bold'
            )

            ui.separator()

            for model in list_models():
                ui.button(
                    model['name'],
                    icon='memory',
                ).props('flat align=left').classes(
                        'w-full justify-start text-left')

        else:

            ui.label('Fine-tuning').classes(
                'text-xl font-bold'
            )

            ui.separator()

            ui.label('No options yet')