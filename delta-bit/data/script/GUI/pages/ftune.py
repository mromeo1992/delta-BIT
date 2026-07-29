from nicegui import ui
from script.GUI.services.datasets import list_datasets, handle_dataset_upload
from script.GUI.services.models import list_models


def finetune():

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

        refresh_drawer(drawer_content, 'Datasets')


    # ---------- TABS ---------------------------------------------------------

    with ui.tabs(
        on_change=lambda e: refresh_drawer(drawer_content, e.value)
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

            ui.table(
                columns=[
                    {'name': 'name', 'label': 'Image', 'field': 'name'},
                    {'name': 'label', 'label': 'Label', 'field': 'label'},
                    {'name': 'size', 'label': 'Size', 'field': 'size'},
                ],
                rows=[],
                pagination=10,
            ).classes('w-full')

            ui.separator()

            ui.label('Testing Images').classes(
                'text-xl font-bold'
            )

            ui.table(
                columns=[
                    {'name': 'name', 'label': 'Image', 'field': 'name'},
                    {'name': 'size', 'label': 'Size', 'field': 'size'},
                ],
                rows=[],
                pagination=10,
            ).classes('w-full')

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

def refresh_drawer(drawer_content, current_tab):

    drawer_content.clear()

    with drawer_content:

        if current_tab == 'Datasets':

            ui.label('Datasets').classes(
                'text-xl font-bold'
            )

            ui.separator()

            upload = ui.upload(
                on_upload=handle_dataset_upload,
                multiple=False,
                auto_upload=True,                
            ).props('accept=.zip').classes('hidden')

            ui.button(
                '+ Import Dataset',
                icon='upload_file',
                on_click=lambda: upload.run_method('pickFiles')
            ).classes('w-full justify-start')


            for ds in list_datasets():
                ui.button(
                    ds,
                    icon='folder',
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